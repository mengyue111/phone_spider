# -*- coding: utf-8 -*-
import json
import logging
import random
import time

import scrapy
import requests
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import TimeoutError, TCPTimedOutError, ConnectionRefusedError
from twisted.web._newclient import ResponseFailed, ResponseNeverReceived
from scrapy.utils.response import response_status_message  # 获取错误代码信息


class PddActivityTypeSpider(scrapy.Spider):
    name = 'douban_spider'

    proxy_ips = []
    timestamp = 0

    custom_settings = {
        'LOG_FILE': '',
        'LOG_LEVEL': 'DEBUG',
        'LOG_ENABLED': True,
        'CONCURRENT_REQUESTS': 30,
        'SCHEDULER_FLUSH_ON_START': True,
        'DOWNLOAD_DELAY': 0.01
    }

    def start_requests(self):
        while True:
            url = 'http://qh.450330.com/api/home/get/phone/?token=f89494f293cc2911263851d0a24cec6b'
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            }
            meta = {'proxy': "http://" + self.get_proxy()}
            # meta = {}
            yield scrapy.Request(url, callback=self.parse, meta=meta, headers=headers, dont_filter=True)

    def parse(self, response):
        """ 获取首页活动信息"""
        data = json.loads(response.text)
        logging.debug(data)
        if data['state']:
            logging.debug(data)

    def errback_httpbin(self, failure):
        request = failure.request
        if failure.check(HttpError):
            response = failure.value.response
            errmsg = 'errback <%s> %s , response status:%s' % (
                request.url, failure.value, response_status_message(response.status))
        elif failure.check(ResponseFailed):
            errmsg = 'errback <%s> ResponseFailed' % request.url

        elif failure.check(ConnectionRefusedError):
            errmsg = 'errback <%s> ConnectionRefusedError' % request.url

        elif failure.check(ResponseNeverReceived):
            errmsg = 'errback <%s> ResponseNeverReceived' % request.url

        elif failure.check(TCPTimedOutError, TimeoutError):
            errmsg = 'errback <%s> TimeoutError' % request.url
        else:
            errmsg = 'errback <%s> OtherError' % request.url
        logging.debug(errmsg)

    def get_proxy_ips(self):
        url = 'http://tunnel-api.apeyun.com/q?id=2120061700049842237&secret=3bfmbgV5odqPGAxV&limit=5&format=json&auth_mode=auto'
        res = requests.get(url).json()
        logging.warning("成功获取代理===============================================================================================================")
        if res['code'] == 200:
            self.timestamp = int(time.time())
            for data in res['data']:
                ip = data['ip']
                port = data['port']
                proxy_ip = ip + ':' + str(port)
                self.proxy_ips.append(proxy_ip)

    def get_proxy(self):
        if int(time.time()) - self.timestamp > 20:
            self.proxy_ips = []
            self.get_proxy_ips()
        proxy = random.choice(self.proxy_ips)
        return proxy
