# encoding : UTF-8
import sys

# from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy_redis.spiders import RedisSpider
import re, time
from weibospider_phi.items import *
from lxml import etree
from weibospider_phi.utils import time_fix, extract_weibo_content, extract_comment_content
# from pyquery import PyQuery as pq


class TweetCommentSpider(RedisSpider):
    name = 'weibo_all_info'
    allow_domains = 'weibo.cn'

    user_info_url = 'https://weibo.cn/{uid}/info'
    fans_url = 'https://weibo.cn/{uid}/fans?page={page}'
    follow_url = 'https://weibo.cn/{uid}/follow?page={page}'
    tweet_url = 'https://weibo.cn/{uid}/profile?page={page}'
    tweet_detail_url = 'https://weibo.cn/comment/{tweet_id}?uid={uid}&rl=0#cmtfrm?page={page}' #https://weibo.cn/comment/IkVJM75fO?uid=2927104133&rl=0#cmtfrm

    base_url = 'https://weibo.cn'
    # start_urls = ['https://weibo.cn/1720399531/info']
    uids = ['1548710891', '2989369913', '7317446669', '6326382835'] #包含全文的页面
    redis_key = 'weibo_spider:start_urls'

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield Request(url, self.user_info_url)
        # for uid in self.uids:
        #     yield Request(self.user_info_url.format(uid=uid), callback=self.parse_user_info)



    def parse(self, response):
        """
        由用户的info详细页面开采集的。需要跳转一次到微博详细页面爬取剩余三个字段（微博数，好友数，粉丝数）
        :param response:
        :return:
        """
        user_item = UserItem()
        user_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
        selector = Selector(response)
        user_item['_id'] = re.findall('(\d+)/info', response.url)[0]
        user_info_text = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())
        nick_name = re.findall('昵称;?:?(.*?);', user_info_text)
        gender = re.findall('性别;?:?(.*?);', user_info_text)
        place = re.findall('地区;?:?(.*?);', user_info_text)
        brief_introduction = re.findall('简介;?:?(.*?);', user_info_text)
        birthday = re.findall('生日;?:?(.*?);', user_info_text)
        sex_orientation = re.findall('性取向;?:?(.*?);', user_info_text)
        sentiment = re.findall('感情状况;?:?(.*?);', user_info_text)
        vip_level = re.findall('会员等级;?:?(.*?);', user_info_text)
        authentication = re.findall('认证;?:?(.*?);', user_info_text)
        labels = re.findall('标签;?:?(.*?)更多>>', user_info_text)
        if nick_name and nick_name[0]:
            user_item["name"] = nick_name[0].replace(u"\xa0", "")
        if gender and gender[0]:
            user_item["sex"] = gender[0].replace(u"\xa0", "")
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split(" ")
            user_item["area"] = place[0]
            if len(place) > 1:
                user_item["city"] = place[1]
        if brief_introduction and brief_introduction[0]:
            user_item["self_intro"] = brief_introduction[0].replace(u"\xa0", "")
        if birthday and birthday[0]:
            user_item['birthday'] = birthday[0]
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                user_item["sex_orientation"] = "同性恋"
            else:
                user_item["sex_orientation"] = "异性恋"
        if sentiment and sentiment[0]:
            user_item["relationship"] = sentiment[0].replace(u"\xa0", "")
        if vip_level and vip_level[0]:
            user_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        if authentication and authentication[0]:
            user_item["authentication"] = authentication[0].replace(u"\xa0", "")
        if labels and labels[0]:
            user_item["tags"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')
        request_meta = response.meta
        request_meta['item'] = user_item
        yield Request(self.base_url + '/u/{}'.format(user_item['_id']),
                      callback=self.parse_user_info_detail,
                      meta=request_meta, dont_filter=True, priority=7)

    def parse_user_info_detail(self, response):
        text = response.text
        user_item = response.meta['item']
        tweets_num = re.findall('微博\[(\d+)\]', text)
        if tweets_num:
            user_item['tweets_count'] = int(tweets_num[0])
        follows_num = re.findall('关注\[(\d+)\]', text)
        if follows_num:
            user_item['follows_count'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', text)
        if fans_num:
            user_item['fans_count'] = int(fans_num[0])
        yield user_item
        # 对用户粉丝、关注、微博进行爬取
        yield Request(self.tweet_url.format(uid=user_item['_id'], page=1), callback=self.parse_tweet, dont_filter=False, priority=7)
        yield Request(self.fans_url.format(uid=user_item['_id'], page=1), callback=self.parse_fans, dont_filter=False, priority=8)
        yield Request(self.fans_url.format(uid=user_item['_id'], page=1), callback=self.parse_follows, dont_filter=False, priority=8)


    def parse_tweet(self,response):
        """
        爬取微博的详细信息
        :param response:
        :return:
        """
        # tree_node = etree.HTML(response.body)
        # next_page_exit = tree_node.xpath('//a[contains(text(),"下页")]/text()')
        # if next_page_exit:
        #     page_url = self.base_url + tree_node.xpath('//a[contains(text(),"下页")]/@href')[-1]
        #     yield Request(page_url, self.parse, dont_filter=True, meta=response.meta)
        ## another method of getting all pages
        if response.url.endswith('page=1'):
            ##-------------------------------- 分析翻页 --------------------------------_
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_tweet, dont_filter=False, meta=response.meta, priority=10)
            ##————————————————————————————————————————————————————————————————————————————————————


        tree_node = etree.HTML(response.body)
        raw_tweet_blocks = tree_node.xpath('//div[@class="c" and @id]') #这里为什么要先用etree一次？
        for one_tweet_block in raw_tweet_blocks:
            tweet_item = TweetItem()
            try:
                tweet_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
                # if one_tweet_block.xpath('.//a[contains(text(),"转发[")]/@href'):
                tweet_detail_url = one_tweet_block.xpath('.//a[contains(text(),"转发[")]/@href')[0] # 转发按钮中的连接可以跳转至该条微博的详细信息中
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_detail_url) # repost连接中包含两个id，分别为微博的连接和用户的加密ID
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_tweet_id.group(2),
                                                                           user_tweet_id.group(1))
                tweet_item['user_id'] = user_tweet_id.group(2)
                tweet_item['_id'] = one_tweet_block.xpath('./@id')[0]
                # time and come from what
                raw_time_tool = one_tweet_block.xpath('.//span[@class="ct"]')[0].text.split('\xa0来自') #这里注意可能有一个问题
                tweet_item['post_time'] = raw_time_tool[0] #### 注意！！！这里需要写一个ulit方法把时间格式转换了。
                tweet_item['send_from'] = raw_time_tool[1]
                # status part
                raw_repost_count = one_tweet_block.xpath('.//div/a[contains(text(),"转发[")]/text()')[-1]
                tweet_item['repost_count'] = re.search('[0-9]\d*',raw_repost_count).group()
                raw_thumbup_count = one_tweet_block.xpath('.//div/a[contains(text(),"赞[")]/text()')[-1]
                tweet_item['thumbup_count'] = re.search('[0-9]\d*', raw_thumbup_count).group()
                raw_comment_count = one_tweet_block.xpath('.//div/a[contains(text(),"评论[")]/text()')[-1]
                tweet_item['comment_count'] = re.search('[0-9]\d*', raw_comment_count).group()
                if_has_comment = re.search('[0-9]\d*', raw_comment_count).group()
                # pic or video
                pic = one_tweet_block.xpath('.//img[@alt="图片"]/@src')
                if pic:
                    tweet_item['pic_url'] = pic
                videos = one_tweet_block.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['video_url'] = videos
                # original posts
                repost_node = one_tweet_block.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    tweet_item['origin_weibo'] = repost_node[0]
                # location
                # map_node = one_tweet_block.xpath('.//a[contains(text(),"显示地图")]')
                # if map_node:
                #     map_node = map_node[0]
                #     map_node_url = map_node.xpath('./@href')[0]
                #     if re.search(r'xy=(.*?)&', map_node_url).group: ###修改了map如果错的逻辑
                #         map_info = re.search(r'xy=(.*?)&', map_node_url).group(1)
                #     else:
                #         self.logger.error('map_info error, line 95')
                #
                #     tweet_item['location_map_info'] = map_info
                ## ----------------判断是否有“全文”字段，需要打开详细页面去抓取内容，若无直接抓取当前页面内容
                if_extend_page = one_tweet_block.xpath('.//a/text()')
                if '全文' in if_extend_page:
                    yield Request(tweet_detail_url, callback=self.parse_tweet_detail, dont_filter=True, meta={'item':tweet_item})
                else:
                    # 首先需要判断是否是转发，如果是则选择div3的如果不是则选择div1的
                    if_repost = one_tweet_block.xpath('./div[1]/span[1]/text()')
                    if if_repost and '转发了\xa0' in if_repost:
                        repost_content = one_tweet_block.xpath('.//div[last()]')[0]
                        tweet_html = etree.tostring(repost_content, encoding='unicode')
                        tweet_item['content'] = extract_weibo_content(tweet_html)
                    else:
                        post_content = one_tweet_block.xpath('./div[1]')[0]
                        tweet_html = etree.tostring(post_content, encoding='unicode')
                        tweet_item['content'] = extract_weibo_content(tweet_html)
                yield tweet_item
                #---------------------------是！否！启！用！评！论！爬！虫！-------------------------------------
                tweet_comment_url = one_tweet_block.xpath('.//a[contains(text(),"评论[")]/@href')[0]
                if int(if_has_comment) > 0:
                    yield Request(tweet_comment_url + '&page=1', callback=self.parse_comments,
                                  dont_filter=False, priority=1)  # 抓取评论，重新请求连接内容
                # ---------------------------是！否！启！用！评！论！爬！虫！-------------------------------------
            except Exception as e:
                # print(e.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
                # print(e.__traceback__.tb_lineno)
                self.logger.error(e,e.__traceback__.tb_lineno)


    def parse_tweet_detail(self,response):
        one_tweet_block = etree.HTML(response.body)
        tweet_item = response.meta['item']
        # 首先需要判断是否是转发，如果是则选择div3的如果不是则选择div1的
        if_repost = one_tweet_block.xpath('//*[@id="M_"]/div[1]/span[1]/text()')
        if if_repost and ('转发了\xa0' or '\xa0转发了\xa0' in if_repost):
            repost_content = one_tweet_block.xpath('.//div[last()]')[0]
            tweet_html = etree.tostring(repost_content, encoding='unicode')
            tweet_item['content'] = extract_weibo_content(tweet_html)
        else:
            post_content = one_tweet_block.xpath('//*[@id="M_"]/div[1]')[0]
            tweet_html = etree.tostring(post_content, encoding='unicode')
            tweet_item['content'] = extract_weibo_content(tweet_html)
        yield tweet_item


    def parse_comments(self,response):
        tree_node = etree.HTML(response.body)
        next_page_exit = tree_node.xpath('//a[contains(text(),"下页")]/text()')
        if next_page_exit:
            page_url = self.base_url + tree_node.xpath('//a[contains(text(),"下页")]/@href')[-1]
            yield Request(page_url, self.parse_comments, dont_filter=False, meta=response.meta, priority=7)
        comment_nodes = tree_node.xpath('//div[@class="c" and contains(@id,"C_")]')
        for comment_node in comment_nodes:
            comment_user_url = comment_node.xpath('.//a[contains(@href,"/u/")]/@href')
            if not comment_user_url:
                continue
            comment_item = CommentItem()
            comment_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
            comment_item['weibo_id'] = response.url.split('/')[-1].split('?')[0]
            comment_item['comment_user_id'] = re.search(r'/u/(\d+)', comment_user_url[0]).group(1)
            comment_item['content'] = extract_comment_content(etree.tostring(comment_node, encoding='unicode'))
            comment_item['_id'] = comment_node.xpath('./@id')[0]
            created_at_info = comment_node.xpath('.//span[@class="ct"]/text()')[0]
            like_num = comment_node.xpath('.//a[contains(text(),"赞[")]/text()')[-1]
            comment_item['thumb_up_count'] = int(re.search('\d+', like_num).group())
            comment_item['post_time'] = time_fix(created_at_info.split('\xa0')[0])
            yield comment_item


    def parse_fans(self, response):
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_fans, dont_filter=True, meta=response.meta)
        ########################
        # if re.search('[1-9]\d*页', response.body) is not None:
        #     end_page = int(re.search('[0-9]\d*', pre_end_page.group()).group()) + 1
        # else:
        #     end_page = 1
        # for i in range(1, end_page):
        #     if i <= 20:
        #         nextpage = basic_page + '?page={}'.format(i)
        #         yield Request(nextpage, self.parse_fans,dont_filter=True, meta=response.meta)
        #
        #
        # fans_doc = pq(response.body)
        # pre_fans_items = fans_doc('td').items()
        # for f in pre_fans_items:
        #     if f('td').attr('style') is not None:
        #         relationships_item = RelationshipItem()
        #         relationships_item['icon'] = f('img').attr('src')
        #         relationships_item['homepage_link'] = f('a').attr('href')
        #     if f('td').attr('style') is None:
        #         relationships_item['name'] = f('a:nth-child(1)').text()
        #         # follow_item['_fans_count'] = re.search('粉丝[0-9]\d*', f.text()).group()
        #         # print(follow_item)
        #     yield relationships_item
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="移除"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/fans', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipItem()
            relationships_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
            relationships_item["fan_id"] = uid
            relationships_item["followed_id"] = ID
            relationships_item["_id"] = uid + '-' + 'fans' + '-' + ID
            yield relationships_item
            ## ---------------------------是否通过粉丝抓取下一个用户——————————————————————————————————
            next_url = self.user_info_url.format(uid=uid, page=1)
            yield Request(next_url, callback=self.parse, priority= -10)
            ## ——————————————————————————————————————————————————————————————————————————————————



    def parse_follows(self, response):
        if response.url.endswith('page=1'):
            all_page = re.search(r'/>&nbsp;1/(\d+)页</div>', response.text)
            if all_page:
                all_page = all_page.group(1)
                all_page = int(all_page)
                for page_num in range(2, all_page + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield Request(page_url, self.parse_follows, dont_filter=True, meta=response.meta)
        selector = Selector(response)
        urls = selector.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/follow', response.url)[0]
        print(ID)
        for uid in uids:
            relationships_item = RelationshipItem()
            relationships_item['crawl_time'] = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
            relationships_item["fan_id"] = ID
            relationships_item["followed_id"] = uid
            relationships_item["_id"] = ID + '-' + 'fans' + '-' + uid
            yield relationships_item
            ## ---------------------------是否通过关注抓取下一个用户——————————————————————————————————
            next_url = self.user_info_url.format(user_id=uid, page=1)
            yield Request(next_url, callback=self.parse, priority=-10)
            ## ——————————————————————————————————————————————————————————————————————————————————





