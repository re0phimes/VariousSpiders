# -*- coding: utf-8 -*-


from loguru import logger
import time
import random
from datetime import datetime
import pymongo
from pymongo.errors import DuplicateKeyError
from scrapy import Selector
from config import settings
from typing import Dict
import requests


############ other constants ################
# logger.debug(settings.user_agent_list)
user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 10.0) Gecko/20100101 Firefox/61.0",
                   "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                   "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                   "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
                   "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                   ]

headers = {
    "user-agent": random.choice(user_agent_list)
}

url = "https://top.baidu.com/board?tab=realtime"


################# database settings ###########
server_name = settings['server_name']
ip = settings[server_name].ip
mongo_settings = settings[server_name].dbs.mongo


my_client = pymongo.MongoClient(
    ip, mongo_settings.port, username=mongo_settings.usr, password=mongo_settings.pwd)
daily_db_name = settings['db_info']['mongo'].db_name
keyword_db_name = settings['db_info']['mongo'].db_name2
daily_db = my_client[daily_db_name]
keyword_db = my_client[keyword_db_name]


################ cralwer #####################
## 1. downloader ##

def downloader():
    """
    下载模块
    """
    resp = requests.get(url, headers=headers)
    resp.encoding = resp.apparent_encoding
    if resp.status_code == 200:
        return resp.text


def parser(html):
    """
    传入文本解析百度搜索的内容
    """
    selector = Selector(text=html)

    date = datetime.today().date().strftime("%Y-%m-%d")

    titles = selector.xpath(
        "//a[@class='title_dIF3B ']/div[@class='c-single-text-ellipsis']/text()").extract()
    titles = [title.strip() for title in titles]
    scores = selector.xpath(
        "//div[@class='trend_2RttY hide-icon']/div[@class='hot-index_1Bl1a']/text()").extract()
    # urls = selector.xpath("")
    data = []
    if len(titles) == len(scores):
        ranks = [i for i in range(0, len(scores))]

        for i, item in enumerate(titles):
            d = {}
            d['keyword'] = titles[i]
            d['rank'] = ranks[i]
            d['score'] = scores[i]
            d['time'] = date
            data.append(d)

    one_top = {}
    one_top['_id'] = date
    one_top['crawltime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    one_top['data'] = data
    one_top['rank_name'] = 'baidu'
    return one_top


def saver(one_top: Dict):
    baidu_col = daily_db['baidu']
    date = datetime.today().date().strftime("%Y-%m-%d")
    try:
        res = baidu_col.insert_one(one_top)

        logger.info(f'SAVE 【{date}-baidu】data succ')
    except Exception as e:
        if type(e) == DuplicateKeyError:
            logger.warning(f"already loged {date} data, update now")

            # 更新数据
            old_data = list(baidu_col.find({'_id': {'$eq': one_top['_id']}}, {}))[
                0]  # 因为是duplicate key了数据必然存在
            # logger.debug(old_data)
            old_news_list = old_data['data']
            new_news_list = one_top['data']
            for new_news in new_news_list:
                for old_news in old_news_list:
                    # 有tag则更新tag
                    if (new_news['keyword'] == old_news['keyword']) and (old_data.get('tag') is not None):
                        new_news['tag'] = old_data.get('tag')
                    if(new_news['keyword'] == old_news['keyword']) and (old_data.get('url') is not None):
                        new_news['url'] = old_news.get('url')
            res = baidu_col.update_one({'_id': one_top['_id']}, {
                '$set': one_top})
            logger.info('update data succ')
        else:
            logger.error(e)


def saver_to_keywords(day_data: Dict):
    """
    将日热搜转为关键字为id的热搜并存入tops_keywords
    """
    # recorder
    recorder = [0, 0, 0] # 插入，更新，失败
    # validator
    for one_top in day_data['data']:
        try:
            one_top['keyword']
            one_top['rank']
            one_top['score']
            one_top['time']
            # logger.debug('valid data')
        except Exception as e:
            logger.error(f'data validate fail:【{one_top}】')
            # raise
        else:  # check data exists
            keyword_col = keyword_db['baidu']
            query = {'keyword': {'$eq': one_top['keyword']}}
            res = list(keyword_col.find(query))
            if len(res) == 0:  # keyword is new
                # 存入
                new_data = {}
                new_data['keyword'] = one_top['keyword']
                new_data['show_rank'] = [one_top['rank']]
                new_data['show_date'] = [one_top['time']]
                new_data['show_score'] = [one_top['score']]
                new_data['last_update_time'] = round(time.time()*1000)
                new_data['source'] = 'baidu'
                res = keyword_col.insert_one(new_data)
                if res:
                    recorder[0] += 1
                # logger.debug(f'insert_res: {res}')
            else:
                # 更新数据
                old_data = res[0]
                logger.debug(one_top)
                if one_top['time'] not in old_data['show_date']:  # 如果没有记录过（当日内），则直接添加
                    old_data['show_rank'].append(one_top['rank'])
                    old_data['show_date'].append(one_top['time'])
                    old_data['show_score'].append(one_top['score'])
                    old_data['last_update_time'] = round(time.time()*1000)
                    res = keyword_col.update_one(query, {'$set': old_data})

                    if res:
                        recorder[1] += 1
                    # logger.debug(f'update_result: {res}')
                else:  # 如果已经记录过，则更新
                    recorder[2] += 1
                    logger.warning(f"今日已经记录过, 更新分数和排行数据")
                    old_data['show_rank'].pop()
                    old_data['show_rank'].append(one_top['rank'])
                    old_data['show_score'].pop()
                    old_data['show_score'].append(one_top['score'])
                    old_data['last_update_time'] = round(time.time()*1000)
                    res = keyword_col.update_one(query, {'$set': old_data})
    logger.info(recorder)


def baidu_top_crawler():
    download_res = downloader()
    parse_res = parser(download_res)
    saver(parse_res)
    saver_to_keywords(parse_res)

if __name__ == "__main__":
    baidu_top_crawler()
