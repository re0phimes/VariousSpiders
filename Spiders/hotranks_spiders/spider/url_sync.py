from pymongo import MongoClient
import pymongo
from config import settings
from loguru import logger


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
daily_db_names = daily_db.list_collection_names()


# 读取没有url的daily数据
def query_keyword_url(keyword:str, col_name:str):
    query = {'keyword': {'$eq': keyword}}
    projection = {'url': 1}
    try:
        url = list(keyword_db[col_name].find(query, projection))[0].get('url')
        if url is not None:
            return url
    except Exception as e:
        logger.error(f"{keyword} 's url not found, error is {e}")


def update_daily_db_url(col_name: str):
    query = {'data': {'$elemMatch': {'url': {'$exists': False}}}}
    none_url_data = list(daily_db[col_name].find(query))
    num = len(none_url_data)
    logger.info(f"got {num} keywords")
    
    for item in none_url_data:
        for each_tops in item['data']:
            url = query_keyword_url(each_tops['keyword'], col_name)
            each_tops['url'] = url

        # logger.debug(item['data'])e
        filter = {'_id': item['_id']}
        update_res = daily_db[col_name].update_one(filter, {'$set' : {'data': item['data']}})
        logger.debug(f"update 【{col_name} - {item['_id']}】 result is {update_res.raw_result}")


def update_all_daily_db_url():
    for col_name in daily_db_names:
        update_daily_db_url(col_name) 
        print('-'*100)
    print('='*100)
    logger.info('='*10 + 'URL SYNC FINISH' + "="*10)
    print('='*100)




if __name__ == "__main__":
    update_all_daily_db_url()
    # update_daily_db_url('baidu')