# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import pymongo
from pymongo.errors import DuplicateKeyError
from weibospider_phi.settings import MONGO_HOST, MONGO_PORT
from weibospider_phi.items import *
from weibospider_phi.spiders.topic_spider import spider_topics


class WeibospiderPhiPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        db = self.client['weibo']
        self.Users = db["Users"]
        self.Tweets = db["Tweets"]
        self.Comments = db["Comments"]
        self.Relationships = db["Relationships"]
        # self.TopicTweets = db['TopicTweets']
        # self.TopicComments = db['TopicComments']


    def process_item(self, item, spider):
        if spider.name == 'weibo_all_info':
            if isinstance(item, TweetItem):
                self.insert_item(self.Tweets, item)
            if isinstance(item, CommentItem):
                self.insert_item(self.Comments, item)
            if isinstance(item, RelationshipItem):
                self.insert_item(self.Relationships, item)
            if isinstance(item, UserItem):
                self.insert_item(self.Users, item)
        if spider.name == 'topics':
            topic_db = self.client['weibo_topics']
            tweet_col = topic_db['Pandemic_Tweet']
            comment_col = topic_db['Pandemic_Comment']
            try:
                if isinstance(item, TopicTweetItem):
                    tweet_col.insert_one(dict(item))
                if isinstance(item, TopicCommentItem):
                    comment_col.insert_one(dict(item))
            except DuplicateKeyError:
                pass
        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            pass

# class WeiboTopicPipline:
#     def __init__(self):
#         client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
#         self.db = client['weibo_topics']
#         self.tweet_col = self.db['Pandemic_Tweet']
#         self.comment_col = ['Pandemic_Comment']
#
#     def process_item(self, item, spdier):
#         if isinstance(item, TopicTweetItem):
#             self.tweet_col.insert(dict(item))
#         if isinstance(item, TopicCommentItem):
#             self.comment_col.insert(dict(item))
