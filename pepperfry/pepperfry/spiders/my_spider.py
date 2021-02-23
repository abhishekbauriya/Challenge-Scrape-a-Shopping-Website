import scrapy
import re
import os
import requests
import json

# USER_AGENT = 'Chrome/77.0.3865.90' in settings.py

class pepperfrySpider(scrapy.Spider):
    name = "pepperfrySpider"
    BASE_DIR = "./Pepperfry_data/"
    MAX_CNT = 20

    def start_requests(self):
        # base url of the website
        BASE_URL = "https://www.pepperfry.com/site_product/search?q="

        # used to search a specific item
        items = ["book cases", "bean bags"]

        urls = []
        dir_names = []

        for item in items:
            query_string = '+'.join(item.split(' '))
            dir_name = '-'.join(item.split(' '))
            dir_names.append(dir_name)
            urls.append(BASE_URL + query_string)
            # store directory names and urls the items

            dir_path = self.BASE_DIR + dir_name
            # name the directory

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # if the directory does not exist, then create it
            

        #print(self.urls)
        # traverse all the urls
        for i in range(len(urls)):
            d = {
                "dir_name": dir_names[i]
            }
            # d gets the directory where current url things need to be saved

            resp = scrapy.Request(url = urls[i], callback = self.parse, dont_filter = True)
            resp.meta['dir_name'] = dir_names[i]
            yield resp
    
    def parse(self, response, **meta):
        product_urls = response.xpath('//div/div/div/h2/a/@href').extract()
        # get the url of the specific item of the product searched above

        counter = 0

        #print(product_urls)

        for url in product_urls:
            resp = scrapy.Request(url = url.split('?', 1)[0], callback = self.parse_item, dont_filter = True)
            resp.meta['dir_name'] = response.meta['dir_name']

            if counter == self.MAX_CNT:
                break

            if not resp == None:
                counter += 1

            yield resp

    def parse_item(self, response, **meta):
        item_title = response.xpath('//div/div/div/h1/text()').extract()[0]
        item_price = response.xpath('//div/div/div/span[@class="vip-our-price-amt font-18 pf-text-dark-grey pf-bold-txt"]/text()').extract()[0].strip()

        item_brand = response.xpath('//span[@itemprop="brand"]/text()').extract()

        d = {
            'Item title': item_title,
            'Item price': item_price,
            'Item brand': item_brand
        }

        img_url_list = response.xpath('//li[@class="vip-options-slideeach"]/a/@data-img').extract()


        # create another directory for a particular type of searched product
        CATEGORY_NAME = response.meta['dir_name']
        ITEM_DIR_URL = os.path.join(self.BASE_DIR, os.path.join(CATEGORY_NAME, item_title))


        if not os.path.exists(ITEM_DIR_URL):
            os.makedirs(ITEM_DIR_URL)

        # save directory in json format as metadata.txt
        with open(os.path.join(ITEM_DIR_URL, 'metadata.txt'), "w") as f:
            json.dump(d, f)

        # travel all the image urls and save the images as jpg
        for i, img_url in enumerate(img_url_list):
            if i == 2:
                break
            
            r = requests.get(img_url)

            with open(os.path.join(ITEM_DIR_URL, 'image_{}.jpg'.format(i)), 'wb') as f:
                f.write(r.content)

            
        yield d