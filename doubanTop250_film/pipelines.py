# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
from scrapy import log
from doubanTop250_film.items import Doubantop250FilmItem


class Doubantop250FilmPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline(object):
    def __init__(self):
        pass
    
    def process_item(self, item, spider):
        if isinstance(item, Doubantop250FilmItem):       
            self.file = open('films/%s.json' % item['name'], 'w')
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
            return item
                


class CsvWriterPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        with open('films/result_film.csv', 'wb') as f:
            f.write('\xEF\xBB\xBF')
            self.csvwriter = csv.writer(f)
            self.csvwriter.writerow(['电影名称', '链接', '导演', '编剧', '主演', '国家和地区', '语言', '上映日期', '片长', '评分', '评分人数', '剧情简介'])
            self.csvwriter.writerow(item)
        return item
