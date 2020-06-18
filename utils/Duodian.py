import json, time, random, urllib.request, urllib.parse,hashlib,hmac,os
import base64
from Crypto.Cipher import AES

class Duodian:
	laravel_cookie=''
	key = 'eNgWuwpQ84MZVTQbmdtHWTEwYXFibzDNXPSMP+B5VsA='

	def __init__(self):

		self.key = base64.b64decode(self.key)

	def get_front_access_token(self):
		self.login_duodian()
		i = 0
		while True:
			url = 'http://47.107.66.170/api/pddba/token'
			now = int(time.time())
			salt = str(random.randint(100000, 999999))
			token = salt + str(now) + salt
			SIGN = {'time':now, 'salt':salt, 'token':hashlib.md5(token.encode(encoding='UTF-8')).hexdigest()}
			data = {}
			data = urllib.parse.urlencode(data).encode('utf-8')
			headers = {'Accept':'application/vnd.ddgj.v2+json', 'SIGN':self.aes_encrypt(SIGN),'Cookie':self.laravel_cookie}
			print(SIGN, data, headers)
			new_url = urllib.request.Request(url=url, headers=headers)
			response = urllib.request.urlopen(new_url).read().decode('utf-8')
			# print(response)
			login_token = json.loads(response)
			if login_token:
				return login_token
			i += 1
			if i > 5:
				return ''

	def aes_encrypt(self,data): 
		key=self.key  #加密时使用的key，只能是长度16,24和32的字符串
		iv = os.urandom(16)
		string = json.dumps(data).encode('utf-8')
		padding = 16 - len(string) % 16
		string += bytes(chr(padding) * padding, 'utf-8')
		value = base64.b64encode(self.mcrypt_encrypt(string, iv))
		iv = base64.b64encode(iv)
		mac = hmac.new(key, iv+value, hashlib.sha256).hexdigest()
		dic = {'iv': iv.decode(), 'value': value.decode(), 'mac': mac}
		return base64.b64encode(bytes(json.dumps(dic), 'utf-8'))

	def mcrypt_encrypt(self, value, iv):
		key=self.key
		AES.key_size = 128
		crypt_object = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
		return crypt_object.encrypt(value)

	def login_duodian(self):
		while True:
			url = 'http://47.107.66.170/api/user/loginV2'
			now = int(time.time())
			salt = str(random.randint(100000, 999999))
			token = salt + str(now) + salt
			SIGN = {'time':now, 'salt':salt, 'token':hashlib.md5(token.encode(encoding='UTF-8')).hexdigest()}
			data = {'username':'WTF','password':'jhc123456'}
			data = urllib.parse.urlencode(data).encode('utf-8')
			headers = {'Accept':'application/vnd.ddgj.v2+json', 'SIGN':self.aes_encrypt(SIGN)}
			new_url = urllib.request.Request(url, data, headers)
			response = urllib.request.urlopen(new_url)
			res_headers = response.getheaders()
			result_body = response.read().decode('utf-8')
			# print(res_headers, result_body)
			d = {}
			for k, v in res_headers:
				if "Set-Cookie" in k:
					d[k]=v
			self.laravel_cookie = d['Set-Cookie'].split(';')[0]
			if self.laravel_cookie:
				return ''
			i += 1
			if i > 5:
				return ''

	def get_front_access_token_list(self, url):
		""" 获取店铺id和pass_id"""
		headers = {"username": 'dianba.main', "password": "sVqk34j2U82nXnhYPDx8nwdUHW693Gdr",
				   'Accept': "application/vnd.ddgj.v2+json"}
		request_url = urllib.request.Request(url=url, headers=headers)
		response = json.loads(urllib.request.urlopen(request_url).read().decode("utf-8"))
		return response
