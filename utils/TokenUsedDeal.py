import os, sys, json, time, pyssdb, random, datetime, redis

import requests
from scrapy.utils.project import get_project_settings

from utils.LogUtil import LogUtil


class TokenUsedDeal(object):
    verify_hash = 'waiting_verify_token_list'
    token_category_used = 'token_category_used'
    token_detail_used = 'token_detail_used'
    token_mall_used = 'token_mall_used'
    token_ip_hash = 'token_ip_hash'
    quantity_token_hash = 'quantity_token_hash'

    def __init__(self):
        self.ssdb_client = pyssdb.Client(get_project_settings().get('SSDB_HOST'), 8888)
        self.today = datetime.date.today()
        # 创建连接池
        pool = redis.ConnectionPool(host=get_project_settings().get('PROXY_REDIS_HOST'), port=6379, db=10,
                                    password=get_project_settings().get('PROXY_REDIS_AUTH'), decode_responses=True)
        # 创建链接对象
        self.redis_client = redis.Redis(connection_pool=pool)
        self.logUtil = LogUtil()
        self.platform = "pdd"
        self.appSecret = "C3v2jTXJtFWDbRqL1VxPoEOA0NHnf9zQGuiB"
        self.get_token_url = 'http://172.16.0.27:88/api/v1/proxy/getToken'
        self.report_token_url = 'http://172.16.0.27:88/api/v1/proxy/tokenReport'

    def collection_verify_token(self, token):
        self.redis_client.sadd(self.verify_hash, token, token)

    def collection_used_token(self, use_type, token):
        if use_type == 'category':
            self.redis_client.sadd(self.token_category_used, token)
        if use_type == 'detail':
            self.redis_client.sadd(self.token_detail_used, token)
        if use_type == 'mall':
            self.redis_client.sadd(self.token_mall_used, token)

    def reuse_category_token(self, token):
        if token and not self.redis_client.hget('category_token_reuse_hash', token):
            self.redis_client.hset('category_token_reuse_hash', token, token)
            self.redis_client.lpush('verified_token_list', json.dumps({'access_token': token}))

    def clean_invalid_token(self, token):
        if self.redis_client.hget('spider_mall_token_hash', token):
            self.redis_client.hdel('spider_mall_token_hash', token)

    def get_detail_token(self):
        token_list = self.redis_client.hkeys(self.token_ip_hash)
        if token_list:
            token = random.choice(token_list)
            return token
        else:
            return ''

    def get_quantity_token(self):
        token_list = self.redis_client.hkeys(self.quantity_token_hash)
        if token_list:
            token = random.choice(token_list)
            return token
        else:
            return ''

    def get_spider_token(self, token_type, request_name):
        query = {
            'platform': self.platform,
            'appSecret': self.appSecret,
            'tokenType': token_type,
            'requestName': request_name,
            'isSpider': True
        }
        try:
            r = requests.get(self.get_token_url, params=query)
            r = r.json()
            if r['code'] == 200:
                return r['data']
            else:
                return ''
        # return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            self.get_spider_token(token_type, request_name)

    def token_report(self, access_token, token_type, report_type):
        query = {
            'platform': self.platform,
            'appSecret': self.appSecret,
            'tokenType': token_type,
            'accessToken': access_token,
            'reportType': report_type
        }
        log_data = {'accessToken': access_token,
                    'tokenType': token_type,
                    'reportType': report_type}
        try:
            r = requests.get(self.report_token_url, params=query)
            r = r.json()
            if r['code'] == 200:
                log_data['status'] = 'success'
            else:
                log_data['status'] = 'fail'
            self.logUtil.write_log('token_report_log', json.dumps(log_data))
        except Exception as e:
            print(e)
            time.sleep(2)
            self.token_report(access_token, token_type, report_type)
