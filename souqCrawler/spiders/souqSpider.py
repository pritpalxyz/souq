# -*- coding: utf-8 -*-
import scrapy, re
from souqCrawler.items import SouqcrawlerItem
from bs4 import BeautifulSoup

class SouqspiderSpider(scrapy.Spider):
    name = "souqSpider"
    # allowed_domains = ["http://deals.souq.com/ae-en/"]
    start_urls = ['http://uae.souq.com/ae-en/shop-all-categories/c/']

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllListXpath = "//div[@class='grouped-list']//a/@href"
        self.getAllProductsXpath = "//a[@class='img-link quickViewAction']/@href"


        self.pageTitleXpath  = "//h1/text()"
        self.categoryXpath = "//div[@id='productTrackingParams']/@data-category-name"
        self.priceXpath = "//div[@id='productTrackingParams']/@data-price"
        self.discountedPriceXpath = "//span[@class='was']/text()"
        self.savingsXpath = "//span[@class='noWrap']/text()"
        self.solfByXpath = "//dt[text()='Sold by:']/following-sibling::dd[1]//a/text()"
        self.SellerRatingXpath = "//dt[text()='Sold by:']/following-sibling::dd[1]/span/span/small/text()"


    def parse(self, response):
        for href in response.xpath(self.getAllListXpath):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self,response):
        for href in response.xpath(self.getAllProductsXpath):
            url = href.extract()
            yield scrapy.Request(url,callback=self.parse_main_item)

    def parse_main_item(self,response):
        item = SouqcrawlerItem()

        Title = response.xpath(self.pageTitleXpath).extract()
        Title = self.cleanText(self.parseText(self.listToStr(Title)))

        Category = response.xpath(self.categoryXpath).extract()
        Category = self.cleanText(self.parseText(self.listToStr(Category)))

        CurrentPrice = response.xpath(self.priceXpath).extract()
        CurrentPrice = self.cleanText(self.parseText(self.listToStr(CurrentPrice)))

        OriginalPrice = response.xpath(self.discountedPriceXpath).extract()
        OriginalPrice = self.cleanText(self.parseText(self.listToStr(OriginalPrice)))
        OriginalPrice = OriginalPrice.replace("AED","")
        Discounted = 'False'
        if OriginalPrice == '':OriginalPrice=CurrentPrice
        else:Discounted = 'True'

        Savings = response.xpath(self.savingsXpath).extract()
        Savings = self.cleanText(self.parseText(self.listToStr(Savings)))
        Savings = Savings.replace("AED","")

        SoldBy = response.xpath(self.solfByXpath).extract()
        SoldBy = self.cleanText(self.parseText(self.listToStr(SoldBy)))

        SellerRating = response.xpath(self.SellerRatingXpath).extract()
        SellerRating = self.cleanText(self.parseText(self.listToStr(SellerRating)))

        item['Title']           = Title
        item['Category']        = Category
        item['OriginalPrice']   = OriginalPrice
        item['CurrentPrice']    = CurrentPrice
        item['Discounted']      = Discounted
        item['Savings']         = Savings
        item['SoldBy']          = SoldBy
        item['SellerRating']    = SellerRating
        item['Url']             = response.url
        yield item

    def listToStr(self,MyList):
        dumm = ""
        for i in MyList:dumm = "{0}{1}".format(dumm,i)
        return dumm

    def parseText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text
