# encoding=utf-8
import os
import time
from conf.EnvConf import EnvConf


class LogUtil(object):

	def __init__(self):
		pass

	@staticmethod
	def write_log(dir_name, log_data, name='', tag=''):
		env_conf = EnvConf()
		file_path = env_conf.get_log_path(dir_name)
		if not os.path.exists(file_path):
			os.makedirs(file_path)
		if not name:
			file_name = file_path + '/' + str(time.strftime('%Y-%m-%d')) + '.log'
		else:
			file_name = file_path + '/' + name + '.log'
		tag = "" if not tag else str(tag) + " "
		data = '[' + str(time.strftime('%Y-%m-%d %H:%M:%S')) + '] ' + tag + log_data
		with open(file_name, "a+") as f:
			f.write(data + "\r\n")
