# Weibo Spider

使用Scrapy-Redis框架进行爬取


##  爬取逻辑


:::image type="content" source="info_data/未命名文件 (1).png" alt-text="爬虫逻辑":::

## 字段说明

所有字段分成四个表格,分别可以通过不同关键字做关联查询：
- User
- Fan_Follow
- Tweet
- Comment

### User

| keyword | explaination |
| --- | --- |
| _id | 微博用户的唯一id |
| crawl_time | 抓取时间 |
| nick_name(name) | 用户昵称 |
| gender(sex) | 性别 |
| province(area) | 省份/海外 |
| city | 所在城市 |
| brief_introduction(self_intro) | 自我介绍 |
| birthday | 生日 |
| vip_level | vip等级 |
| labels(tags) | 标签 |
| tweets_num(tweet_count) | 微博总数 |
| follows_num(follow_count) | 关注总数 |
| fans_num(fans_count) | 粉丝总数 |
| sentiment(relationship) | ???? |
| sex_orientation | 性取向 |
| authentication | 认证 |
| (person_url)homepage_url | 主页 |

------------------------------

### Fan_Follow

| keyword | explaination |
| --- | --- |
| _id | 唯一id，组合方式为"粉丝id-fan-被关注者id" |
| crawl_time | 抓取时间 |
| post_time | 粉丝id |
| content | 被关注者id |

------------------------------

### Tweet

| keyword | explaination |
| --- | --- |
| _id | 微博用户的唯一id |
| crawl_time | 抓取时间 |
| post_time | 发布时间 |
| content | 微博内容 |
| tweet_url | 微博地址 |
| user_id | 用户ID |
| source | 发送设备/话题 |
| repost_count | 转发数 |
| thumbup_count | 点赞数 |
| comement_count | 评论数 |
| pic_url | 图片地址 |
| video_url | 视频地址 |
| origin_tweet | 原微博地址 |

-------------------------------

### Comment

| keyword | explaination |
| --- | --- |
| _id | 评论的唯一id格式为 "C_" + "id" |
| crawl_time | 爬取时间 |
| post_time | 发布时间 |
| comment_user_id | 评论者id |
| comment | 评论内容 |
| thumb_up_count | 点赞数 |
| tweet_id | 评论的微博的id |

-------------------------------


## 数据
