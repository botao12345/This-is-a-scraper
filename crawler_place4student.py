import scrapy
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
import selenium
from selenium.webdriver.support.ui import WebDriverWait


class ForumItem(scrapy.Item):
    address = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()
    zip_code = scrapy.Field()
    name = scrapy.Field()
    phone = scrapy.Field()
    school = scrapy.Field()
    url = scrapy.Field()

def phoneformat(phone):
    phone = re.sub("\D", "", phone)
    return phone


class ForumSpider(scrapy.Spider):
    name = 'dwelbot'
    custom_settings = {'DOWNLOAD_DELAY': 0, 'LOG_LEVEL': 'INFO'}
    start_urls =['https://www.places4students.com/Search/Index']

    def parse(self, response):
        driver = webdriver.Firefox()
        driver.get(response.url)
        for letter in driver.find_elements_by_xpath('//div[@class ="container-fixed-height"]/div[1]/div[1]/div[1]/div[2]/ul/li'):
            link = letter.find_element_by_xpath('a').get_attribute('href')
            yield scrapy.Request(response.urljoin(link).replace('.aspx', ''), callback= self.parse_school)
        driver.close()

    def parse_school(self, response):
        for school in response.xpath('//div[@id="MainContent_divResultsWindow"]/table/tbody/tr'):
            school_name = school.xpath('td[1]/a/text()').extract_first()
            yield scrapy.Request(response.urljoin(school.xpath('td[1]/a/@href').extract_first()), callback= self.parse_get_listing, meta={'school_name': school_name})

    def parse_get_listing(self, response):
        link = response.xpath('//span[@id="MainContent_P4SThumbNail0_lbTextFooter"]/a[1]/@href').extract_first()
        school_name = response.meta['school_name']
        yield scrapy.Request(response.urljoin(link), callback=self.parse_listing, meta={'school_name': school_name})

    def parse_listing(self, response):
        driver = webdriver.Firefox()
        driver.implicitly_wait(10)
        school_name = response.meta['school_name']
        if 'Disclaimer' in response.url:
            driver.get(response.url)
            elem = driver.find_element_by_id('MainContent_btnAgere')
            elem.click()
        for listing in driver.find_elements_by_class_name('listing-title'):
            yield scrapy.Request(listing.find_element_by_xpath('a').get_attribute('href'), callback=self.parse_info, meta={'school_name': school_name})

        while True:
            try:
                current_page = int(driver.find_element_by_xpath('/html/body/form/div[5]/div/div[2]/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td/span').text)
                next_page = current_page + 1
            except selenium.common.exceptions.NoSuchElementException:
                next_page = 999999
            try:
                next_page = driver.find_element_by_xpath('/html/body/form/div[5]/div/div[2]/div/div/div/table/tbody/tr[1]/td/table/tbody/tr/td[%s]' % next_page )
                next_page.click()
                for listing in driver.find_elements_by_class_name('listing-title'):
                    try:
                        yield scrapy.Request(listing.find_element_by_xpath('a').get_attribute('href'),
                                             callback=self.parse_info, meta={'school_name': school_name})
                    except selenium.common.exceptions.StaleElementReferenceException:
                        print(driver.current_url)

            except selenium.common.exceptions.NoSuchElementException:
                driver.close()
                return False


    def parse_info(self, response):
        if 'Disclaimer' not in response.url:
            item = ForumItem()
            item['address'] = response.xpath('//div[@class="row"]/div[3]/div[1]/div[1]/text()').extract()[1][:-18][24:]
            item['city'] = response.xpath('//div[@class="row"]/div[3]/div[1]/div[@id="MainContent_trCity"]/text()').extract()[1][:-18][24:]
            item['state'] = response.xpath('//div[@class="row"]/div[3]/div[1]/div[@id="MainContent_trProvince"]/text()').extract()[1][:-18][24:]
            item['country'] = response.xpath('//div[@class="row"]/div[3]/div[1]/div[@id="MainContent_trCountry"]/text()').extract()[1][:-18][44:]
            item['zip_code'] = response.xpath('//div[@class="row"]/div[3]/div[1]/div[@id="MainContent_trZip"]/text()').extract()[1][:-18][24:]
            item['name'] = response.xpath('//div[@class="row"]/div[3]/div[1]/div[contains(string(), "Landlord Name:")]/text()').extract()[1][:-18][24:]
            item['phone'] = phoneformat(response.xpath('//div[@class="row"]/div[3]/div[1]/div[contains(string(), "Landlord Telephone:")]/text()').extract()[1][:-18][24:])
            item['school'] = response.meta['school_name']
            item['url'] = response.url
            yield item




process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)','FEED_FORMAT': 'csv',
                          'FEED_URI': 'place4student.csv'})

process.crawl(ForumSpider)
process.start()



