# -*- coding: utf-8 -*-  
'''
增加淘宝等数据
'''


import requests
import pandas as pd
import pymongo
from pymongo.errors import DuplicateKeyError
import time
import logging
from logging import exception, handlers
from lxml import etree
# from crawlab import save_item
from settings import *
import traceback
# from apscheduler.schedulers.blocking import BlockingScheduler



########## set up logging config###################
# logger = logging.getLogger('hotrank_logger')
# logging.basicConfig(level = logging.INFO,
#                     # filename = 'hotrank_spider.log',
#                     # filemode = 'a',
#                     format=
#                     '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger = logging.getLogger('hotrank_logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 创建FileHandler对象
fh = logging.FileHandler('hotrank_exceptions.log')
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)


########### basic urls########################
# weibohot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
# baidu_url = 'http://top.baidu.com/buzz?b=1&fr=topnews'
# zhihu_url = 'https://www.zhihu.com/billboard'
weinxin_url = 'https://tophub.today/n/WnBe01o371'
tianmao_url = 'https://tophub.today/n/yjvQDpjobg'
douyin_url = 'https://tophub.today/n/DpQvNABoNE'



################# database settings ###########
mydb = pymongo.MongoClient(REMOTE_MONGO_HOST, REMOTE_MONGO_PORT)
mydb.admin.authenticate('beihai','4Speedforward!')
mycol = mydb['hot_rank']
# scheduler = BlockingScheduler(timezone="Asia/Shanghai")


############## spiders #########################


