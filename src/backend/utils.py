# -*- coding: utf-8 -*-

import base64


def safe_utf8(string):
    if isinstance(string, unicode):
        return string.encode('utf-8')
    return string


def safe_unicode(string):
    if isinstance(string, str):
        return string.decode('utf-8')
    return string


def http_get(url, timeout=30):
    import requests
    r = requests.get(
        url,
        headers={'User-Agent': 'User-Agent Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14'},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.content


def thunder_encode(url):
    return 'thunder://' + base64.b64encode('AA' + safe_utf8(url) + 'ZZ')
