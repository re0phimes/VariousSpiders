import asyncio
from asyncore import loop
from email.mime import base
import aiohttp
from loguru import logger
from scrapy import Selector



base_url = "https://tophub.today/n/x9ozB4KoXb"
session = None

async def fetch(session, url):
    async with session.get(url) as response:
        return response.text


def parser(html):
    """
    解析一级页面链接
    """
    global session
    selector = Selector(html)
    parser_string = ".//table//td[@class='al']/a/@href"
    raw_urls = selector.xpath(parser_string).extract()
    return raw_urls
        

async def parse_raw_url(html):
    """
    解析二级而页面
    """
    global session
    selector = Selector(html)
    parse_raw_string = '//a[@class="l-view block l-image block"]/@href'
    real_urls = selector.xpath(parse_raw_string).extract()
    nums = len(real_urls)
    logger.debug(f"find {nums} real_urls")
    real_url = real_urls[0] if nums >= 1 else None
    logger.info(f"final url is {real_url}")

async def main():
    global session
    session = aiohttp.ClientSession()
    first_resp = await fetch(session, base_url)
    raw_urls = parser(first_resp)
    crawl_second_tasks = [asyncio.ensure_future(fetch(session, raw_url)) for raw_url in raw_urls]
    results = asyncio.gather(*crawl_second_tasks)
    # parse detail
    crawl_final_tasks = [asyncio.ensure_future(parse_raw_url(html)) for html in results]
    await asyncio.wait(crawl_final_tasks)
    await session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
        


    

    

    
    
    
        


# async def downloader(url):
#     async with aiohttp.ClientSession() as session:
#         html = await fetch(session, url)

