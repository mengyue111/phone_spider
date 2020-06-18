# encoding=utf-8
import datetime
import time
import json
import requests
from conf.EnvConf import EnvConf
from utils.LogUtil import LogUtil


class ProxyCommon(object):

    proxy_fy_advanced_list = 'proxy_ip_list_fy_advanced'

    proxy_2808_advanced_list = 'proxy_ip_list_2808_advanced'

    proxy_zhilian_advanced_list = 'proxy_ip_list_zhilian_advanced'

    def __init__(self):
        self.platform = "pdd"
        self.appSecret = "C3v2jTXJtFWDbRqL1VxPoEOA0NHnf9zQGuiB"
        self.get_proxy_url = 'http://172.16.0.30:88/api/v1/proxy/getProxy'
        self.redis_client = EnvConf().get_proxy_redis_client()
        self.logUtil = LogUtil()

    def get_spider_proxy(self, proxy_type, request_name):
        query = {
            'platform': self.platform,
            'appSecret': self.appSecret,
            'proxyType': proxy_type,
            'requestName': request_name,
            'isSpider': True
        }
        try:
            r = requests.get(self.get_proxy_url, params=query)
            r = r.json()
            if r['code'] == 200:
                return 'https://' + r['data']
            else:
                return ''
        # return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            self.get_spider_proxy(proxy_type, request_name)

    def get_spider_proxy_only(self, proxy_type, request_name):
        query = {
            'platform': self.platform,
            'appSecret': self.appSecret,
            'proxyType': proxy_type,
            'requestName': request_name,
            'isSpider': True
        }
        try:
            r = requests.get(self.get_proxy_url, params=query)
            r = r.json()
            if r['code'] == 200:
                return r['data']
            else:
                return ''
        # return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            self.get_spider_proxy(proxy_type, request_name)

    def get_fy_advanced_proxy(self):
        today = datetime.date.today()
        proxy = self.redis_client.rpop(self.proxy_fy_advanced_list)
        if proxy:
            self.redis_client.hincrby("proxy_fy_count", str(today))
            return "http://" + str(proxy)
        else:
            # print('暂无可用代理 睡眠3s')
            time.sleep(3)
            return self.get_fy_advanced_proxy()

    def get_2808_advanced_proxy(self):
        proxy = self.redis_client.rpop(self.proxy_2808_advanced_list)
        if proxy:
            return "http://" + str(proxy)
        else:
            time.sleep(3)
            return self.get_2808_advanced_proxy()

    def get_fy_advanced_proxy_v2(self):
        proxy = self.redis_client.get('spider_sync_proxy')
        if not proxy:
            proxy = self.redis_client.rpop(self.proxy_fy_advanced_list)
            if proxy:
                proxy_str = "http://" + str(proxy)
                self.redis_client.setex('spider_sync_proxy', 40, proxy_str)
                return proxy_str
            else:
                time.sleep(3)
                return self.get_fy_advanced_proxy()
        else:
            return proxy

    def get_fy_proxy_local(self):
        # res = requests.get('http://129.204.8.31//api/v1/proxy/getProxy').json()
        res = requests.get('http://182.254.163.159:5050/api/v1/proxy/getProxy?proxy_type=proxy_fy&debug=100000&platform=pdd').json()
        return res['data']

    def get_bly_long_proxy_local(self):
        # res = requests.get('http://129.204.8.31//api/v1/proxy/getProxy').json()
        res = requests.get('http://111.230.55.188/api/v2/proxy/longLastingProxy?debug=200000').json()
        return res['data']

    def proxy_count(self):
        redis_key = 'proxy_stat_' + str(datetime.date.today())
        self.redis_client.hincrby(redis_key, 'proxy_count')

    def proxy_timeout(self):
        redis_key = 'proxy_stat_' + str(datetime.date.today())
        self.redis_client.hincrby(redis_key, 'proxy_time_out')

    # 直接请求多布云代理
    def get_dby(self):
        proxy_ip = ''
        res = requests.get('http://125.88.158.218:8082/open?api=byumcjkr').json()
        self.logUtil.write_log('proxy_dby_request', json.dumps(res))
        if res['code'] == 200:
            ip = res['domain']
            for port in res['port']:
                proxy_ip = ip + ':' + str(port)
        return proxy_ip

    # 释放多布云代理
    def flush_dby(self, proxy):
        proxyArray = proxy.split(':')
        if len(proxyArray) < 2:
            return
        port = proxyArray[1]
        res = requests.get('http://125.88.158.218:8082/close?api=byumcjkr&port='+str(port)).json()
        self.logUtil.write_log('proxy_dby_flush', json.dumps(res))

    # 直接请求飞蚁代理
    def get_fy(self, count=1):
        proxy_ip = ''
        res = requests.get('http://112.17.250.28:88/open?user_name=hys_92418531_9dd1&timestamp=1565854349852&md5=C58101FAFFE2A5D634852DC40D672D32&pattern=json&fmt=1&number=' + str(count)).json()
        self.logUtil.write_log('proxy_fy_request', json.dumps(res))
        if res['code'] == 100:
            ip = res['domain']
            for proxy in res['data']:
                proxy_ip = ip + ':' + str(proxy['port'])
        return proxy_ip
    
    def get_66(self):
        time.sleep(3)
        proxy_ip = ''
        res = requests.get('http://api.66daili.cn/API/GetSecretProxy/?orderid=1131209352001228027&num=1&token=66daili&format=json&line_separator=win&protocol=http&region=domestic').json()
        self.logUtil.write_log('proxy_66_request', json.dumps(res))
        if res['status']:
            for proxy in res['proxies']:
                proxy_ip = proxy
        return proxy_ip
