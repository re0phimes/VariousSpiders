import requests
import pandas as pd
import pymongo
import time
import logging
from lxml import etree
from apscheduler.schedulers.blocking import BlockingScheduler

# set up log config
# logger = logging.getLogger('hotrank_logger')
logging.basicConfig(level = logging.INFO,
                    filename = 'hotrank_spider.log',
                    filemode = 'a',
                    format=
                    '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

# basic urls
weibohot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
baidu_url = 'http://top.baidu.com/buzz?b=1&fr=topnews'
zhihu_url = 'https://www.zhihu.com/billboard'

# header info, for now, only used in baidu zhihu_hotrank
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': '_zap=259afda1-92a7-4f90-a0ec-e3f60dbace0d; _xsrf=tC6CE28898gCK4h9FmeMF32SOv5weZDL; d_c0="AFBfMzwsrhGPTglqXvZ3fhFpSPqxrpugj2c=|1596526314"; _ga=GA1.2.1106294443.1596526316; capsion_ticket="2|1:0|10:1596526316|14:capsion_ticket|44:NjViYTFjZmQ2NzllNGEzNWFlMjk2MTFhNGQ1NmNiMTE=|8379c8353cd75cae1b4f306a5171629be0c72e3002fb45508ab3335085a2c577"; z_c0="2|1:0|10:1596526325|4:z_c0|92:Mi4xOFNBekFBQUFBQUFBVUY4elBDeXVFU1lBQUFCZ0FsVk45VndXWUFBVmtDV0wwbmN2UllDdkxVaTNpS0t5UURHNGdR|c3df7545e754c928438d2586f89b5d260202dd5bf64887e04db3e8a04e6b602b"; q_c1=16ef6e89802249379877df7bd4456c09|1596595738000|1596595738000; _gid=GA1.2.35532845.1597021484; tst=h; tshl=; SESSIONID=ozvvmld4MyquciCTkzlD6xwJuMjrgH1sWKaxnSQ9H3E; JOID=WlwXA0rOyEHsakoJScYNWT1VbqJSrbQ1mw4qa3-KvTabCCpGG0AxcrtvQA1Kni90kaYRm2RJ6mIZZlwZv70b6NM=; osd=VlAXAEPCxEHvY0YFScUEVTFVbateobQ2kgIma3yDsTqbCyNKF0Aye7djQA5DkiN0kq8dl2RK424VZl8Qs7Eb69o=; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1597041118,1597041771,1597045814,1597046213; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1597046717; _gat_gtag_UA_149949619_1=1; KLBRSID=4843ceb2c0de43091e0ff7c22eadca8c|1597046723|1597045624'
}


# database settings
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27000
mydb = pymongo.MongoClient(MONGO_HOST,MONGO_PORT)
mycol = mydb['hot_rank']
scheduler = BlockingScheduler()


# spiders
def weibo_hot(url):
    '''
    微博爬虫
    '''
    dt = time.localtime(time.time())
    crawltime = time.strftime("%Y-%m-%d %H:%M:%S", dt)
    r = requests.get(url)
    df = pd.read_html(url,index_col=0,header=0)[0]
    df.index.name = 'index'
    df.rename(columns={'关键词':'keyword','Unnamed: 2':'description'},inplace=True)
    df[['keyword','value']] = df['keyword'].str.rsplit(' ',expand=True,n=1)
    data = [dict(r) for i,r in df.iterrows()]
    one_data = {'_id':crawltime, 'data':data}
    mycol['weibo_hot'].insert_one(one_data)
    logging.INFO('DateTime:' + crawltime + ' weibo data downloaded')

def baidu_hot(url):
    '''
    百度爬虫
    '''
    dt = time.localtime(time.time())
    crawltime = time.strftime("%Y-%m-%d %H:%M:%S", dt)
    baiduDF = pd.read_html(url, index_col=0)[0].drop(columns=['相关链接'])
    baiduDF.index.name = 'index'
    # clean data
    for x in baiduDF.index:
        if len(x) > 2:
            baiduDF.drop(index=x, inplace=True)
    baiduDF.rename(columns={'关键词':'keyword','搜索指数':'score'},inplace=True)
    baiduDF['keyword'] = baiduDF['keyword'].str.rsplit(' ',expand=True,n=1)
    baiduData = [dict(r) for i,r in baiduDF.iterrows()]
    one_data = {'_id':crawltime, 'data':baiduData}
    mycol['baidu_realtime_hot'].insert_one(one_data)
    logging.INFO('DateTime:' + crawltime + ' baidu downloaded')
    # print('DateTime:' + crawltime + ' baidu data hdownloaded')


def zhihu_hot(url):
    '''
    知乎爬虫
    '''
    r = requests.get(zhihu_url,headers=headers)
    tree_node = etree.HTML(r.text)
    item_node = tree_node.xpath('//div[@class="HotList-itemBody"]')
    zhihuDataList = []
    for x in item_node:
        one_data = {}
        one_data['keyword'] = x.xpath('./div[@class="HotList-itemTitle"]/text()')[0]
        one_data['score'] = x.xpath('./div[@class="HotList-itemMetrics"]/text()')[0]
        zhihuDataList.append(one_data)
    dt = time.localtime(time.time())
    crawltime = time.strftime("%Y-%m-%d %H:%M:%S", dt)
    zhihuData = {'_id':crawltime, 'data':zhihuDataList}
    mycol['zhihu_hot'].insert_one(zhihuData)
    logging('DateTime:' + crawltime + ' zhihu data downloaded')

scheduler.add_job(weibo_hot, 'interval', minutes =30,args=[weibohot_url])
scheduler.add_job(baidu_hot, 'interval', minutes =30,args=[baidu_url])
scheduler.add_job(zhihu_hot, 'interval', minutes =30,args=[zhihu_url])
scheduler.start()