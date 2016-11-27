# -*- coding: utf-8 -*-

import base64
import logging

from bs4 import BeautifulSoup

from settings import DEBUG
from storage import TaskManager


class XunboBase(object):
    SCHEMA = "http"
    DOMAIN = "www.4567.tv"
    HOST = SCHEMA + "://" + DOMAIN
    SEARCH_URL = HOST + '/search.asp'
    TYPES = [
        15,  # 电影
        16,  # 电视剧
    ]
    SOURCE = DOMAIN

    def request(self, url):
        import subprocess
        try:
            content = subprocess.check_output(['curl', url], stderr=subprocess.PIPE)
            content = content.decode('gb18030')
        except Exception as ex:
            logging.error("CURL: %s, %s", url, ex)
            return ''
        return content


class XunboSpider(XunboBase):

    def __init__(self):
        self.task_manager = TaskManager()

    def start(self, start_page=1):
        import time

        for t in self.TYPES:
            for i in range(start_page, 1000):
                movielist = self.fetch_list(t, page=i)
                for brief in movielist:
                    self.task_manager.add(brief)

                time.sleep(1)
                if DEBUG:
                    break

    def fetch_list(self, t, page=1, retry=3):
        movielist = []

        for i in range(0, retry):
            try:
                content = self.request(self.SEARCH_URL + '?searchtype=-1&page={}&t={}'.format(page, t))
                movielist = self.parse_page(content)
                if not movielist:
                    continue
                logging.debug("REQUEST: type:%s, page:%s, movies:%s", t, page, len(movielist))
                logging.debug("|".join([m['name'] for m in movielist]))
            except Exception as ex:
                logging.error("PARSE: type:%s, page:%s, %s", t, page, ex)
                if DEBUG:
                    raise
                with open('data/xunbo_{}_{}.html'.format(t, page), 'wt') as f:
                    f.write(content)

        return movielist

    def parse_page(self, content):
        movielist = []
        soup = BeautifulSoup(content, 'html.parser')
        divs = soup.find_all('div')
        for div in divs:
            if div.get('class') and 'movielist' in div.get('class'):
                for li in div.find_all('li'):
                    node = list(li.find('h5').children)[0]
                    name = node.text.encode('utf-8')
                    href = self.HOST + node.get('href').encode('utf-8')
                    movielist.append(dict(name=name, detail_url=href))
        return movielist


class XunboHandler(XunboBase):

    def thunder_encode(self, url):
        return 'thunder://' + base64.b64encode('AA' + url + 'ZZ')

    def process_gvodurls(self, js_line):
        def parse_filmname(addr):
            import urllib
            if isinstance(addr, unicode):
                addr = addr.encode('utf-8')

            if addr.startswith('ed2k://'):
                name = urllib.unquote(addr.split('|')[2])
            elif addr.startswith('ftp://'):
                name = addr.split('/')[-1]
            else:
                logging.warn('PARSE URLNAME: %s', addr)
                name = addr

            return name

        result = []
        addrs = js_line.split('"')[1].split('###')
        for addr in addrs:
            name = parse_filmname(addr)
            download_url = self.thunder_encode(addr.encode('utf-8'))
            result.append(dict(
                name=name,
                download_url=download_url,
                source=self.SOURCE,
            ))
        return result

    def parse_page(self, html_content):
        result = {
            'name': '',  # 影片名字
            'poster': '',  # 海报
            'category': '',  # 分类：电影、电视剧
            'tags': [],  # 类型
            'roles': [],  # 主演
            'country': '',  # 地区
            'story': '',  # 剧情
            'downlist': [],  # 下载链接
        }
        soup = BeautifulSoup(html_content, 'html.parser')
        result['name'] = self.parse_name(soup.title)

        divs = soup.find_all('div')
        for div in divs:
            classs = div.get('class')
            if not classs:
                continue

            if 'location' in classs:
                result['category'] = self.parse_category(div)

            if 'endpage' in classs:
                result.update(self.parse_info(div))

            if 'endtext' in classs:
                result['story'] = self.parse_story(div)

            if 'ndownlist' in classs:
                result['downlist'].extend(self.process_gvodurls(div.text.split(';')[0]))

        return result

    def parse_name(self, title):
        try:
            return title.text.split('-')[0]
        except:
            logging.warn("PARSE DETAIL title: %s", title)
        return ''

    def parse_category(self, div):
        try:
            return list(div.find_all('a'))[1].text
        except:
            logging.warn("PARSE DETAIL category: %s", div)
        return ''

    def parse_info(self, div):
        result = {}
        l = list(div.children)[0]
        try:
            result['poster'] = list(l.children)[0].img.get('src')
        except:
            logging.warn("PARSE DETAIL poster: %s", l)

        try:
            info = list(l.children)[1].ul.find_all('li')
        except:
            logging.warn("PARSE DETAIL info: %s", l)

        try:
            result['tags'] = [a.text for a in list(info[1].find_all('a'))]
        except:
            logging.warn("PARSE DETAIL tags: %s", info)

        try:
            result['roles'] = [a.text for a in list(info[2].find_all('a'))]
        except:
            logging.warn("PARSE DETAIL roles: %s", info)

        try:
            result['country'] = info[3].text
        except:
            logging.warn("PARSE DETAIL country: %s", info)

        return result

    def parse_story(self, div):
        return div.text

    def detail(self, name, url, retry=3):
        for i in range(0, retry):
            content = self.request(url)

            info = self.parse_page(content)
            if not info['downlist']:
                continue

        if not info['downlist']:
            logging.error("PARSE downlist: %s", url)
        else:
            logging.debug("SUCCESS: %s, %s found %s links.", name, url, len(info['downlist']))
        return info


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
    )
    XunboSpider().start(1)

    # XunboHandler().search('暮光之城4')
    # XunboHandler().detail(u'XXX', 'http://www.4567.tv/film/id23892.html')
    # print XunboHandler().detail(u'XXX', 'http://www.4567.tv/film/id8730.html')
    # print XunboHandler().detail(u'硅谷', 'http://www.4567.tv/film/id18157.html')
    # ml = XunboHandler().detail(u'幻城', 'http://www.4567.tv/film/id23761.html')
    # for m in ml:
    #     print m['name'], m['download_url']
    # XunboSpider().fetch_list(t=15, page=2)
