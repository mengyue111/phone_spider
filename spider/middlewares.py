# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import math
import os

import scrapy
from scrapy import signals
import random, base64, sys, json, pyssdb, time, redis, datetime

from twisted.internet.endpoints import TCP4ClientEndpoint

import setting
from utils.ProxyCommon import ProxyCommon
from conf.EnvConf import EnvConf

PY3 = sys.version_info[0] >= 3


def base64ify(bytes_or_str):
    if PY3 and isinstance(bytes_or_str, str):
        input_bytes = bytes_or_str.encode('utf8')
    else:
        input_bytes = bytes_or_str

    output_bytes = base64.urlsafe_b64encode(input_bytes)
    if PY3:
        return output_bytes.decode('ascii')
    else:
        return output_bytes


class SpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    basic_token_redis_key = 'pdd_spider_token_basic'
    day_token_redis_key = ''
    currentToken = ''
    currentCount = ''

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(
            redis_host=crawler.settings.get('PROXY_REDIS_HOST'),
            redis_auth=crawler.settings.get('PROXY_REDIS_AUTH'),
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def __init__(self, redis_host, redis_auth):
        self.today = datetime.date.today()
        pool = redis.ConnectionPool(host=redis_host, port=6379, db=10, password=redis_auth, decode_responses=True)
        # 创建链接对象
        self.redis_client = redis.Redis(connection_pool=pool)

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        try:
            spider_type = spider.alias_name
        except Exception as e:
            spider_type = spider.name

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


'''生成header请求中间件'''
class BuildHeaderMiddleware(object):
    def process_request(self, request, spider):
        headers = self.make_headers()
        for key in headers.keys():
            request.headers[key] = headers[key]

    def make_headers(self):
        user_agent = self.get_user_agent()
        headers = {
            "Host": "yangkeduo.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://yangkeduo.com/goods.html?goods_id=442573047&from_subject_id=935&is_spike=0&refer_page_name=subject&refer_page_id=subject_1515726808272_1M143fWqjQ&refer_page_sn=10026",
            "Connection": "keep-alive",
            'User-Agent': user_agent,
        }
        ip = str(random.randint(100, 200)) + '.' + str(random.randint(1, 255)) + '.' + str(
            random.randint(1, 255)) + '.' + str(random.randint(1, 255))
        headers['CLIENT-IP'] = ip
        headers['X-FORWARDED-FOR'] = ip
        return headers

    def get_user_agent(self):
        chrome_version = str(random.randint(59, 63)) + '.0.' + str(random.randint(1000, 3200)) + '.94'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' + chrome_version + ' Safari/537.36'
        return user_agent


'''fy代理IP中间件 供前台使用'''
class ProxyMiddleware(object):
    proxyCommon = ProxyCommon()
    env = EnvConf().get_env()

    def spider_opened(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_request(self, request, spider):
        proxy = self.proxyCommon.get_fy_advanced_proxy() if self.env == 'prod' else 'http://' + self.proxyCommon.get_fy_proxy_local()
        # print(proxy)
        if request.url.split(':')[0] == 'https':
            request.meta['proxy'] = proxy.replace('http', 'https')
        else:
            request.meta['proxy'] = proxy
        # print(request.meta['proxy'])


class TestProxyMiddleware(object):
    def spider_opened(self, spider):
        pass
    
    def close_spider(self, spider):
        pass
    
    def process_request(self, request, spider):
        pass
        # request.meta['proxy'] = 'http://11938142158:ve0Luih1@119.38.142.158:3128'
