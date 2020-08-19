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
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
# REDIS_DB = 1
# REDIS_PASSWORD = 123456
REDIS_PARAMS = {
    'password': 101519
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
    'weibo_topic.pipelines.WeibospiderPhiPipeline':300
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
    'Cookie': 'SINAGLOBAL=8660737555550.509.1596606706794; un=15714823923; YF-V5-G0=f5a079faba115a1547149ae0d48383dc; login_sid_t=50a2558c81fd70a48ef6fb3f1e73a582; cross_origin_proto=SSL; Ugrow-G0=5c7144e56a57a456abed1d1511ad79e8; _s_tentry=passport.weibo.com; Apache=8107048149976.288.1597626790217; ULV=1597626790222:4:4:1:8107048149976.288.1597626790217:1597394205405; UOR=,,login.sina.com.cn; SSOLoginState=1597724078; wvr=6; wb_view_log_7450202580=1920*10801; webim_unReadCount=%7B%22time%22%3A1597810934977%2C%22dm_pub_total%22%3A2%2C%22chat_group_client%22%3A28%2C%22chat_group_notice%22%3A4%2C%22allcountNum%22%3A107%2C%22msgbox%22%3A0%7D; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFJgAfDoOvlD__Q-Fdha9hl5JpX5KMhUgL.FoMXSK5Eehzf1h52dJLoIERLxK-LB--L1-zLxK-LBKqL1hzLxKMLB.2LBKzLxKnLBKzL1Kq_i--fiKnfiK.p; ALF=1629347145; SCF=Aga_cfik6RuvO19L8L1zoLw2Xkf8fQNwuVM1_A1HJaKw0R7wcgiJ1kcdmpUGfTp2fWX1AOtdYkEcCPWFsz3X9ZY.; SUB=_2A25yONmbDeRhGeFK7lIT8CzJwzyIHXVRTExTrDV8PUNbmtANLWrskW9NQ1vJtgvBIwy-bFMGJUibupNYdAfnzj0W; SUHB=09P98w2Tui-5wh; YF-Page-G0=4358a4493c1ebf8ed493ef9c46f04cae|1597811147|1597811145'
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
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27000
MONGO_URL = 'mongodb://{}:{}'.format(MONGO_HOST,MONGO_PORT)


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