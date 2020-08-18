
## 备用
from scrapy_redis.dupefilter import RFPDupeFilter
# from scrapy.utils.request import

    class TweetIDDuperFilter(RFPDupeFilter):
#
    def __fitler_refer(self,request):



    def request_seen(self, request):
        if request.url[-6:] == 'page=1':
            return False
