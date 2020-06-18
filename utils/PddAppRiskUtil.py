# encoding=utf-8
import random
import string
import requests
import json
import time
import re
import hashlib
import urllib.parse
from conf.EnvConf import EnvConf
from utils.CommonUtil import CommonUtil


class PddAppRiskUtil(object):
	ANTI_TYPE_CLOUD = 1  # 云采集生成anti-token(后期)
	ANTI_TYPE_APP = 2    # 手机端直接生成anti-token(前期)

	current_device_id = 1000

	devices_increment_list_key = 'pdd_devices_increment_list'
	devices_anti_token_list_key = 'pdd_device_anti_token_list'
	devices_only_etag_list_key = 'pdd_device_only_etag_list'
	devices_total_hash_key = 'pdd_devices_total_hash'

	ETAG_ALIVE_TIME = 3600
	
	ANTI_ALIVE_TIME = 600

	def __init__(self):
		env_conf = EnvConf()
		self.etag_redis_client = env_conf.get_etag_redis_client()
		self.ssdb_client = env_conf.get_ssdb_client()
		self.device_pika_client = env_conf.get_device_pika_client()
		self.ycrawl_url = env_conf.get_ycrawl_url()

	@staticmethod
	def generate_rand_str(length=10):
		return ''.join(random.sample(string.ascii_letters + string.digits, length)).lower()

	@staticmethod
	def x_b3():
		now = int(time.time())
		salt = str(random.randint(100000, 999999))
		token = salt + str(now) + salt
		return hashlib.md5(token.encode(encoding='UTF-8')).hexdigest()

	@staticmethod
	def get_etag(device_info,etag_data,proxy=''):
		proxies = {'http': proxy,'https': proxy}
		data = etag_data
		headers = {
			"Referer": "Android",
			"X-PDD-QUERIES": PddAppRiskUtil.pdd_get_xPDD_QUERIES(device_info),
			"ETag": "",
			"p-appname": "pinduoduo",
			"x-b3-ptracer": PddAppRiskUtil.x_b3(),
			"User-Agent": PddAppRiskUtil.pdd_get_user_agent(device_info),
			"PDD-CONFIG": "00102",
			"Content-Type": "application/json",
			# "Content-Length": 2881,
			"Host": "meta.yangkeduo.com",
			# "Connection": "Keep-Alive",
			# "Accept-Encoding": "gzip",
			# "Cookie": "api_uid=CiSW114JyTQrwgBSBZviAg==",
		}
		res = requests.post('http://meta.yangkeduo.com/project/meta_info?pdduid', data=json.dumps(data), headers=headers,
		                    proxies=proxies).json()
		return res['pdd_id']
	
	@staticmethod
	def get_api_uid_from_cookie(api_str):
		detail_data = re.findall(r'api_uid=(.+?);', api_str)
		return detail_data[0]

	@staticmethod
	def pdd_get_xPDD_QUERIES(device_info):
		# return "width=" + device_info['width'] + "&height=" + device_info['height'] + "&net=4&brand=" + device_info[
		# 	'brand'] + "&model=" + device_info['model'] + "&osv=" + device_info['release'] + "&appv=4.79.0&pl=2"
		return "width=" + device_info['width'] + "&height=" + device_info['height'] + "&net=4&brand=" + device_info[
			'brand'] + "&model=" + device_info['model'] + "&osv=" + device_info['release'] + "&appv=5.9.1&pl=2"

	@staticmethod
	def pdd_get_user_agent(device_info):
		# return "android Mozilla/5.0 (Linux; Android " + device_info['release'] + "; " + device_info[
		# 	'model'] + " Build/" + device_info[
		# 	       'buildId'] + "; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.109 Mobile Safari/537.36  phh_android_version/4.79.0 phh_android_build/8f1f3c5b5775973e09c20ba23b2c6a23aad33e5f phh_android_channel/qihu360 pversion/0"
		return "android Mozilla/5.0 (Linux; Android " + device_info['release'] + "; " + device_info[
			'model'] + " Build/" + device_info[
			       'buildId'] + "; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/69.0.3497.109 Mobile Safari/537.36  phh_android_version/5.9.1 phh_android_build/b9213e6babdc300b5d68497c8b02025835c239ce_pdd_patch phh_android_channel/qihu360 pversion/0"

	@staticmethod
	def get_anti_token(device_info):
		form_data = {
			"VersionIncremental": device_info['incremental'],
			"android_id": device_info['androidId'],
			"buildDisplay_id": device_info['displayId'],
			"buildPropFileTime": int(device_info['propTime']),
			"buildVersion": device_info['kernelVersion'],
			"date_utc": int(device_info['time']),
			"product_board": device_info['board'],
			"product_brand": device_info['brand'],
			"product_device": device_info['device'],
			"product_manufacturer": device_info['manufacturer'],
			"product_model": device_info['model'],
			"serialno": device_info['serialNo'],
		}
		res = requests.post('http://pdd-build.dianba6.com/api/v2/antiToken', data=json.dumps(form_data)).json()
		return res['data']

	'''从哈希表获取设备信息，后根据设备信息获取对应请求头数据'''
	def get_common_headers(self):
		current_anti_type = self.ANTI_TYPE_APP
		if current_anti_type == self.ANTI_TYPE_CLOUD:
			self.current_device_id += 1
			print(self.current_device_id)
			if self.current_device_id > 1200:
				return '测试范围已超过', {}
			data = self.device_pika_client.hget(self.devices_total_hash_key, self.current_device_id)
			device_info = json.loads(data.decode('utf-8'))
			return '', self.get_device_common_headers(device_info), self.current_device_id
		else:
			return self.get_anti_device_common_headers()

	@staticmethod
	def get_device_common_headers(device_info):
		headers = {
			'Referer': 'Android',
			'X-PDD-QUERIES': PddAppRiskUtil.pdd_get_xPDD_QUERIES(device_info),
			'ETag': device_info['etag'],
			'Content-Type': 'application/json;charset=UTF-8',
			'anti-token': PddAppRiskUtil.get_anti_token(device_info),
			'p-appname': 'pinduoduo',
			'x-b3-ptracer': PddAppRiskUtil.x_b3(),
			'User-Agent': PddAppRiskUtil.pdd_get_user_agent(device_info),
			'PDD-CONFIG': '00102',
			'Host': 'api.yangkeduo.com',
			'Connection': 'Keep-Alive',
			'Accept-Encoding': 'gzip',
			# 'AccessToken': 'BUHAN473ZWICCTQFDYWV4LEGHQ2SYWGTVDDY7WEVB3NDSMJBM5LA1136038',
		}
		return headers
	
	def get_only_etag_common_headers(self):
		errmsg = '目前的etag不足，请充值'
		anti_info = {}
		while self.etag_redis_client.llen(self.devices_only_etag_list_key) > 0:
			data = self.etag_redis_client.rpop(self.devices_only_etag_list_key)
			anti_info = json.loads(data.decode('utf-8'))
			if time.time() - anti_info['etag_update_time'] < self.ANTI_ALIVE_TIME:
				errmsg = ''
				break
		if errmsg != '':
			return errmsg, anti_info, ''
		if 'device_id' not in anti_info.keys():
			errmsg = '当前信息流[ ' + json.dumps(anti_info) + ' ]不存在device_id，请提醒设备组检测格式'
			return errmsg, {}, ''
		data = self.device_pika_client.hget(self.devices_total_hash_key, anti_info['device_id'])
		if not data:
			errmsg = '当前设备信息ID为[ ' + anti_info['device_id'] + ' ]不存在，请提醒设备组检测存入hash表'
			return errmsg, {}, ''
		# device_info = json.loads(data.decode('utf-8')) #ssdb 读出格式
		device_info = json.loads(data)  # redis读出格式
		return '', {
			'Referer': 'Android',
			'X-PDD-QUERIES': self.pdd_get_xPDD_QUERIES(device_info),
			'ETag': device_info['etag'],
			'Content-Type': 'application/json;charset=UTF-8',
			'p-appname': 'pinduoduo',
			'x-b3-ptracer': self.x_b3(),
			'User-Agent': self.pdd_get_user_agent(device_info),
			'PDD-CONFIG': '00102',
			'Host': 'api.yangkeduo.com',
			'Connection': 'Keep-Alive',
			'Accept-Encoding': 'gzip',
			# 'AccessToken': 'BUHAN473ZWICCTQFDYWV4LEGHQ2SYWGTVDDY7WEVB3NDSMJBM5LA1136038',
		}, anti_info['device_id']

	def get_anti_device_common_headers(self):
		errmsg = '目前的anti-token不足，请充值'
		anti_info = {}
		while self.etag_redis_client.llen(self.devices_anti_token_list_key) > 0:
			data = self.etag_redis_client.rpop(self.devices_anti_token_list_key)
			anti_info = json.loads(data.decode('utf-8'))
			now = int(time.time())
			if now - anti_info['current_time'] / 1000 < self.ANTI_ALIVE_TIME and now - anti_info['etag_update_time'] < PddAppRiskUtil.ETAG_ALIVE_TIME:
				errmsg = ''
				break
		if errmsg != '':
			return errmsg, anti_info, ''
		if 'device_id' not in anti_info.keys():
			errmsg = '当前信息流[ ' + json.dumps(anti_info) + ' ]不存在device_id，请提醒设备组检测格式'
			return errmsg, {}, ''
		data = self.device_pika_client.hget(self.devices_total_hash_key, anti_info['device_id'])
		if not data:
			errmsg = '当前设备信息ID为[ ' + anti_info['device_id'] + ' ]不存在，请提醒设备组检测存入hash表'
			return errmsg, {}, ''
		# device_info = json.loads(data.decode('utf-8')) #ssdb 读出格式
		device_info = json.loads(data)  # redis读出格式
		return '', {
			'Referer': 'Android',
			'X-PDD-QUERIES': self.pdd_get_xPDD_QUERIES(device_info),
			'ETag': device_info['etag'],
			'Content-Type': 'application/json;charset=UTF-8',
			'anti-token': anti_info['antitoken'],
			'p-appname': 'pinduoduo',
			'x-b3-ptracer': self.x_b3(),
			'User-Agent': self.pdd_get_user_agent(device_info),
			'PDD-CONFIG': '00102',
			'Host': 'api.yangkeduo.com',
			'Connection': 'Keep-Alive',
			'Accept-Encoding': 'gzip',
			# 'AccessToken': 'BUHAN473ZWICCTQFDYWV4LEGHQ2SYWGTVDDY7WEVB3NDSMJBM5LA1136038',
		}, anti_info['device_id']

	@staticmethod
	def get_etag_params(device_info, etag_body):
		# url = 'http://meta.yangkeduo.com/project/meta_info?pdduid='
		url = 'https://meta.pinduoduo.com/project/meta_info?pdduid='
		request_body = etag_body
		return url, {
			'Referer': 'Android',
			'X-PDD-QUERIES': PddAppRiskUtil.pdd_get_xPDD_QUERIES(device_info),
			'ETag': '',
			'Content-Type': 'application/json;charset=UTF-8',
			'p-appname': 'pinduoduo',
			'x-b3-ptracer': PddAppRiskUtil.x_b3(),
			'User-Agent': PddAppRiskUtil.pdd_get_user_agent(device_info),
			'PDD-CONFIG': '00102',
			# 'Host': 'meta.yangkeduo.com',
			'Host': 'meta.pinduoduo.com',
			'Connection': 'Keep-Alive',
			'Accept-Encoding': 'gzip',
			# 'Cookie': ''
		}, request_body

	def get_keyword_goods_params_bak(self, keyword, page, flip):
		parameters = {
			"ycr": False,
			"q": keyword,
			"page": page,
			"flip": flip
		}
		res = requests.get(self.ycrawl_url + '/api/keywordGoods', params=parameters).json()
		if res['code'] != 0:
			return '', '', res['msg'], {}
		url = res['data']['url']
		if res['data']['method'] == 'GET' and len(res['data']['parameters']) > 0:
			url += '?' + CommonUtil.make_query_by_dict(res['data']['parameters'])
		return 'xxx', url, '', res['data']['headers']

	def get_keyword_goods_params(self, keyword, page, flip):
		url = 'https://api.yangkeduo.com/search' \
		      '?back_search=false' \
		      '&source=index' \
		      '&size=20' \
		      '&q={keyword}' \
		      '&search_met=manual' \
		      '&sort=default' \
		      '&requery=0' \
		      '&page={page}'
		url = url.format(keyword=urllib.parse.quote(keyword),page=page)
		if flip.strip():
			url += '&flip=' + urllib.parse.quote(flip)
		errmsg, headers, device_id = self.get_common_headers()
		return device_id, url, errmsg, headers

	def get_goods_detail_params(self, goods_id):
		url = 'https://api.pinduoduo.com/api/oak/integration/render'
		body = {
			# "address_list": [],
			"goods_id": goods_id,
			"page_from": "35",
			"page_version": "7",
			"client_time": int(time.time() * 1000),
			# "_oak_rank_id": "69340010201",
		}
		errmsg, headers, device_id = self.get_only_etag_common_headers()
		return device_id, url, errmsg, headers, body

	def get_img_goods_params(self, img_url):
		url = 'http://api.pinduoduo.com/api/search/img?pdduid='
		errmsg, headers, device_id = self.get_common_headers()
		body = {
			"url": img_url,
			"sort": "default",
		}
		return device_id, url, errmsg, headers, body

	def get_mall_info_params(self, mall_id):
		url = 'http://api.yangkeduo.com/mall/' + str(mall_id) + '/info?query_mall_favorite_coupon=true'
		errmsg, headers, detail_id = self.get_common_headers()
		params_dict = {'url': url, 'headers': headers}
		return errmsg, params_dict

