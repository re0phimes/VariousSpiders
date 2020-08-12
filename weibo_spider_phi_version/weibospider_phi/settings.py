# Scrapy settings for weibospider_phi project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'weibospider_phi'

SPIDER_MODULES = ['weibospider_phi.spiders']
NEWSPIDER_MODULE = 'weibospider_phi.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'weibospider_phi (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# https://docs.scrapy.org/en/latest/topics/settings.html#concurrent-requests
CONCURRENT_REQUESTS = 16



# https://docs.scrapy.org/en/latest/topics/settings.html#std:setting-DOWNLOAD_DELAY
DOWNLOAD_DELAY = 1

# https://docs.scrapy.org/en/latest/topics/settings.html#download-timeout
DOWNLOAD_TIMEOUT = 3

# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#retry-times
RETRY_TIMES = 20

# Schduler
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Dupefilter
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# redis config
REDIS_HOST = '159.226.192.228'
REDIS_PORT = 6789
REDIS_DB = 1
REDIS_PASSWORD = '123456'

# Redis URL
REDIS_URL = 'redis://{}:{}'.format(REDIS_HOST, REDIS_PORT)

# Number of Hash Functions to use, defaults to 6
# BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
# BLOOMFILTER_BIT = 31

ITEM_PIPELINES = {
   # 'scrapy_redis.pipelines.RedisPipeline': 300,
    'weibospider_phi.pipelines.WeibospiderPhiPipeline':300
}

# Requests的调度策略
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.LifoQueue'

# Persist
SCHEDULER_PERSIST = True

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': 'SUB=_2A25yD6KJDeRhGeFK6FAY8izNyTqIHXVR887BrDV6PUJbktANLRPskW1NQ2XhFDzlox7jkbKmQJJnp7x7nRh8x0vL; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Whbzul.YIzKvQYIRhmuWy665JpX5KzhUgL.FoMXe0z4eozpeoq2dJLoIEMLxKnL12zL12BLxKML1K.LB.BLxKML1-2L1hBLxK.LBKeL12HbINet; SUHB=08JLiksMY2jPep; _T_WM=9103835666'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'weibospider_phi.middlewares.WeibospiderPhiSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'weibospider_phi.middlewares.WeibospiderPhiDownloaderMiddleware': 543,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html



# mongo config
MONGO_HOST = '159.226.192.228'
MONGO_PORT = 27000
MONGO_URL = 'mongodb://{}:{}'.format(MONGO_HOST,MONGO_PORT)


# LOG_FILE  = "spider_logs.log"
# LOG_LEVEL = "ERROR"