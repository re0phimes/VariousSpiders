# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TopicTweetItem(scrapy.Item):
    _id = scrapy.Field()
    send_time = scrapy.Field()
    crawl_time = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    topic = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    send_device = scrapy.Field()
    repost_count = scrapy.Field()
    comment_count = scrapy.Field()
    thumb_up_count = scrapy.Field()


class TopicCommentItem(scrapy.Item):
    _id = scrapy.Field()
    send_time = scrapy.Field()
    crawl_time = scrapy.Field()
    tweet_id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    content = scrapy.Field()
    thumb_up = scrapy.Field()
    origin_comment_id = scrapy.Field()
    # more_comments_url = scrapy.Field()