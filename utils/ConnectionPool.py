import os, sys, json, time, pyssdb, random, datetime, redis

# import pymysql
from scrapy.utils.project import get_project_settings


class ConnectionPool(object):

    def __init__(self):
        pass

    def conn_ssdb(self):
        ssdb = pyssdb.Client(get_project_settings().get('SSDB_HOST'), 8888)
        return ssdb

    def conn_redis(self):
        pool = redis.ConnectionPool(host=get_project_settings().get('PROXY_REDIS_HOST'), port=6379, db=10,
                                    password='20A3NBVJnWZtNzxumYOz', decode_responses=True)
        # 创建链接对象
        redis_client = redis.Redis(connection_pool=pool)
        return redis_client
