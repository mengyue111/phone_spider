# Scrapy settings for example project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
SPIDER_MODULES = ['spider.spiders']
NEWSPIDER_MODULE = 'spider.spiders'

USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'

# 指定使用scrapy-redis的调度器
# SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 指定使用scrapy-redis的去重
# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# 在redis中保持scrapy-redis用到的各个队列，从而允许暂停和暂停后恢复，也就是不清理redis queues
SCHEDULER_PERSIST = True
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 60
CONCURRENT_ITEMS = 100
CONCURRENT_REQUESTS_PER_DOMAIN = 60

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#   'spider.middlewares.SpiderDownloaderMiddleware': 543,
# }
DOWNLOADER_STATS = False
DOWNLOAD_TIMEOUT = 20
RETRY_COUNT = 0
RETRY_ENABLED = False

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

ITEM_PIPELINES = {
    'spider.pipelines.SpiderPipeline': 300,
    # 'scrapy_redis.pipelines.RedisPipeline': 400,
}

# 默认情况下,RFPDupeFilter只记录第一个重复请求。将DUPEFILTER_DEBUG设置为True会记录所有重复的请求。
DUPEFILTER_DEBUG = True

LOG_FILE = '/data/pdd-spider/log.log'
LOG_LEVEL = 'WARNING'
LOG_ENABLED = False

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 0

REDIRECT_ENABLED = False

# TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

REDIRECT_MAX_TIMES = 3

# SPIDER_REDIS_27 = {
#     'host': '192.168.1.198',
#     'port': '6379',
#     'password': '',
#     'db': 2
# }
#
# SPIDER_REDIS_30 = {
#     'host': '172.16.0.30',
#     'port': '6379',
#     'password': '20A3NBVJnWZtNzxumYOz',
#     'db': 3
# }

# Pika = {
#     'host': '172.16.0.71',
#     'port': '9221',
#     'password': '20A3NBVJnWZtNzxumYOz',
#     'db': 0,
#     'decode_responses': True,
# }
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PARAMS = {
    'password': '',
    'db': 3
}

SSDB_HOST = '172.16.0.5'

SPIDER2_SSDB_HOST = '172.16.0.8'
