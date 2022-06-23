import requests
from scrapy import Selector
from loguru import logger
from pymongo import MongoClient
from typing import Dict
import threadpool
import time
import datetime
import re
from gne import GeneralNewsExtractor
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from config import settings
from tools.proxy_setings import proxy, headers
from tenacity import retry, retry_if_exception_type, wait_fixed, stop_after_attempt
from requests.exceptions import *
from fake_useragent import UserAgent



# ################ contents ##################
normal_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}


################# database settings ###########
server_name = settings['server_name']
ip = settings[server_name].ip
mongo_settings = settings[server_name].dbs.mongo


my_client = MongoClient(
    ip, mongo_settings.port, username=mongo_settings.usr, password=mongo_settings.pwd)
daily_db = my_client['tops_daily']
daily_cols = daily_db.list_collection_names()
keyword_db = my_client['tops_keywords']
keyowrd_cols = keyword_db.list_collection_names()


scheduler = BlockingScheduler(timezone="Asia/Shanghai")


url = "http://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&ie=utf-8&word={}&pn={}"
# headers = {
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53"
# }


########################################################
##                                       READ DATABASE                                                   
########################################################

# read_no_url from two dbs
def read_none_url_daily(col_name: str):
    query = {'data': {'$elemMatch': {'url': {'$exists': False}}}}
    none_url_data = list(daily_db[col_name].find(query))
    num = len(none_url_data)
    logger.info(f"got {num} keywords")
    return none_url_data


# read no detail from tops_keyword db
def read_none_detail_from_keyword(col_name: str, query_mode: int = 0):
    """
    从一个top_keyword表中找到content为空的内容。
    query_mode : 0：查询没有content的; 1:查询flag_url为0的（逻辑判断未查询过url）, 2：查询所有都走一遍
    """
    if query_mode == 0:
        query = {'relative_news': {'$exists': False}}
    if query_mode == 1:
        query = {'flag_detail': {'$exists': False}}
    if query_mode == 2:
        query = {}
    none_tag_data = list(keyword_db[col_name].find(query).sort('last_update_time',-1)) # 倒序，优先更新最新的
    return none_tag_data


def read_none_detail_today(col_name: str):
    """
    :param col_name: 数据库中的集合名
    """
    now= datetime.datetime.now()
    ts = round((datetime.datetime.now() - datetime.timedelta(hours=now.hour ,minutes=now.minute, seconds=now.second, microseconds=now.microsecond)).timestamp())
    # ts = round((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    query = {'$and':  [{'last_update_time': {'$gt': ts}}, {'relative_news': {'$exists': False}}]}
    none_tag_today = list(keyword_db[col_name].find(query))
    return none_tag_today


#############################################
##                                   UTILS                                            ##
#############################################

def generate_header():
    """
    生成随机header
    """
    ua = UserAgent()
    headers = {
        "user-agent": ua.random}
    return headers


def time_fix(time_string):
    now_time = datetime.datetime.now()
    if '分钟前' in time_string:
        minutes = re.search(r'^(\d+)分钟', time_string).group(1)
        created_at = now_time - datetime.timedelta(minutes=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '小时前' in time_string:
        minutes = re.search(r'^(\d+)小时', time_string).group(1)
        created_at = now_time - datetime.timedelta(hours=int(minutes))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if "天前" in time_string:
        days = re.search(r'^(\d+)天', time_string).group(1)
        created_at = now_time - datetime.timedelta(days=int(days))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '今天' in time_string:
        return time_string.replace('今天', now_time.strftime('%Y-%m-%d'))

    if "昨天" in time_string:
        created_at = now_time - datetime.timedelta(days=int(1))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if "前天" in time_string:
        created_at = now_time - datetime.timedelta(days=int(2))
        return created_at.strftime('%Y-%m-%d %H:%M')

    if '月' in time_string:
        time_string = time_string.replace('月', '-').replace('日', '')
        time_string = str(now_time.year) + '-' + time_string
        return time_string

    return time_string


def isChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

########################################################
##                                       END OF UTILS                                                   ##
########################################################


########################################################
#                                            CRAWLER
########################################################
def retry_return(retry_state):
    return []


# 基础抓取方法
@retry(wait=wait_fixed(3), stop=stop_after_attempt(10), retry_error_callback=retry_return)
def crawl_rela_news_title_one_pg(news_keywords: str = "北京疫情最新情况", pn: int = 0):
    """
    输入关键字爬取百度资讯中的新闻
    pn: 10的倍数
    根据关键字搜索百度并爬取解析
    """
    r = requests.get(url.format(news_keywords, pn),
                     headers=generate_header(), proxies=proxy)
    if r == None:
        logger.warning(f"空返回重试：{news_keywords}-第{pn}页-{crawl_rela_news_title_one_pg.retry.statistics['attempt_number']}")
        raise

    # 成功的情况
    if r.status_code == 200:
        # 检查是否定获取没有找到东西
        is_search_right = re.findall("抱歉，没有找到", r.text)
        if len(is_search_right) >= 1:
            logger.warning(f"无解析内容重试：{news_keywords}-第{pn}页-{crawl_rela_news_title_one_pg.retry.statistics['attempt_number']}")
            raise
        # 有查询到结果或触发风控
        else:
            # 有结果
            selector = Selector(text=r.text)
            data_list = []

            # 获取时间
            times = selector.xpath(
                "//span[@class='c-color-gray2 c-font-normal c-gap-right-xsmall']/text()").extract()
            # 转换时间，特殊时间：昨天XX、今天XX、前天XX、XX分钟前，XX小时前，XX天前
            times = [time_fix(post_time) for post_time in times]

            # 如果times不为空
            if len(times) > 1:
                titles = selector.xpath(
                    "//a[contains(@class,'news-title')]/@aria-label").extract()
                titles = [title[3:] for title in titles]
                urls = selector.xpath(
                    "//a[contains(@class,'news-title')]/@href").extract()
                sources = selector.xpath(
                    "//span[@class='c-color-gray']/text()").extract()
                # print(len(sources))
                for i, item in enumerate(times):
                    d = {}
                    d['time'] = times[i]
                    d['title'] = titles[i]
                    d['url'] = urls[i]
                    d['source'] = sources[i]
                    data_list.append(d)
                # logger.info(f"抓取成功：【{news_keywords}】, 第{pn}页  baidu 解析成功")
                return data_list

            # 异常获取或触发风控的情况
            else:
                logger.warning(f"风控重试：{news_keywords}-第{pn}页-{crawl_rela_news_title_one_pg.retry.statistics['attempt_number']}")
                raise
    else:
        raise


## daily_更新模式批量抓取业务 ##
def add_url(day_data: Dict):
    """
    获取百度中馊酸关键词后第一个数据信息
    """
    try:
        # logger.debug(day_data)
        # 如果url已经有内容则不重复查询
        if day_data.get('url'):
            logger.warning(
                f"skip keyword {day_data['keyword']}, already got its url")
            pass
        else:

            # 判断内容是否为中文（部分记录为乱码）
            if isChinese(day_data['keyword']):
                res = crawl_rela_news_title_one_pg(
                    day_data['keyword'], 1)  # 获取第一页数据
                logger.debug(
                    f'keyword <{day_data["keyword"]}> has url : <{res[0]["url"]}>')
                day_data['url'] = res[0]['url']

            # 如果不是则退出
            else:
                logger.error("KEYWORD NOT CHINESE")
    except Exception as e:
        logger.error(f'CRAWL KEYWORD FAIL: {day_data["keyword"]}, {e}')
        # if type(e) == IndexError:
        time.sleep(5)  # index错误则等5秒


def update_daily_news_url(col_name: str):
    """
    更新数据
    """
    query_data=read_none_url_daily(col_name)
    daily_col=daily_db[col_name]
    for item in query_data:  # 临时只看一个
        # 获取每一条数据，查询结果可能是多天的。
        consum_list=item['data']
        pool=threadpool.ThreadPool(5)
        tasks=threadpool.makeRequests(add_url, consum_list)
        [pool.putRequest(task) for task in tasks]
        pool.wait()
        print('-'*30 + 'crawled' + '-'*30)
        # 更新数据库
        filter={'_id': item['_id']}
        update_value={'$set': {'data': item['data']}}
        update_res=daily_col.update_one(filter, update_value)
        logger.debug(f"update result is {update_res}")
    # logger.debug(query_data[0]['data'])


def crawl_all_rela_news(keyword_top: Dict):
    """
    1、获取关键词相关新闻，1-5页，根据时间判断是否继续爬。
    2、挑选第一个链接抓取详情
    3、时间超过3个月则判断为不相关的信息。
    : param keyword_top: tops_daily中的一条数据，具体查看tops_daily库的格式。
    """
    # logger.debug(keyword_top)

    # validate: 读取的keyword内容为中文正常可以搜索
    keyword=keyword_top['keyword']
    if isChinese(keyword):
        pass
    else:
        logger.error(f"keyword {keyword} is not chinese")
        raise
    
    # 抓取10页，共计50个相关新闻报道
    relative_news_list=[]
    for i in range(0, 50, 10):
        one_page_urls=crawl_rela_news_title_one_pg(keyword, pn=i)
        if len(one_page_urls) > 1:
            relative_news_list += one_page_urls
        else:
            break
    logger.info(f"抓取完成：【{keyword}】多页信息搜索解析成功！")
    # 最匹配数据url
    try:
        detail_url=relative_news_list[0]['url']
    except Exception as e:
        logger.debug(f"CRAWL ERROR: relative news url is 0")

    # 去重
    relative_news_list=list(
        set([json.dumps(item) for item in relative_news_list]))
    relative_news_list=[json.loads(item) for item in relative_news_list]
    keyword_top['relative_news']=relative_news_list
    news_num=len(relative_news_list)
    # logger.debug(f"{keyword_top['keyword']} got {news_num}")

    # 获取第一个详情内容，详情页不用加代理，且直接用固定header即可
    if len(relative_news_list) > 0:
        raw_resp=requests.get(detail_url, headers=normal_headers)
        # raw_resp.encoding=raw_resp.apparent_encoding
        if raw_resp.status_code == 200:
            # logger.debug(r)
            extractor=GeneralNewsExtractor()
            details=extractor.extract(raw_resp.text)
            keyword_top['title']=details['title']
            keyword_top['pub_time']=details['publish_time']
            keyword_top['author']=details['author']
            keyword_top['content']=details['content']
            keyword_top['images']=details['images']
        else:
            logger.error(raw_resp.status_code)
            logger.debug('FAIL GET DETAIL PAGE')
            details={}
        # 更新入数据库内容
        update_values={'$set': {'relative_news': keyword_top['relative_news'],
                                  'title': details.get('title'),
                                  'pub_time': details.get('publish_time'),
                                  'author': details.get('author'),
                                  'content': details.get('content'),
                                  'images': details.get('images'),
                                  'flag_details': 1,
                                  'url': detail_url}
                         }
        update_res=keyword_db[keyword_top['source']].update_one(
            {'keyword': keyword_top['keyword']}, update_values)
        logger.info(
            f"写入数据库：【{keyword_top['keyword']}】写入数据库结果为： {update_res.modified_count}")
    else:
        logger.error(f'【{keyword}】 search in baidu failed')
        update_values={'$set': {
            'flag_details': 2,
        }}
        logger.error(f"UPDATE DB: {keyword} update flag has change to 2")
        update_res=keyword_db[keyword_top['source']].update_one(
            {'keyword': keyword_top['keyword']}, update_values)
        # 对数据库中标识进行更新。


def keyword_news_detail(keyword_top: Dict):
    """
    抓取详情
    """
    # request
    return None


def update_keywords_db(col_name: str, query_mode: int=0):
    """
    从数据库中读取关键词抓取、更新回mongodb中
    :param col_name: 数据库中的集合名
    : query_mode: 0-查询没有content的; 1-查询flag_url为0的（逻辑判断未查询过url）, 2-查询所有, 3-查询当天指定库中relative news 不存在的
    """
    logger.info(f"===========【query raw data from {col_name}】==========")
    if query_mode < 3:
        raw_query_data=read_none_detail_from_keyword(col_name, query_mode)
    if query_mode == 3:
        raw_query_data=read_none_detail_today(col_name)
    query_num = len(list(raw_query_data))
    logger.info(f'{col_name}库中有{query_num}个待查询数据')

    # 生成多线程list
    pool=threadpool.ThreadPool(3)
    tasks=threadpool.makeRequests(crawl_all_rela_news, raw_query_data)
    [pool.putRequest(task) for task in tasks]
    pool.wait()
    # logger.debug(raw_query_data[0])


def news_detail_crawler():
    col_name_list=keyword_db.list_collection_names()
    except_cols = ['天猫', '水木社区', '腾讯辟谣', '360', 'bilibili', '抖音']
    fetch_cols = list(set(col_name_list).difference(set(except_cols)))
    params_list = []
    for col_name in fetch_cols:
        param = ([col_name, 0], None)
        params_list.append(param)

    # 生成新闻详情抓取线程池
    thread_num = len(fetch_cols)
    pool=threadpool.ThreadPool(thread_num)
    logger.info(f'根据读取的col数量生成{thread_num}个线程')
    tasks=threadpool.makeRequests(update_keywords_db, params_list)
    [pool.putRequest(task) for task in tasks]
    pool.wait()





    

if __name__ == "__main__":
    news_detail_crawler()
    # res = read_none_detail_today(col_name='baidu')
    # logger.debug(res)
    # now= datetime.datetime.now()
    # a = datetime.datetime.now() - datetime.timedelta(hours=now.hour ,minutes=now.minute, seconds=now.second, microseconds=now.microsecond) 
    # logger.debug(round(a.timestamp()*1000))
    # logger.debug(a)
    