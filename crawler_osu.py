import scrapy
from scrapy.crawler import CrawlerProcess

class ForumItem(scrapy.Item):
    name = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()



class ForumSpider(scrapy.Spider):
    name = 'dwelbot'
    custom_settings = {'DOWNLOAD_DELAY': 0, 'LOG_LEVEL': 'DEBUG'}
    start_urls =['https://offcampus.osu.edu/search-housing.aspx?pricefrom=0']

    def parse(self, response):
        for listing in response.xpath('//*[@id="properties"]/div'):
            yield scrapy.Request(response.urljoin(listing.xpath('div/h3/a/@href').extract_first()), callback= self.parse_info)

        next_page = response.xpath('//div[@id = "content"]/form/div[@id="mainbar"]/div/'
                                   'div[@class="paging"][1]/ul/li[contains(string(), "Next")]/a/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_info(self, response):
        item = ForumItem()
        all_info = response.xpath('//*[@id="contact"]/p/text()').extract()

        item['name'] = all_info[0][30:-1]

        for i in all_info:
            if 'Local' in i:
                item['phone'] = i.split(' ')[1]

        item['email'] = response.xpath('//*[@id="contact"]/p/a[1]/text()').extract_first()
        yield item

process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'FEED_FORMAT': 'csv',
                          'FEED_URI': 'result_osu.csv'})

process.crawl(ForumSpider)
process.start()