# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from itemadapter import ItemAdapter
import psycopg2


class IlcatsToyotaPipeline(object):
    # def process_item(self, item, spider):
    #     return item
    def open_spider(self, spider):
        hostname = '34.107.3.46'
        username = 'rugved'
        password = 'ASd4&*56fdKlsTT'
        database = 'partly'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()


    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):

        # try:
        self.cur.execute("""insert into index_data.ilcats_lexus 
        (part_information,
        car_info,
        url,
        category_tree,
        image) 
        values(%s, %s, %s, %s, %s);""", 
        (item['part_information'], 
        item['car_info'], 
        item['url'], 
        item['category_tree'], 
        item['image']))
        # except psycopg2.IntegrityError:
        #     self.conn.rollback()
        # finally:
        self.connection.commit()
        return item