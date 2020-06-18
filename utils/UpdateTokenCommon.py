# encoding=utf-8
import datetime
import random
import sys, time, json, os, pyssdb

import redis
from scrapy.utils.project import get_project_settings

from utils.ProxyCommon import ProxyCommon


class UpdateTokenCommon(object):
    def __init__(self, token_type, token_hash_source, token_set_cd, token_set, min_cd=80, max_cd=160, num=1,
                 sleep_time=10, new_token_set_cd="", new_token_set=""):
        """
        :param token_type:
        :param token_hash_source:
        :param token_set_cd:
        :param num:
        :param sleep_time:
        :param min_cd:
        :param max_cd:
        """
        self.token_type = token_type
        self.token_hash_source = token_hash_source
        self.token_set_cd = token_set_cd
        self.num = num
        self.sleep_time = sleep_time
        self.min_cd = min_cd
        self.max_cd = max_cd
        self.token_set = token_set
        self.today = datetime.date.today()
        self.new_token_set_cd = new_token_set_cd
        self.new_token_set = new_token_set
        self.proxyCommon = ProxyCommon()
        self.redis_client = redis.Redis(host='172.16.0.27', port='6379', db=10, password='20A3NBVJnWZtNzxumYOz')

    def init_valid_token(self):
        result = self.redis_client.hvals(self.token_hash_source)
        for i in result:
            token_detail = json.loads(i.decode('utf-8'))
            access_token = token_detail['access_token']
            if 'last_used_time' not in token_detail.keys():
                token_detail['last_used_time'] = int(time.time()) - 300
            if 'day_count' not in token_detail.keys():
                token_detail['day_count'] = 0
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            today = datetime.date.today()
            # 随机分配  给新老有序集合使用
            # 判断是否有标记, 1 为新 0为老 ,无标记随机分
            # if self.new_token_set_cd and self.new_token_set:
            # 	if 'flag' not in token_detail.keys():
            # 		if random.randint(0, 10) < 7:
            # 			token_detail['flag'] = 1
            # 			self.token_set_cd = self.new_token_set_cd
            # 		else:
            # 			token_detail['flag'] = 0
            # 	if token_detail['flag'] == 1:
            # 		self.new_token_set = self.new_token_set_cd
            # 每天23点30初始化day_count
            if start_time > (str(today) + ' 23:30:00'):
                print(access_token, '====>初始化day_count')
                token_detail['day_count'] = 0
            # if token_detail['day_count'] > 200 and token_detail['platform'] in [0, 11]:
            # 	print(access_token, '====>今日使用次数达到200次,不在使用')
            # 	self.redis_client.zrem(self.token_set_cd, access_token)
            # 	continue
            self.redis_client.hset(self.token_hash_source, access_token, json.dumps(token_detail))
            self.redis_client.zadd(self.token_set_cd, access_token, int(time.time()))

    def get_valid_token_v2(self):
        cd_time = random.randint(self.min_cd, self.max_cd)
        token_list = self.redis_client.zrangebyscore(self.token_set_cd, 0, int(time.time()) - cd_time)
        for i in token_list:
            if type(i) == bytes:
                i = str(i, 'utf-8')
            self.redis_client.sadd(self.token_set, i)

    def update_used_time(self, access_token, proxy=""):
        token_detail = self.redis_client.hget(self.token_hash_source, access_token)
        if token_detail:
            token_detail = json.loads(token_detail.decode('utf-8'))
            token_detail['day_count'] += 1
            token_detail['count'] += 1
            if proxy:
                token_detail['proxy'] = proxy
            self.redis_client.hset(self.token_hash_source, access_token, json.dumps(token_detail))
        self.redis_client.zadd(self.token_set_cd, {access_token: int(time.time())})

    def clean_invalid_token(self, access_token):
        if type(access_token) == bytes:
            access_token = str(access_token, 'utf-8')
        token_detail = self.redis_client.hget(self.token_hash_source, access_token)
        if token_detail:
            self.redis_client.hdel(self.token_hash_source, access_token)
            self.redis_client.zrem(self.token_set_cd, access_token)
            self.redis_client.hset(self.token_hash_source + ':' + str(self.today), access_token, token_detail)

    def deal_token_expired(self, access_token):
        self.clean_invalid_token(access_token)
        self.redis_client.sadd('token_expired:' + str(self.today), access_token)

    def token_response_error(self, access_token):
        if type(access_token) == bytes:
            access_token = str(access_token, 'utf-8')
        token_detail = self.redis_client.hget(self.token_hash_source, access_token)
        if token_detail:
            token_detail = json.loads(token_detail.decode('utf-8'))
            if token_detail['error_count'] >= 10:
                self.clean_invalid_token(access_token)
                return None
            token_detail['error_count'] += 1
            token_detail['last_used_time'] = int(time.time())
            self.redis_client.hset(self.token_hash_source, access_token, json.dumps(token_detail))

    def get_access_token(self):
        token_list = self.redis_client.spop(self.token_set, 1)
        if token_list:
            access_token = random.choice(token_list)
            self.update_used_time(access_token)
            return access_token
        else:
            return ''

    def init_valid_token_v2(self):
        result = self.redis_client.hvals(self.token_hash_source)
        for i in result:
            token_detail = json.loads(i.decode('utf-8'))
            access_token = token_detail['access_token']
            if 'last_used_time' not in token_detail.keys():
                token_detail['last_used_time'] = int(time.time()) - 300
            if 'day_count' not in token_detail.keys():
                token_detail['day_count'] = 0
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            today = datetime.date.today()
            if start_time > (str(today) + ' 23:30:00'):
                print(access_token, '====>初始化day_count')
                token_detail['day_count'] = 0
            if 'proxy' not in token_detail.keys():
                token_detail['proxy'] = ""
            proxy = token_detail['proxy']
            self.redis_client.hset(self.token_hash_source, access_token, json.dumps(token_detail))
            self.redis_client.zadd(self.token_set_cd, json.dumps({'proxy': proxy, 'access_token': access_token}),
                                   int(time.time()))

    def get_access_token_v2(self):
        token_list = self.redis_client.spop(self.token_set, 1)
        if token_list:
            token_detail = random.choice(token_list)
            if type(token_detail) == bytes:
                token_detail = json.loads(token_detail.decode('utf-8'))
            else:
                token_detail = json.loads(token_detail)
            if 'proxy' not in token_detail.keys() or not token_detail['proxy']:
                token_detail['proxy'] = self.proxyCommon.get_spider_proxy('proxy_2808', self.token_type)
            access_token = token_detail['access_token']
            self.update_used_time(access_token, token_detail['proxy'])
            return {"proxy": token_detail['proxy'], "access_token": access_token}
        else:
            return ''

    def clear_token_proxy(self, token_detail):
        access_token = token_detail['access_token']
        token_detail_source = self.redis_client.hget(self.token_hash_source, access_token)
        if token_detail_source:
            token_detail_source = json.loads(token_detail_source.decode('utf-8'))
            token_detail_source['proxy'] = ""
            self.redis_client.hset(self.token_hash_source, access_token, json.dumps(token_detail_source))
        self.redis_client.zrem(self.token_set_cd, json.dumps(token_detail))
