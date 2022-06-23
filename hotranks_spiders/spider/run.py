
from loguru import logger
from hotrank_spiders import *
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from baidu_hotrank import baidu_top_crawler 
from url_sync import update_all_daily_db_url
from news_crawler import news_detail_crawler # 更新详细信息爬虫

def hotrank_crawler(url, hotrank_name, columns):
    '''
    最终爬虫
    '''
    logger.info('开始爬取【{}】排行版信息'.format(hotrank_name.split('_')[0]))
    resp = downloader(url)
    # 实时部分
    logger.info('| STEP | 获取实时榜')
    parsed_data = hotrank_realtime_parser(hotrank_name, resp, columns)
    realtime_saver(parsed_data, hotrank_name)  # hotrank name 就是数据库里的table name
    print('='*100)
    logger.info('='*10 + ' HOT RANK CRAWLER FINISH ' + "="*10)
    print('='*100)
    # 历史部分
    # logger.info("| STEP | 获取历史榜")
    # hist_data = hotrank_history_parser(hotrank_name, resp, columns)
    # hist_saver(hist_data, hotrank_name+ "_history")


# ！主要在这里添加url和对应的字典
weibohot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
baidu_url = 'http://top.baidu.com/buzz?b=1&fr=topnews'
zhihu_url = 'https://www.zhihu.com/billboard'

toutiao_url = 'https://tophub.today/n/x9ozB4KoXb'
weixin_url = 'https://tophub.today/n/WnBe01o371'
tianmao_url = 'https://tophub.today/n/yjvQDpjobg'
douyin_url = 'https://tophub.today/n/DpQvNABoNE'
bilibili_url = "https://tophub.today/n/b0vmbRXdB1"
shuimu_url = "https://tophub.today/n/rDgeyqeZqJ"
sanliuling_url = "https://tophub.today/n/KMZd7x6erO"
sougou_url = "https://tophub.today/n/NaEdZndrOM"

# 新闻类：新闻类需要对url做解析，不能只拿标题
# pengpai_url = "https://tophub.today/n/wWmoO5Rd4E"
pengpai_sixiang_url = "https://tophub.today/n/WmoO54ld4E" # 思想频道
zaker_url = "https://tophub.today/n/5VaobJgoAj"
xinjingbao_url = "https://tophub.today/n/YqoXQ8XvOD"
cctv_international_url = "https://tophub.today/n/qndg1WxoLl"
guanchazhe_url = "https://tophub.today/n/RrvWOl3v5z"
tengxun_jiaozhen = "https://tophub.today/n/0MdKxr0ew1" # 辟谣平台，收集近期谣言


url_list = [{'今日头条': toutiao_url},
            {'微信': weixin_url},
            {'天猫': tianmao_url},
            {'抖音': douyin_url},
            {"bilibili": bilibili_url},
            {"水木社区":shuimu_url},
            {"sougou": sougou_url},
            {"360": sanliuling_url}
            ]

news_url_list = [
    # {"彭拜新闻": pengpai_url},
    {"彭拜思想": pengpai_sixiang_url},
    {"ZAKER": zaker_url},
    {"新京报": xinjingbao_url},
    {"cctv国际": cctv_international_url},
    {"观察者网": guanchazhe_url},
    {"腾讯辟谣": tengxun_jiaozhen},
    ]


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    ## baidu tops ##
    baidu_top_crawler()
    scheduler.add_job(baidu_top_crawler, 'cron', hour='*/2', minute="1")

    ## 普通热搜榜 ##
    # generate params
    realtime_params_list = [[list(url.values())[0], list(url.keys())[
        0], ['rank', 'keyword', 'score', 'other']] for url in url_list]
    logger.info("realtime cralwer params generated: {}".format(
        realtime_params_list))
        

    # [['https://tophub.today/n/x9ozB4KoXb', '今日头条_realtime', ['rank', 'keyword', 'score', 'other']] # data example
    for param in realtime_params_list:
        hotrank_crawler(param[0], param[1], param[2])
        scheduler.add_job(hotrank_crawler, 'cron', hour='*/2', minute="1", args=param)
        logger.info('添加【{}】任务成功'.format(param[1]))


    # 新闻类热搜榜
    # 参数生成
    xinwen_params_list = [[list(url.values())[0], list(url.keys())[0], ['rank', 'keyword', 'score', 'other']] for url in news_url_list] 
    logger.debug(xinwen_params_list)
    for param in xinwen_params_list:
        hotrank_crawler(param[0], param[1], param[2])
        scheduler.add_job(hotrank_crawler, 'cron', hour='*/2', minute="1", args=param)
        logger.info('添加【{}】任务成功'.format(param[1]))



    news_detail_crawler()
    update_all_daily_db_url()
    # 增加url_sync定时任务，从keyword_db中同步url到daily_db中
    scheduler.add_job(news_detail_crawler, 'cron', hour='*/2', minute='3')
    scheduler.add_job(update_all_daily_db_url, 'cron', hour='*/4', minute='10')

    # # 开启任务
    scheduler.start()
