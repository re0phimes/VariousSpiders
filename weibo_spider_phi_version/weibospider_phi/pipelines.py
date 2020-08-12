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

class WeibospiderPhiPipeline:
    def __init__(self):
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        db = client['weibo']
        self.Users = db["Users"]
        self.Tweets = db["Tweets"]
        self.Comments = db["Comments"]
        self.Relationships = db["Relationships"]
        self.TopicTweets = db['TopicTweets']
        self.TopicComments = db['TopicComments']


    def process_item(self, item, spider):
        if isinstance(item, TweetItem):
            self.insert_item(self.Tweets, item)
        if isinstance(item, CommentItem):
            self.insert_item(self.Comments, item)
        if isinstance(item, RelationshipItem):
            self.insert_item(self.Relationships, item)
        if isinstance(item, UserItem):
            self.insert_item(self.Users, item)
        if isinstance(item, TopicTweetItem):
            self.insert_item(self.TopicTweets, item)
        if isinstance(item, TopicCommentItem):
            self.insert_item(self.TopicComments, item)

        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            pass