import scrapy
from scrapy.selector import Selector

class HeaderSpider(scrapy.Spider):
    name = "header"

    

    def start_requests(self):
        self.places = []
        urls = [
            'https://en.wikipedia.org/wiki/List_of_United_Kingdom_locations',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        
       

        print("places"+len(self.places))

        

    def parse(self, response):
        print('here')
        sel = Selector(response)
        for div in sel.xpath("//div[@id='mw-content-text']/div/ul/li/a/@href"):
        #for div in response.xpath('//div').get():
            print (div.get())
            yield scrapy.Request(url="https://en.wikipedia.org"+div.get(), callback=self.parse_sub_table)

    def parse_sub_table(self,response):
        sel = Selector(response)
        for div in sel.xpath("//table[@class='wikitable']/tbody/tr/td/a/text()"):
            print(div.get())
            self.places.append(div.get())
        for div in sel.xpath("//table[@class='wikitable']/tbody/tr/td/text()"):
            print(div.get())
            self.places.append(div.get())
    
    def closed(self, reason):
        f = open("uk_places1.txt", "w")
        for p in self.places:
            f.write(p+"\n")
        f.close()