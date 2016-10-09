# -*- coding: utf-8 -*-

import base64
import logging

import requests
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
    ]

    def request(self, url):
        import subprocess
        try:
            content = subprocess.check_output(['curl', url], stderr=subprocess.PIPE)
        except Exception as ex:
            logging.error("CURL: %s, %s", url, ex)
            return ''
        return content


class XunboHandler(XunboBase):

    SOURCE = 'www.xunbo.cc'

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

    def get_download_list(self, html_content):
        # import pdb; pdb.set_trace()
        soup = BeautifulSoup(html_content, 'html.parser')
        divs = soup.find_all('div')
        for div in divs:
            if div.get('class') and 'ndownlist' in div.get('class'):
                return self.process_gvodurls(div.text.split(';')[0])
        else:
            return []

    def parse_search_list(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        movie_list = []
        for div in soup.find_all('div'):
            if div.get('class') and 'movielist' in div.get('class'):
                for li in div.find_all('li'):
                    movie_list.append(dict(
                        detail_url=self.HOST + li.a['href'],
                        title=li.a['title'],
                    ))
        return movie_list

    def search_list(self, keyword):
        if isinstance(keyword, str):
            keyword = keyword.decode('utf-8')

        r = requests.post(self.SEARCH_URL, data=dict(
            typeid=2,
            input=u'搜索'.encode('gbk'),
            keyword=keyword.encode('gbk')))
        return self.parse_search_list(r.content)

    def search(self, keyword):
        film_list = self.search_list(keyword)

        result = []
        for film in film_list:
            name = film['title']
            downlist = self.detail(film['detail_url'])
            result.append(dict(
                name=name.encode('utf-8'), downlist=downlist))
        return result

    def detail(self, name, url):
        # r = requests.get(url)
        # content = r.content
        # if r.status_code != 200:
        #     logging.error("REQUEST: %s, %s", r.status_code, url)
        #     return []
        content = self.request(url)

        downlist = self.get_download_list(content)
        if not downlist:
            logging.error("PARSE downlist: %s", url)
        else:
            logging.debug("SUCCESS: %s, %s found %s links.", name, url, len(downlist))
        return downlist


class XunboSpider(XunboBase):

    def __init__(self):
        self.task_manager = TaskManager()

    def start(self):
        import time

        for t in self.TYPES:
            for i in range(1, 1000):
                movielist = self.fetch_search_list(t, page=i)
                for brief in movielist:
                    self.task_manager.add(brief)

                time.sleep(1)
                if DEBUG:
                    break

    def fetch_search_list(self, t, page=1):
        movielist = []

        # r = requests.get(self.SEARCH_URL, params=dict(searchtype=-1, page=page, t=t))
        # content = r.content
        # if r.status_code != 200:
        #     logging.error("REQUEST: type:%s, page:%s,  return %s", t, page, r.status_code)
        #     return movielist
        content = self.request(self.SEARCH_URL + '?searchtype=-1&page={}&t={}'.format(page, t))

        try:
            movielist = self.parse_page(content)
            logging.debug("REQUEST: type:%s, page:%s, movies:%s", t, page, len(movielist))
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


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
    )

    # with open("tests/search.asp", 'rt') as f:
    #     result = XunboHandler().parse_search_list(f.read())
    # for r in result:
    #     print r['title'], r['href']

    # with open("id23892.html", 'rt') as f:
    #     result = XunboHandler().get_download_list(f.read())
    # for r in result:
    #     print r['name'], r['download_url']
    # XunboHandler().search('暮光之城4')
    # with open("4_2.html", 'rt') as f:
    #     XunboSpider().parse_page(f.read())
    XunboSpider().start()
    # XunboHandler().detail(u'XXX', 'http://www.4567.tv/film/id23892.html')
