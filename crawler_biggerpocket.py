import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess


class ForumItem(scrapy.Item):
    username = scrapy.Field()
    city = scrapy.Field()
    email = scrapy.Field()
    state = scrapy.Field()
    phone = scrapy.Field()
    company = scrapy.Field()
    occupation = scrapy.Field()
    url = scrapy.Field()


def cfDecodeEmail(encodedString):
    if encodedString:
        r = int(encodedString[:2],16)
        email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
        return email
    else:
        return None

class ForumSpider(scrapy.Spider):
    name = 'biggerbot'
    custom_settings = {'DOWNLOAD_DELAY': 0.8}
    start_urls =['https://www.biggerpockets.com/forums/21-real-estate-agents']

    def parse(self, response):
        for topic in response.xpath('//body/div[3]/div/div/div/table/tbody/tr'):
            yield scrapy.Request(response.urljoin(topic.xpath('td[1]/a/@href').extract_first()), callback=self.parse_post)

        next_page = response.xpath(
            'body/div[3]/div/div/div/header/div[3]/ul/li[last()]/a[@class="next-page"]/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)


    def parse_post(self, response):
        for post in response.xpath('//article[@class="post"]'):
            item = ForumItem()

            item['username'] = post.xpath('section/header/div[1]/h3/a/text()').extract_first()

            city = post.xpath('section/header/div[1]/h3/span[@class="city"]/text()').extract_first()
            if city is not None:
                item['city'] = city[:-2]
#            item['city'] = post.xpath('section/header/div[1]/h3/span[@class="city"]/text()').extract_first()[:-2]

            item['email'] = cfDecodeEmail(post.xpath('section/div[2]/div/div/div[last()]/a/@data-cfemail').extract_first())

            item['state'] = post.xpath('section/header/div[1]/h3/span[last()]/text()').extract_first()

            item['phone'] = post.xpath('section/div[2]/div/div/div[@class="component-signature-middle-info'
                                       ' component-signature-phone"]/text()').extract_first()

            item['company'] = post.xpath('section/div[2]/div/div/div[@class="component-signature-company-info '
                                         'component-signature-company-name '
                                         'component-signature-middle-info"]/a/text()').extract_first()

            item['occupation'] = post.xpath('section/header/div[1]/h3/span[1]/text()').extract_first()

            user_url = post.xpath('section/header/div[1]/h3/a/@href').extract_first()
            if user_url is not None:
                item['url'] = 'https://www.biggerpockets.com' + user_url

            if item['occupation'] is not None:
                if item['occupation'][:-2] == item['city']:
                    item['occupation'] = None

            yield item

        next_page = response.xpath('body/div[3]/div/div/div/header[2]/div[2]/ul/li[last()]/a[@class="next-page"]/@href').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_post)



process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'FEED_FORMAT': 'csv',
                          'FEED_URI': 'result_realestate_agents.csv'})

process.crawl(ForumSpider)
process.start()