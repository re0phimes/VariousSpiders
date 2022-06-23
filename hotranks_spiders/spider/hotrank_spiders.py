# -*- coding: utf-8 -*-  


from loguru import logger
import time
from datetime import datetime
from os import name
import requests, random
import pandas as pd
import pymongo
from pymongo.errors import DuplicateKeyError
# import logging
from logging import exception, handlers
from lxml import etree
# from crawlab import save_item

from apscheduler.schedulers.blocking import BlockingScheduler
import sys
sys.path.append("../")
from config import settings
from constants import user_agent_list
import requests
from typing import Dict
########## constants ##########
now = datetime.now()
format_time = now.strftime("%Y-%m-%d %H:%M")



########## set up logging config###################
logger.remove() # remove auto generate handler by import loguru, otherwise will print repeatly
info_handler = logger.add(sys.stderr, level="INFO")
logger.add("../logs/hotrank_spider_error_{time}.log", level="ERROR",encoding="utf-8", rotation="1 week")
logger.add("../logs/horank_spider_succ{time}.log", level="INFO", encoding="utf-8")

########### basic urls########################
weibohot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
baidu_url = 'http://top.baidu.com/buzz?b=1&fr=topnews'
zhihu_url = 'https://www.zhihu.com/billboard'
toutiao_url = 'https://tophub.today/n/x9ozB4KoXb'
weixin_url = 'https://tophub.today/n/WnBe01o371'
tianmao_url = 'https://tophub.today/n/yjvQDpjobg'
douyin_url = 'https://tophub.today/n/DpQvNABoNE'
sanliuling_url = "https://tophub.today/n/KMZd7x6erO"
pengpai_url = "https://tophub.today/n/wWmoO5Rd4E"
############ other constants ################
# logger.debug(settings.user_agent_list)
headers =  {
    "user-agent": random.choice(user_agent_list)
}


################# database settings ###########
<<<<<<< HEAD
mydb = pymongo.MongoClient(HOST_MONGO_HOST, HOST_MONGO_PORT)
# mydb.admin.authenticate('beihai','yaoduoxiang')
mycol = mydb['hot_rank']
scheduler = BlockingScheduler()
=======
server_name = settings['server_name']
ip = settings[server_name].ip
mongo_settings = settings[server_name].dbs.mongo


myclient = pymongo.MongoClient(ip, mongo_settings.port, username=mongo_settings.usr, password=mongo_settings.pwd)
# myclient.admin.authenticate(mongo_settings.usr, mongo_settings.pwd)
daily_db = settings['db_info']['mongo'].db_name
keyword_db_name = settings['db_info']['mongo'].db_name2 
mydb = myclient[daily_db]
keyword_db = myclient[keyword_db_name]

>>>>>>> server


############## spiders #########################
## 1. downloader ##
def downloader(url):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            logger.info(f'成功获取页面：{url}')
            # r.encoding = r.apparent_encoding
            return r.text
        else:
            logger.error('status code error : {}'.format(r.status_code))
            logger.info('-'*50)
    except Exception as e:
        logger.error(f"获取链接失败【{e}】")
        logger.error(e)



## 2. parser ##
def hotrank_realtime_parser(hotrank_name, response, columns = ['rank', 'keyword', 'score', 'other']):
    '''
    解析实时部分的数据网页内容返回字典
    :hotrank_name : 热搜榜名字
    :response : 网页response
    :columns : 重命名的columns
    '''
    df_list = pd.read_html(response)
    if len(df_list) > 1:
        df = df_list[-1]
        
        df.dropna(axis=1,how='all', inplace=True)
        # rename index
        try:
            logger.debug("获取表格列名为：{}".format(df.columns))
            logger.debug(df)
            df.columns = columns
        except Exception as e:
            logger.error(e)
            logger.debug('columns name:{}'.format(df.columns))
        finally:
            # df.drop(columns=list(df.columns)[-1], inplace=True)
            # df.columns = columns
            pass

        # change column data type
        try:
            logger.debug("尝试转换rank列为int类型")
            df['rank'] = df['rank'].astype('int')
        except Exception as e:
            logger.warning(e)
            logger.warning('由于解析columns错误，将index列转为rank列')
            try:
                df.drop(['rank'], axis=1, inplace=True)
                df = df.rename_axis("rank").reset_index()
            except:
                pass
        # remove error columns
        try:
            logger.debug("正在删除多余列")
            df.drop(columns=['other'], inplace=True)
            df.drop(columns=['other2'], inplace=True)
            df.drop(columns=['other3'], inplace=True)
        except Exception as e:
            pass 
        
        # add timestamp then convert data type
        dt = time.localtime(time.time())
        crawltime = time.strftime("%Y-%m-%d %H:%M:%S", dt)
        log_date = time.strftime("%Y-%m-%d", dt)
        list_rankdata = [dict(r) for i,r in df.iterrows()]
        for adata in list_rankdata:
            adata['time'] = log_date 
        dict_rankdata = {'_id':log_date, 'rank_name':hotrank_name, 'data':list_rankdata, 'crawltime': crawltime}
        example_data = list_rankdata[0]
        logger.info(f'成功解析实时数据：{example_data}')
        return dict_rankdata
    else:
        logger.error("未获取到表格")
        logger.error(e)

## 3. saver ##
def keyword_saver(one_top_data:Dict, tablename:str):
    # recorder
    recorder = [0, 0, 0]
    # validator
    try:
        one_top_data['keyword']
        one_top_data['rank']
        one_top_data['score']
        one_top_data['time']
        # logger.debug('valid data')
    except Exception as e:
        logger.error(f'data validate fail:【{one_top_data}】')
        # raise
    else: # check data exists
        keyword_col = keyword_db[tablename]
        query = {'keyword':{'$eq': one_top_data['keyword']}}
        res = list(keyword_col.find(query))
        if len(res) == 0: # keyword is new
            #存入
            new_data = {}
            new_data['keyword'] = one_top_data['keyword']
            new_data['show_rank'] = [one_top_data['rank']]
            new_data['show_date'] = [one_top_data['time']]
            new_data['show_score'] = [one_top_data['score']]
            new_data['last_update_time'] = round(time.time()*1000) 
            new_data['source'] = tablename
            res = keyword_col.insert_one(new_data)
            if res:
                recorder[0] += 1
            # logger.debug(f'insert_res: {res}')
        else:
            # 更新数据
            old_data =res[0]
            logger.debug(one_top_data)
            if one_top_data['time'] not in old_data['show_date']: # 如果没有记录过（当日内），则直接添加
                old_data['show_rank'].append(one_top_data['rank'])
                old_data['show_date'].append(one_top_data['time'])
                old_data['show_score'].append(one_top_data['score'])
                old_data['last_update_time'] = round(time.time()*1000)
                res = keyword_col.update_one(query, {'$set': old_data})
                
                if res:
                    recorder[1] += 1
                # logger.debug(f'update_result: {res}')
            else: # 如果已经记录过，则更新
                recorder[2] += 1
                # logger.warning(f"今日已经记录过, 更新分数和排行数据")
                old_data['show_rank'].pop()
                old_data['show_rank'].append(one_top_data['rank'])
                old_data['show_score'].pop()
                old_data['show_score'].append(one_top_data['score'])
                old_data['last_update_time'] = round(time.time()*1000) 
                res = keyword_col.update_one(query, {'$set': old_data})
        return recorder
            
        
def realtime_saver(hotrank_dict, tablename):
    """
    将单个平台热搜榜存入tops_daily库，处理成以关键词为主键存入tops_keywords库
    hotrank_dict: return value of hotrank_realtime_parser funciton
    """
    mycol = mydb[tablename]
    keyword_col = keyword_db[tablename]
    try:
        mycol.insert_one(hotrank_dict)
        logger.info('{}-{} 写入成功'.format(hotrank_dict['_id'], hotrank_dict['rank_name']))
    except Exception as e:
        if type(e) == DuplicateKeyError:
            logger.warning('今日已抓取过，现在更新')
            
            # 更新今日数据：若热搜已经有url和label则在新数据上更新。
            old_data = list(mycol.find({'_id':{'$eq': hotrank_dict['_id']}},{}))[0] # 因为是duplicate key了数据必然存在
            old_news_list = old_data['data']
            new_news_list = hotrank_dict['data']
            for new_news in new_news_list:
                for old_news in old_news_list:
                    if (new_news['keyword'] == old_news['keyword']) and (old_data.get('tag') is not None): # 有tag则更新tag
                        new_news['tag'] = old_data.get('tag')
                    if( new_news['keyword'] == old_news['keyword']) and (old_data.get('url') is not None):
                        new_news['url'] = old_news.get('url')
            mycol.update_one({'_id': hotrank_dict['_id']}, {'$set': hotrank_dict})
        else:
            logger.error(e)
            logger.error('{}-{} 写入失败'.format(hotrank_dict['_id'], hotrank_dict['rank_name']))

    # 将实施数据中的关键词提取出来，并写入关键词数据库。
    # record
    insert_num = 0
    update_num = 0
    duplicate_num = 0
    for item in hotrank_dict['data']:
        recorder = keyword_saver(item, tablename)
        if recorder:
            insert_num += recorder[0]
            update_num += recorder[1]
            duplicate_num += recorder[2]
    logger.info(f'DB SAVE RESULT: insert num-{insert_num}, update num-{update_num}, duplicate num-{duplicate_num}')

<<<<<<< HEAD
# =======================================================================
def main():
    weibo_hot(weibohot_url)
    baidu_hot(baidu_url)
    zhihu_hot(zhihu_url)
    toutiao_hot(toutiao_url)
    logger.info('==========================================================')


main()
scheduler.add_job(main, 'interval', minutes =30)
scheduler.start()
# scheduler.add_job(weibo_hot, 'interval', minutes =30,args=[weibohot_url])
# scheduler.add_job(baidu_hot, 'interval', minutes =30,args=[baidu_url])
# scheduler.add_job(zhihu_hot, 'interval', minutes =30,args=[zhihu_url])
# scheduler.add_job(toutiao_hot, 'interval', minutes=30, args=[toutiao_url])
=======
## saver ##

    


if __name__ == "__main__":
    # scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    resp = downloader(pengpai_url)
        # 实时部分
    parsed_data = hotrank_realtime_parser("澎湃新闻", resp)
    realtime_saver(parsed_data, "澎湃新闻")
        # 历史部分
    # hist_data = hotrank_history_parser("微信", resp)
    logger.info(parsed_data)
>>>>>>> server
