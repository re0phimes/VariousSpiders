# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import pymongo
from pymongo.errors import DuplicateKeyError
from weibo_topic.settings import MONGO_HOST, MONGO_PORT
from weibo_topic.items import *


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
        if spider.name == 'topics':
            topic_db = self.client['weibo_topics']
            tweet_col = topic_db['Topic_Tweet']
            comment_col = topic_db['Topic_Comment']
            try:
                if isinstance(item, TopicTweetItem):
                    tweet_col.insert_one(dict(item))
                if isinstance(item, TopicCommentItem):
                    comment_col.insert_one(dict(item))
            except DuplicateKeyError:
                pass
        return item

    # @staticmethod
    # def insert_item(collection, item):
    #     try:
    #         collection.insert(dict(item))
    #     except DuplicateKeyError:
    #         pass

