from scrapy import Spider
from scrapy.http import Request
import re, time
from weibospider_phi.items import TweetItem, CommentItem
from lxml import etree
from weibospider_phi.utils import time_fix, extract_weibo_content, count_extract, extract_comment_content


class TweetCommentSpider(Spider):
    name = 'comment'
    # allow_domains =
    # start_url =
    # start_urls = ['https://weibo.cn/u/2970452952']
    start_urls = ['https://weibo.cn/comment/FbQ8KATK9?rl=0&page=1'] #包含全文的页面
    base_url = 'https://weibo.cn'


    def parse(self,response):
        # print(response.url)
        tree_node = etree.HTML(response.body)
        next_page_exit = tree_node.xpath('//a[contains(text(),"下页")]/text()')
        if next_page_exit:
            page_url = self.base_url + tree_node.xpath('//a[contains(text(),"下页")]/@href')[-1]
            yield Request(page_url, self.parse, dont_filter=True, meta=response.meta)

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
