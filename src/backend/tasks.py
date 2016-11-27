# -*- coding: utf-8 -*-

from foundation import celery as app_celery
from utils import http_get
from storage import MovieStorage


@app_celery.task(queue='dygod')
def fetch_dygod():
    for country in ('china', 'oumei', 'rihan'):
        url = 'http://www.dygod.net/html/gndy/{}/index.html'.format(country)
        fetch_dygod_country_page.delay(url)


@app_celery.task(queue='dygod')
def fetch_dygod_country_page(url):
    from parsers.dygod import DygodParser

    content = http_get(url).decode('gb18030')
    ulinks, next_page = DygodParser(url).parse_list(content)

    for ulink in ulinks:
        fetch_dygod_detail.delay(ulink)

    if next_page:
        fetch_dygod_country_page.delay(next_page)

    return url, next_page


@app_celery.task(queue='dygod')
def fetch_dygod_detail(url):
    from parsers.dygod import DygodParser

    content = http_get(url).decode('gb18030')
    info = DygodParser(url).parse(content)

    MovieStorage().save(info['name'], info)

    return info['name']
