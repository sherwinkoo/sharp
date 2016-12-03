# -*- coding: utf-8 -*-

import urlparse

from bs4 import BeautifulSoup


class DygodParser(object):

    def __init__(self, url=None):
        self.url = url
        r = urlparse.urlparse(url)
        self.domain = r.scheme + "://" + r.hostname

    def parse_list(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        ulinks = soup.find_all('a', attrs={'class': 'ulink'})
        for a in soup.find_all('a'):
            if a.text == u'下一页':
                next_page = self.domain + a.attrs['href']
                break
        else:
            next_page = None
        return [self.domain + ulink.attrs['href'] for ulink in ulinks], next_page

    def parse(self, content):
        info = {}

        soup = BeautifulSoup(content, 'html.parser')
        zoom = soup.find('div', attrs={'id': 'Zoom'})
        attrs = zoom.find_all('p')

        detail_text = ''
        for attr in attrs:
            detail_text += attr.text.replace(u'\u3000', u' ')

        for text in detail_text.split(u'\u25ce'):
            text = text.lstrip(u'\u25ce')
            if text.startswith(u'片  名') or text.startswith(u'译  名'):
                if 'name' in info:
                    info['name'] = info['name'] + '/' + text[5:]
                else:
                    info['name'] = text[5:]
            elif text.startswith(u'类  别'):
                info['category'] = text[5:]
            elif text.startswith(u'国  家'):
                info['country'] = text[5:]
        info['poster'] = zoom.find('img').attrs['src']

        link = zoom.find('table').find('tr').find('td').find('a').attrs['href']
        name = '.'.join(link.split('/')[-1].split('.')[:-1])
        info['links'] = [{
            'name': name,
            'download_url': link,
            'source': self.url,
        }]
        return info
