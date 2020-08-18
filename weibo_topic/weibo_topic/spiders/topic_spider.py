# encoding : UTF-8

from lxml import etree
import time
import json, re, logging
from scrapy.selector import Selector
from scrapy.http import Request
from weibo_topic.items import TopicTweetItem, TopicCommentItem
from scrapy_redis.spiders import RedisSpider
from weibo_topic.utils import time_fix, time_fix_comments
# from redis import StrictRedis

logger = logging.getLogger("TopicTweetSpider")

spider_topics = ['北京疫情','美国干净网络计划']

# redis传输url
# lpush topics:start_urls 'https://s.weibo.com/realtime?q=%23北京疫情%23&rd=realtime&tw=realtime&Refer=weibo_realtime&page=1'
# lpush topics:start_urls 'https://s.weibo.com/realtime?q=%23%E5%8C%97%E4%BA%AC%E7%96%AB%E6%83%85%23&rd=realtime&tw=realtime&Refer=weibo_realtime&page=1'
# lpush topics:start_urls 'https://s.weibo.com/hot?q=%23%E5%8C%97%E4%BA%AC%E7%96%AB%E6%83%85%23&xsort=hot&suball=1&tw=hotweibo&Refer=hot_hot'


# redis_client = StrictRedis(host='localhost', port=6789, db=1)


class TopicSpider(RedisSpider):
    name = 'topics'
    allow_domains = 'weibo.com'
    redis_key = 'topics:start_urls'
    def __init__(self):


        self.topic_realtime_url = 'https://s.weibo.com/realtime?q=%23{}%23&rd=realtime&tw=realtime&Refer=weibo_realtime&page={}'
        self.topic_hot_url = 'https://s.weibo.com/hot?q=%23{}%23&xsort=hot&suball=1&tw=hotweibo&Refer=realtime_hot&page={}'
        self.comment_base_url = "https://weibo.com/aj/v6/comment/big?ajwvr=6&id={}&from=singleWeiBo&page={}"
        self.search_list = ['疫情','北京疫情','美国净网行动']
        self.url_list = []


# make search_list
    def start_requests(self):

        for topic in self.search_list:
            # 实时链接
            realtime_url = self.topic_realtime_url.format(topic, 1)
            self.url_list.append(realtime_url)
            yield Request(realtime_url, callback=self.parse, meta={'topic': topic})
            # 热门链接
            hot_url = self.topic_hot_url.format(topic,1)
            self.url_list.append(hot_url)
            yield Request(hot_url, callback=self.parse, meta={'topic': topic})


# use custom_settings
#     custom_settings = {
#         # 指定 redis链接密码，和使用哪一个数据库
#         'REDIS_HOST': '127.0.0.1',
#         'REDIS_PORT': 6789,
#
#         'REDIS_PARAMS': {
#             'db': 1
#         },
#
#         # 'ITEM_PIPELINES': {
#         #     'weibospider_phi.pipelines.WeiboTopicPipeline'
#         # }
#     }






    def parse(self, response):
        '''
        爬取一个话题下的实时消息
        '''
        topic = response.meta['topic']
        print(response.url)
        if response.url[-6:] == 'page=1':
            print('This is first page! add other pages into requests queue')
            for i in range(2,50):
                next_url = self.topic_realtime_url.format('北京疫情',str(i))
                yield Request(next_url, callback=self.parse,meta={'topic':topic})
        # -----------------
        selector = Selector(response)
        card_node = selector.xpath('//div[@class="card"]')
        for tweet_block in card_node:
            tweet_item = TopicTweetItem()
            tweet_item['user_name'] = tweet_block.xpath('.//div[@class="content"]/div/div[2]/a/@nick-name')[0].extract()
            # tweet_item['url'] = tweet_block.xpath('.//div[@class="content"]/div/div[2]/a/@href')[0].extract()
            tweet_item['url'] = tweet_block.xpath('.//p[@class="from"]/a/@href')[0].extract().replace('//', '').split('?')[0]
            # --------------------------content--------------------------
            if tweet_block.xpath('./div/div/p[@node-type="feed_list_content_full"]/text()') == []:
                content_temp_list = tweet_block.xpath('.//p[@node-type="feed_list_content"]/text()').extract()
                tweet_item['content'] = ''.join(content_temp_list).replace(' ', '').replace('\n', '')
            else:
                content_temp_list = tweet_block.xpath('.//p[@node-type="feed_list_content_full"]/text()').extract()
                tweet_item['content'] = ''.join(content_temp_list).replace(' ', '').replace('\n', '')
            send_time_temp = tweet_block.xpath('//p[@class="from"]/a[1]/text()')[0].extract().replace(' ', '').replace('\n', '')
            tweet_item['send_time'] = time_fix(send_time_temp)
            tweet_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
            # --------------------------from-------------------------------
            if tweet_block.xpath('.//a[@rel="nofollow"]/text()').extract() != []:
                tweet_item['send_device'] = tweet_block.xpath('.//a[@rel="nofollow"]/text()')[0].extract()
            else:
                tweet_item['send_device'] = ""
            # -----------------status---------------------
            temp_repost = tweet_block.xpath('.//div[@class="card-act"]/ul/li/a/text()')[1].extract().split(' ')[2]
            if temp_repost == '':
                tweet_item['repost_count'] = 0
            else:
                tweet_item['repost_count'] = int(temp_repost)

            temp_comment = tweet_block.xpath('.//div[@class="card-act"]/ul/li/a/text()')[2].extract().split(' ')[1]
            if temp_comment == '':
                tweet_item['comment_count'] = 0
            else:
                tweet_item['comment_count'] = int(temp_comment)
            temp_thumbup = tweet_block.xpath('.//div[@class="card-act"]/ul/li/a/em/text()').extract()
            if temp_thumbup == []:
                tweet_item['thumb_up_count'] = 0
            else:
                tweet_item['thumb_up_count'] = int(temp_thumbup[0])
            tweet_item['_id'] = tweet_item['url'].split('/')[-1] # tweet_id
            try:
                tweet_item['user_id'] = tweet_item['url'].split('/')[1]
            except Exception as e:
                print(tweet_item['url'],e)
            tweet_item['topic'] = topic
            # ----------判断是否有评论----------------
            logger.info(tweet_item)
            if tweet_item['comment_count'] != '0':
                tweet_mid = tweet_block.xpath('../@mid').extract()[0]  #评论连接需要用的mid
                common_url = self.comment_base_url.format(tweet_mid, '1')
                yield Request(common_url, callback=self.parse_comments, meta={'tweet_id': tweet_item['_id']})
            yield tweet_item


    def parse_comments(self, response):
        '''
        单个微博的评论信息
        '''
        # 先判断评论多少，多的话需要翻几页
        # print(response.url)
        if re.findall('&page=1&', response.url):
            comm_count = json.loads(response.body)['data']['count']
            if int(comm_count) > 15:
                page_num = int(int(comm_count)/20)
                # print(page_num)
                for i in range(2,page_num+1):
                    print(type(i),i)
                    next_page_num = '&page={}&'.format(str(i))
                    next_url = response.url.replace('&page=1&', next_page_num)
                    print(next_url)
                    yield Request(next_url, callback=self.parse_comments, meta={'tweet_id': response.meta['tweet_id']})
        # 开始实际爬取评论信息
        comm_html = json.loads(response.body)['data']['html']
        comm_tree = etree.HTML(comm_html)
        content_node = comm_tree.xpath('//div[@comment_id]')
        for user_info_node in content_node:

            comment_data = {}
            comment_item = TopicCommentItem()
            # print(response.meta)
            comment_item['tweet_id'] = response.meta['tweet_id']
            temp_userid = user_info_node.xpath('.//a[@usercard]/@usercard')[0]
            comment_item['user_id'] = re.findall('[0-9]\d+', temp_userid)[0]
            comment_item['_id'] = user_info_node.xpath('./@comment_id')[0]
            comment_item['user_name'] = user_info_node.xpath('.//a[@usercard]/text()')[0]
            # coentent
            content_emojo = ''.join(user_info_node.xpath('.//div[@class="WB_text"]/img/@alt'))
            content_words = ''.join(user_info_node.xpath('.//div[@class="WB_text"]/text()')[1:]).replace('：',
                                                                                                         '').replace(
                " ", "")
            comment_item['content'] = content_emojo + content_words
            send_time_temp = user_info_node.xpath('.//div[@class="WB_from S_txt2"]/text()')[0]  # 需要优化时间格式
            comment_item['send_time'] = time_fix_comments(send_time_temp)
            comment_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
            # status
            temp_like = user_info_node.xpath('.//span[@node-type="like_status"]/em[last()]/text()')[0]
            if temp_like == "赞":
                comment_item['thumb_up'] = 0
            else:
                comment_item['thumb_up'] = temp_like
            if 'origin_comment' in response.meta.keys():
                comment_item['origin_comment_id'] = response.meta['origin_comment']
            else:
                comment_item['origin_comment_id'] = None
            ### 这里要注意逻辑处理，不要重复爬取
            more_comments_url_list = []
            if user_info_node.xpath('.//div[@class="list_li_v2"]/text()'):

                more_comments_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6' + \
                                    user_info_node.xpath('.//div[@class="list_li_v2"]//a[@action-data]/@action-data')[0] + \
                                    '&page=1&'
                more_comments_url_list.append(more_comments_url)
            if len(more_comments_url_list) > 0:
                yield Request(more_comments_url_list[0], callback=self.parse_comments, meta={'origin_comment': comment_item['_id'],'tweet_id':comment_item['tweet_id']})
            yield comment_item


