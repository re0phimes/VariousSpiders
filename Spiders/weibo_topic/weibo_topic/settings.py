# Scrapy settings for weibo_topic project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'weibo_topic'

SPIDER_MODULES = ['weibo_topic.spiders']
NEWSPIDER_MODULE = 'weibo_topic.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'weibo_topic (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# https://docs.scrapy.org/en/latest/topics/settings.html#concurrent-requests
CONCURRENT_REQUESTS = 16



# https://docs.scrapy.org/en/latest/topics/settings.html#std:setting-DOWNLOAD_DELAY
DOWNLOAD_DELAY = 1

# https://docs.scrapy.org/en/latest/topics/settings.html#download-timeout
DOWNLOAD_TIMEOUT = 5

# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#retry-times
RETRY_TIMES = 20

# Schduler
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# Dupefilter
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# DUPEFILTER_CLASS = "weibo_topic.dupefilters.WeiboTopicDupeFilter"

# redis config
REDIS_HOST = '180.76.153.244'
REDIS_PORT = 6789
REDIS_DB = 1
REDIS_PARAMS = {
            'password': 'arknights',
        }


# Redis URL
# REDIS_URL = 'redis://:{}@{}:{}'.format(REDIS_PASSWORD, REDIS_HOST, REDIS_PORT)
# urlformat = redis://name:password@ip:port/dbnum 如果没有name则直接为空

# Number of Hash Functions to use, defaults to 6
# BLOOMFILTER_HASH_NUMBER = 6

# Redis Memory Bit of Bloomfilter Usage, 30 means 2^30 = 128MB, defaults to 30
# BLOOMFILTER_BIT = 31

ITEM_PIPELINES = {
   # 'scrapy_redis.pipelines.RedisPipeline': 300,
    'weibo_topic.pipelines.WeibospiderPhiPipeline':300,
    #'crawlab.pipelines.CrawlabMongoPipeline': 888,
}

# Requests的调度策略
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
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
    # 'Cookie': '_T_WM=c7b81e04f496ae8f4bfc5a8dee238fb6; SSOLoginState=1595987507; SUHB=0h1JuhW2i28SRM; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W56vFoKR1IlXLiCyIaGhnV05JpX5KzhUgL.FoMXSK2feozpSo.2dJLoI0QLxK-L1hqLBoeLxK-LB--L1-2LxK-LB.qL1KnLxKnLB--LBo5LxKBLB.BLBK5LxKBLBonLBo9sUcyb; SUB=_2A25yJKZjDeRhGeFK7lMU8izNzTWIHXVR5sorrDV6PUJbktAKLVb5kW1NQ1svGBtDsN8CBrhiGHUO8xN-CqLgs28U'
    'Cookie': 'SINAGLOBAL=8660737555550.509.1596606706794; un=15714823923; UOR=,,login.sina.com.cn; SSOLoginState=1598339801; wvr=6; _s_tentry=login.sina.com.cn; Apache=2495566055560.976.1598339804813; ULV=1598339804824:5:5:1:2495566055560.976.1598339804813:1597626790222; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFJgAfDoOvlD__Q-Fdha9hl5JpX5KMhUgL.FoMXSK5Eehzf1h52dJLoIERLxK-LB--L1-zLxK-LBKqL1hzLxKMLB.2LBKzLxKnLBKzL1Kq_i--fiKnfiK.p; ALF=1629962508; SCF=Aga_cfik6RuvO19L8L1zoLw2Xkf8fQNwuVM1_A1HJaKwdR3V7wUg7CblbU3b-Y78IhGHwe_9a13I_lp3aCFEh0o.; SUB=_2A25yQn3dDeRhGeFK7lIT8CzJwzyIHXVRNugVrDV8PUNbmtANLWzakW9NQ1vJtkUgb0K8MdWC7vW1SM8XbZoYJNeT; SUHB=06ZF4Ul0USnEKA; WBStorage=70753a84f86f85ff|undefined'

}
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'weibo_topic.middlewares.WeibospiderPhiSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'weibo_topic.middlewares.WeibospiderPhiDownloaderMiddleware': 543,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html



# mongo config
MONGO_HOST = '180.76.153.244'
MONGO_PORT = 27890
MONGO_USERNAME = 'beihai'
MONGO_PASSWORD = 'yaoduoxiang'
MONGO_URL = 'mongodb://{}:{}'.format(MONGO_HOST, MONGO_PORT)


# LOG_FILE  = "spider_logs.log"
# LOG_LEVEL = "ERROR"


MYEXT_ENABLED=True      # 开启扩展
IDLE_NUMBER=360           # 配置空闲持续时间单位为 360个 ，一个时间单位为5s

# 在 EXTENSIONS 配置，激活扩展
EXTENSIONS = {
            'weibo_topic.extensions.RedisSpiderSmartIdleClosedExensions': 500,
        }
# MYEXT_ENABLED: 是否启用扩展，启用扩展为 True， 不启用为 False
# IDLE_NUMBER: 关闭爬虫的持续空闲次数，持续空闲次数超过IDLE_NUMBER，爬虫会被关闭。默认为 360 ，也就是30分钟，一分钟12个时间单位