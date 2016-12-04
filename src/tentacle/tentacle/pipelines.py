# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
from scrapy.pipelines.images import ImagesPipeline

from backend.utils import thunder_encode
from backend.storage import MovieStorage


class PosterPipeline(ImagesPipeline):
    """ 下载电影海报 """

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['poster'] = '/static/posters/' + image_paths[0]
        else:
            item['poster'] = ''
        return item


class TentaclePipeline(object):
    """ 保存抓取结果到数据库 """

    def process_item(self, item, spider):
        for link in item['links']:
            url = link['download_url']
            if url.startswith('ftp') or url.startswith('http'):
                url = thunder_encode(url)
            link['download_url'] = url

        MovieStorage().save(item['name'], item)
        return item
