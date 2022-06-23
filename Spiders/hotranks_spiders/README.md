# hotranks_spiders

python spider that crawl following hot ranks:

- Baidu
- Zhihu
- Toutiao
- Weibo
- 

## 文件结构
 - hotranks_spiders.py : 通过tophub实现的几个主要平台热搜榜爬虫
 - news_crawler.py : 通过baidu搜索指定关键词的新闻链接和详细信息爬虫
 - run.py : 程序入口




## 待实现功能




### tops_daily
记录各排行版每日热搜
```
[
  {
    "_id": "2022-05-12 13:25:22",
    "data": [
      {
        "rank": 0,
        "keyword": "腾讯等企业被点名",
        "score": "57534人在看",
        "time": "2022-05-12 13:25:22"
      },
      {
        "rank": 1,
        "keyword": "北京封城静默系谣言",
        "score": "71741人在看",
        "time": "2022-05-12 13:25:22"
      },
    ],
    "rank_name": "360_realtime"
  }
]
```
#### 字段
- _id: 日期
- data: 实际数据。一个List[Dict]
    - rank: 热搜的当日排名
    - keyword: 热搜实际内容
    - score: 分数
    - time: 时间
    - tag: 标签，需要算法
- rank_name: 排行版名称

### tops_combine
以关键热搜关键字为主键，包含热搜出现的日期等信息
#### 字段
- _id: 随机生成
- keyword: 热搜内容
- show_date: List[datetime], 出现的日期
- show_rank: List[int], 出现日期的排行
- show_score: List[str], 出现日期的分数
- tag: 标签
- last_updatetime: timstamp, 最后更新时间。






## Docker 

```dockerfile
docker build -t hotrank_spiders .
```

### ceate volume if needed
```dockerfile
docker volume create hotrank_spiders
```


### run container
```dockerfile
docker run -d --name hotrank_spiders -v hotrank_spiders:/data hotrank_spiders
```

### docker-compose
```dockerfile
docker-compose up -d
```

## Python

~~~python
python ./spider/hotrank_spiders.py
~~~

