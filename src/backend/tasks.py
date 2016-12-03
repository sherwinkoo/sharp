# -*- coding: utf-8 -*-

import logging

from backend.foundation import celery as app_celery
from backend.utils import http_get, thunder_encode
from backend.common import fetch_poster

from backend.parsers.dygod import DygodParser
from backend.storage import MovieStorage


@app_celery.task(queue='dygod')
def fetch_dygod():
    for country in ('china', 'oumei', 'rihan'):
        url = 'http://www.dygod.net/html/gndy/{}/index.html'.format(country)
        fetch_dygod_country_page.delay(url)


@app_celery.task(queue='dygod')
def fetch_dygod_country_page(url):

    try:
        content = http_get(url).decode('gb18030')
        ulinks, next_page = DygodParser(url).parse_list(content)

        for ulink in ulinks:
            fetch_dygod_detail.delay(ulink)

        if next_page:
            fetch_dygod_country_page.delay(next_page)

        return url, next_page
    except:
        logging.error("dygod: %s", url, exc_info=True)
    return url, None


@app_celery.task(queue='dygod')
def fetch_dygod_detail(url):
    content = http_get(url).decode('gb18030')
    try:
        info = DygodParser(url).parse(content)

        if info['poster'].startswith('http://'):
            info['poster'] = fetch_poster(info['poster'])

        for link in info['links']:
            if link['download_url'].startswith('ftp://') or link['download_url'].startswith('http://'):
                link['download_url'] = thunder_encode(link['download_url'])

        MovieStorage().save(info['name'], info)
        return url, info['name']
    except:
        logging.error("dygod: %s", url, exc_info=True)
    return url, None
