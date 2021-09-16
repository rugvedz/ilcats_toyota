# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy import Field, Item

class IlcatsToyotaItem(scrapy.Item):
    part_information = scrapy.Field()
    car_info = scrapy.Field()
    url = scrapy.Field()
    category_tree = scrapy.Field()
    image = scrapy.Field()
