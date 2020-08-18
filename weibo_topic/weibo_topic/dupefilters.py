
## 备用
from scrapy_redis.dupefilter import RFPDupeFilter
# from scrapy.utils.request import

class WeiboTopicDupeFilter(RFPDupeFilter):
    def request_seen(self, request):
        if 'root_comment_id' in request.url:
            url_temp_list = request.url.split('&')
            filter_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&{}&{}&{}&{}'.format(url_temp_list[1], url_temp_list[2], url_temp_list[4], url_temp_list[5])
            fp = self.request_fingerprint(filter_url)
            added = self.server.sadd(self.key, fp)
            return added == 0
        # 如果是如果结尾表示为第一页，则不进行过滤
        if request.url[-6:] == 'page=1':
            return False
        fp = self.request_fingerprint(request)
        added = self.server.sadd(self.key, fp)
        return added == 0
