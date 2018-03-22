import scrapy
from scrapy.crawler import CrawlerProcess

class ForumItem(scrapy.Item):
    name = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()



class ForumSpider(scrapy.Spider):
    name = 'dwelbot'
    custom_settings = {'DOWNLOAD_DELAY': 0, 'LOG_LEVEL': 'DEBUG'}
    start_urls =['https://studentaffairs.psu.edu/offcampus/hsearchlist.asp']

    def parse(self, response):
        item = ForumItem()
        for tr in  response.xpath('//tr[@align="center"]'):
            all_info = tr.xpath('td[6]/font/text()').extract()
            item['name'] = all_info[0]
            item['email'] = tr.xpath('td[6]/font/a/text()').extract_first()
            if len(all_info) == 2:
                item['phone'] = None
            else:
                item['phone'] = all_info[1]

            yield item

process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'FEED_FORMAT': 'csv',
                          'FEED_URI': 'result_psu.csv'})

process.crawl(ForumSpider)
process.start()