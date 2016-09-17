# -*- coding: utf-8 -*-

import base64

import requests

from bs4 import BeautifulSoup


class XunboHandler(object):

    def thunder_encode(self, url):
        return 'thunder://' + base64.b64encode('AA' + url + 'ZZ')

    def process_gvodurls(self, js_line):
        addrs = js_line.split('"')[1].split('###')
        return [self.thunder_encode(addr.encode('utf-8')) for addr in addrs]

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
                    movie_list.append((li.a['href'], li.a['title']))
        return movie_list

    def search_list(self, keyword):
        r = requests.post('http://www.4567.tv/search.asp', data=dict(
            typeid=2,
            input=u'搜索'.encode('gb2312'),
            keyword=keyword.encode('gb2312')))
        return self.parse_search_list(r.content)

    def search(self, keyword):
        film_list = self.search_list(keyword)

        result = []
        for href, name in film_list:
            r = requests.get('http://www.4567.tv{}'.format(href))
            downlist = self.get_download_list(r.content)
            result.append(dict(
                name=name.encode('utf-8'), downlist=downlist))
        return result


if __name__ == "__main__":
    # with open("id4794.html", 'rt') as f:
    with open("search.asp", 'rt') as f:
        result = XunboHandler().parse_search_list(f.read())
    for r in result:
        print r
