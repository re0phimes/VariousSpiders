# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TweetItem(scrapy.Item):
    weibo_url = scrapy.Field() # 微博地址
    post_time = scrapy.Field()  # 发布时间
    thumbup_count = scrapy.Field()  # 点赞数
    repost_count = scrapy.Field()  # 转发数
    comment_count = scrapy.Field()  # 评论数
    content = scrapy.Field()  # 微博内容
    user_id = scrapy.Field()  # 发表该微博用户的id
    send_from = scrapy.Field()  # 发布微博的来源
    pic_url = scrapy.Field()  # 图片
    video_url = scrapy.Field()  # 视频
    origin_weibo = scrapy.Field()  # 原始微博，只有转发的微博才有这个字段
    location_map_info = scrapy.Field()  # 定位的经纬度信息
    crawl_time = scrapy.Field()  # 抓取时间戳
    _id = scrapy.Field() # 微博id
    pass


class CommentItem(scrapy.Item):
    weibo_id = scrapy.Field() # 标识评论的哪条微博
    comment_user_id = scrapy.Field() # 评论者的id
    comment_user_url = scrapy.Field() # 评论者的主页地址
    comment_user_name = scrapy.Field() # 评论者昵称
    content = scrapy.Field() # 评论内容
    thumb_up_count = scrapy.Field() # 评论点赞内容
    post_time = scrapy.Field() #评论发布时间
    crawl_time = scrapy.Field() #评论抓取时间
    _id = scrapy.Field() #评论id
    pass


class RelationshipItem(scrapy.Item):
    """ 用户关系，只保留与关注的关系 """
    _id = scrapy.Field() #关注关系id
    fan_id = scrapy.Field()  # 关注者,即粉丝的id
    followed_id = scrapy.Field()  # 被关注者的id
    crawl_time = scrapy.Field()  # 抓取时间戳
    pass

class UserItem(scrapy.Item):
    """ User Information"""
    _id = scrapy.Field()  # 用户ID
    crawl_time = scrapy.Field()  # 抓取时间戳
    name = scrapy.Field()  # 昵称
    sex = scrapy.Field()  # 性别
    area = scrapy.Field()  # 所在省
    city = scrapy.Field()  # 所在城市
    self_intro = scrapy.Field()  # 简介
    birthday = scrapy.Field()  # 生日
    vip_level = scrapy.Field()  # 会员等级
    tags = scrapy.Field()  # 标签
    tweets_count = scrapy.Field()  # 微博数
    follows_count = scrapy.Field()  # 关注数
    fans_count = scrapy.Field()  # 粉丝数
    relationship = scrapy.Field()  # 感情状况
    sex_orientation = scrapy.Field()  # 性取向
    authentication = scrapy.Field()  # 认证
    # homepage = scrapy.Field()  # 首页链接

class TopicTweetItem(scrapy.Item):
    _id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    send_time = scrapy.Field()
    send_device = scrapy.Field()
    repost_count = scrapy.Field()
    comment_count = scrapy.Field()
    thumb_up_count = scrapy.Field()
    crawl_time = scrapy.Field()

class TopicCommentItem(scrapy.Item):
    _id = scrapy.Field()
    tweet_id = scrapy.Field()
    user_id = scrapy.Field()
    origin_comment_id = scrapy.Field()
    user_name = scrapy.Field()
    content = scrapy.Field()
    send_time = scrapy.Field()
    crawl_time = scrapy.Field()
    thumb_up = scrapy.Field()
    # more_comments_url = scrapy.Field()