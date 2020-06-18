import time
import urllib.parse
import urllib.request
import random
import string
import requests
from conf.EnvConf import EnvConf


class PddRiskUtil(object):
    anti_content_url = 'http://172.16.0.27:8888'
    pdd_risk_url = 'http://172.16.0.27:3333'
    pdd_nano_url = 'http://172.16.0.27:3030'

    def __init__(self):
        env_conf = EnvConf()
        self.pdd_risk_v3 = 'http://172.16.0.27:3030' if env_conf.get_env() == 'prod' else 'http://172.16.11.99:3030'

    @staticmethod
    def generate_rand_str(length=10):
        return ''.join(random.sample(string.ascii_letters + string.digits, length))

    @staticmethod
    def get_anti_content(referer, page_num=1):
        query = {
            'href': referer,
            'page': page_num
        }
        try:
            r = requests.get(PddRiskUtil.anti_content_url, params=query)
            return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            return PddRiskUtil.get_anti_content(referer, page_num)

    def get_risk_old(self, referer, page_num=1):
        query = {
            'href': referer,
            'page': page_num
        }
        try:
            r = requests.get(self.pdd_risk_url + '/anti', params=query)
            return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            return self.get_risk_old(referer, page_num)

    def get_pdd_sign_login(self, referer, request_type):
        query = {
            'href': referer,
            'request_type': request_type
        }
        try:
            r = requests.get(self.pdd_risk_url + '/antiV2Login', params=query)
            return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            return self.get_pdd_sign_login(referer, request_type)

    @staticmethod
    def get_mall_anti_content(referer, page_num=1):
        query = {
            'href': referer,
            'page': page_num
        }
        try:
            r = requests.get(PddRiskUtil.pdd_nano_url + '/antiV2Mall', params=query)
            return r.content
        except Exception as e:
            print(e)
            time.sleep(2)
            return PddRiskUtil.get_mall_anti_content(referer, page_num)

    def get_anti_content_bak(self, referer):
        query = {
            'href': referer
        }
        data = urllib.parse.urlencode(query).encode('utf-8')
        try:
            request = urllib.request.Request(self.anti_content_url, data)
            anti_content_data = urllib.request.urlopen(request)
            anti_content = str(anti_content_data.read().decode('utf-8'))
            return anti_content
        except Exception as e:
            print(e)
            time.sleep(2)
            return self.get_anti_content(referer)

    @staticmethod
    def get_nano_fp():
        try:
            r = requests.get(PddRiskUtil.pdd_nano_url + '/antiV2Nano')
            return r.text
        except Exception as e:
            print(e)
            time.sleep(2)
            return PddRiskUtil.get_nano_fp()

    @staticmethod
    def get_anti_risk(referer, page=1, nano_fp=None, ua=None):
        query = {
            'href': referer,
            'page': page,
            'ua': ua,
            'nano_fp': nano_fp
        }
        try:
            r = requests.get(PddRiskUtil.pdd_nano_url + '/antiV2RiskControl', params=query)
            return r.text
        except Exception as e:
            print(e)
            time.sleep(2)
            return PddRiskUtil.get_anti_risk(referer, page, ua, nano_fp)
    
    def get_v3_nano_fp(self):
        try:
            r = requests.get(self.pdd_risk_v3 + '/antiV2Nano')
            return r.text
        except Exception as e:
            print(e)
            time.sleep(2)
            return self.get_v3_nano_fp()
    
    def get_v3_risk_control(self, referer, page=1, nano_fp=None, ua=None):
        query = {
            'href': referer,
            'page': page,
            'ua': ua,
            'nano_fp': nano_fp
        }
        try:
            r = requests.get(self.pdd_risk_v3 + '/antiV2RiskControl', params=query)
            return r.text
        except Exception as e:
            print(e)
            time.sleep(2)
            return self.get_v3_risk_control(referer, page, ua, nano_fp)

    def get_mms_order_params(self, start_time, end_time, page, size, pass_id):
        nano_fp = self.get_v3_nano_fp()
        refer = 'https://mms.pinduoduo.com/orders/list'
        anti_content = self.get_v3_risk_control(refer, 1, nano_fp)
        data = {
            'crawlerInfo': anti_content,
            'groupStartTime': start_time,
            'groupEndTime': end_time,
            'orderType': 0,
            'pageNumber': page,
            'pageSize': size,
            'afterSaleType': 0,
            'remarkStatus': -1,
            'source': 'MMS'
        }
        headers = {
            'Cookie': "PASS_ID=" + pass_id + ";_nano_fp=" + nano_fp,
            'Content-Type': 'application/json',
            'Referer': refer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'anti-content': anti_content
        }
        return 'https://mms.pinduoduo.com/mars/shop/recentOrderList', headers, data
