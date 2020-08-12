# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import pymongo, random

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

class CookieMiddleware(object):
    """
    从mongodb中随机取一个微博cookie
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.account_db = client['weibo']['account']


    def process_request(self):
        # extract cookie code here
        total_cookies = self.account_db.count()
        rand_index = random.randint(0,total_cookies - 1)
        next_cookie_list = self.account_db.find({'cookie':1,'_id':0})
        request.headers.setdefault('Cookie', list(next_cookie_list)[rand_index])


class ProxyMiddleware(object):
    """
    两个选择
    从收费网站直接调用API
    从免费代理网站爬取后的MONGODB中取
    """
    def fetch_proxy(self):
        '''
        获取IP的方法写在这里
        :return:
        '''

    def process_request(self):
        proxy_data = self.fetch_proxy() # what type?
        if proxy_data:
            new_proxy = f'http://{proxy_data}'
            spider.meta['proxy'] = new_proxy




class RedirectMiddleware(object):
    """
    如果返回的状态码不对则换一个cookie
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.account_db = client['weibo']['account']


    def process_response(self, request, response, spider):
        connect_status = response.status
        if connect_status == 403 or connect_status == 302:
            self.account_db.find_one_and_update({'_id': request.meta['account']['_id']},
                                                        {'$set': {'status': 'error'}}, )

