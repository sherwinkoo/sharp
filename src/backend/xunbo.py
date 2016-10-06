# -*- coding: utf-8 -*-

import base64

import requests
from bs4 import BeautifulSoup

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)


class XunboHandler(object):

    HOST = "http://www.4567.tv"
    SEARCH_URL = HOST + '/search.asp'
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
            else:
                name = addr.split('/')[-1]
            return name

        result = []
        addrs = js_line.split('"')[1].split('###')
        for addr in addrs:
            name = parse_filmname(addr)
            if not name:
                logging.warn("CANT RESOLVED RealURL: %s", addr)
            download_url = self.thunder_encode(addr.encode('utf-8'))
            result.append(dict(
                name=name,
                download_url=download_url,
                source=self.SOURCE,
            ))
        return result

    def get_download_list(self, html_content):
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
                        href=self.HOST + li.a['href'],
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
            r = requests.get(film['href'])
            downlist = self.get_download_list(r.content)
            result.append(dict(
                name=name.encode('utf-8'), downlist=downlist))
        return result


class XunboSpider(object):
    HOST = 'http://www.4567.tv'

    def start(self):
        import time

        for i in range(1, 33):
            time.sleep(1)

            logging.debug("fetch page %s", i)
            subfix = '' if i == 1 else '_{}'.format(i)
            r = requests.get(self.HOST + '/html/4{}.html'.format(subfix))
            if r.status_code != 200:
                logging.warn("page: %s return %s", i, r.status_code)
                continue

            names = self.parse_page(r.content)
            with open('names-xunbo.txt', 'a+') as f:
                f.write('|'.join(names) + '\n')

    def parse_page(self, content):
        names = []
        soup = BeautifulSoup(content, 'html.parser')
        divs = soup.find_all('div')
        for div in divs:
            if div.get('class') and 'movielist' in div.get('class'):
                for li in div.find_all('li'):
                    name = list(li.find('h5').children)[0].text.encode('utf-8')
                    names.append(name)
        return names


if __name__ == "__main__":
    # with open("tests/search.asp", 'rt') as f:
    #     result = XunboHandler().parse_search_list(f.read())
    # for r in result:
    #     print r['title'], r['href']

    # with open("tests/id4794.html", 'rt') as f:
    #     result = XunboHandler().get_download_list(f.read())
    # for r in result:
    #     print r['name'], r['download_url']
    # XunboHandler().search('暮光之城4')
    # with open("4_2.html", 'rt') as f:
    #     XunboSpider().parse_page(f.read())
    XunboSpider().start()
