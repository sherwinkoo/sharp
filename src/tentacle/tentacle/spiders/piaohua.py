# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request

from tentacle.items import TentacleItem, TentacleLinkItem


class PiaohuaSpider(scrapy.Spider):
    name = "piaohua"
    allowed_domains = ["www.piaohua.com"]
    start_urls = [
        'http://www.piaohua.com/html/kehuan/list_1.html',
        'http://www.piaohua.com/html/dongzuo/list_1.html',
        'http://www.piaohua.com/html/xiju/list_1.html',
        'http://www.piaohua.com/html/aiqing/list_1.html',
        'http://www.piaohua.com/html/juqing/list_1.html',
        'http://www.piaohua.com/html/xuannian/list_1.html',
        'http://www.piaohua.com/html/zhanzheng/list_1.html',
        'http://www.piaohua.com/html/kongbu/list_1.html',
        'http://www.piaohua.com/html/zainan/list_1.html',
        'http://www.piaohua.com/html/lianxuju/list_1.html',
        'http://www.piaohua.com/html/dongman/list_1.html',
    ]

    def parse(self, response):
        detail_urls = response.xpath('//div[@id="list"]/dl/dt/a/@href').extract()
        for url in detail_urls:
            yield Request(
                url="http://www.piaohua.com" + url,
                headers={
                    'Referer': response.url,
                    'Cache-Control': 'max-age=0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                })

        if not detail_urls:
            yield self.parse_detail(response)

    def parse_detail(self, response):
        item = TentacleItem()
        item['image_urls'] = response.xpath('//div[@id="showinfo"]/img[1]/@src').extract()

        for info in response.xpath('//div[@id="showinfo"]/p/text()').extract():
            info = info.strip('\r\n\t').replace(u'\u3000', ' ')
            if not info.startswith(u'\u25ce'):
                continue
            info = info[1:]
            if info.startswith(u'译  名') or info.startswith(u'片  名'):
                if item.get('name', ''):
                    item['name'] = item['name'] + '/' + info[5:]
                else:
                    item['name'] = info[5:]
            if info.startswith(u'类  别'):
                item['category'] = info[5:]
            if info.startswith(u'国  家'):
                item['country'] = info[5:]
        if not item.get('name', ''):
            try:
                item['name'] = response.xpath('//div[@id="showdesc"]/text()').extract()[0].strip('\r\n\t').split(' ')[0][3:]
            except:
                item['name'] = response.xpath('//div[@id="show"]/h3/text()').extract()

        item['links'] = []
        links = response.xpath('//div[@id="showinfo"]/table/tbody/tr/td/a/@href').extract()
        for url in links:
            url = url.strip('\r')

            link = TentacleLinkItem()
            try:
                link['name'] = url.split('/')[-1].split('[')[0]
            except:
                link['name'] = url
            link['source'] = response.url
            link['download_url'] = url

            item['links'].append(link)
        return item
