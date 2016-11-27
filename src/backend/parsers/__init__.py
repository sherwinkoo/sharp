# -*- coding: utf-8 -*-

# from .xunbo import XunboParser
from .dygod import DygodParser


class Parser(object):
    _PARSER_MAP = {
        # '4567.tv': XunboParser,
        'www.dygod.net': DygodParser,
    }

    @classmethod
    def get_parser(cls, url):
        from urlparse import urlparse
        domain = urlparse(url).hostname
        parser_class = cls._PARSER_MAP.get(domain, None)
        if not parser_class:
            raise Exception('No Parser for "{}"'.format(url))
        return parser_class()
