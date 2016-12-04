# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TentacleItem(scrapy.Item):
    name = scrapy.Field()
    poster = scrapy.Field()
    category = scrapy.Field()
    country = scrapy.Field()
    links = scrapy.Field()

    image_urls = scrapy.Field()
    images = scrapy.Field()


class TentacleLinkItem(scrapy.Item):
    name = scrapy.Field()
    source = scrapy.Field()
    download_url = scrapy.Field()
