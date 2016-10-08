# -*- coding: utf-8 -*-


def safe_utf8(string):
    if isinstance(string, unicode):
        return string.encode('utf-8')
    return string


def safe_unicode(string):
    if isinstance(string, str):
        return string.decode('utf-8')
    return string
