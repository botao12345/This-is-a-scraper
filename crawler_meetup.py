import scrapy
from scrapy.crawler import CrawlerProcess

class ForumItem(scrapy.Item):
    name = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    Occupation = scrapy.Field()
    # phone = scrapy.Field()
    Email = scrapy.Field()
    # url = scrapy.Field()

class ForumSpider(scrapy.Spider):
    name = 'dwelbot'
    custom_settings = {'DOWNLOAD_DELAY': 0, 'LOG_LEVEL': 'DEBUG'}
    start_urls =['https://secure.meetup.com/login/?returnUri=https%3A%2F%2Fwww.meetup.com%2Fnjtech%2F']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response, formid= 'loginForm',
            formdata={'email': 'botao12345@gmail.com', 'password': '123456'},
            callback=self.after_login
        )

    def after_login(self, response):
        seeall = response.xpath('//*[@id="members"]/div[1]/div[2]/a/@href').extract_first()
        yield scrapy.Request(seeall, callback=self.allmember)

    def allmember(self, response):
        for member in response.xpath('//div[@class="doc-box"]/div[2]/div[@id="member_list"]/ul/li[@class="clearfix line memberInfo"]'):
            member_link = member.xpath('div/div[2]/h4/a/@href').extract_first()
            yield scrapy.Request(member_link, callback=self.member_info)

        current_page = int(response.xpath('//li[@class="nav-pageitem selected"]/a/text()').extract_first())
        next_page = current_page + 1
        next_page_link = response.xpath('//ul[@class="nav-pagination"]/li[contains(string(),%s)]/a/@href' % next_page).extract_first()
        if next_page_link is not None:
            print(current_page)
            yield scrapy.Request(next_page_link, callback=self.allmember)

    def member_info(self, response):
        item = ForumItem()
        item['name'] = response.xpath('//hgroup[@class="flush--bottom"]/h1/span[@class="memName fn"]/text()').extract_first()
        item['city'] = response.xpath('//*[@id="D_memberProfileMeta"]/div[1]/div/p/a/span[1]/text()').extract_first()
        item['state'] = response.xpath('//*[@id="D_memberProfileMeta"]/div[1]/div/p/a/span[2]/text()').extract_first()
        item['Occupation'] = response.xpath('//*[@id="D_memberProfileQuestions"]/div[6]/p/text()').extract_first()
        email = response.xpath('//*[@id="D_memberProfileQuestions"]/div[7]/p/text()').extract_first()
        if email.find('@') == -1:
            item['Email'] = None
        else:
            item['Email'] = email
        # item['phone'] = response.xpath('//*[@id="D_memberProfileQuestions"]/div[6]/p/text()').extract_first()
        # item['url'] = response.url
        yield item


process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)', 'FEED_FORMAT': 'csv',
                          'FEED_URI': 'result_meetup_nj_tech.csv'})

process.crawl(ForumSpider)
process.start()


