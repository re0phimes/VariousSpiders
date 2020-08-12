
## 备用
from scrapy_redis.dupefilter import RFPDupeFilter
from scrapy.utils.request import

class TweetIDDuperFilter(RFPDupeFilter):

    def request_seen(self, request):
        request.url