# -*- coding: utf-8 -*-

from pprint import pprint

from flask_script import Manager

from backend.foundation import app
from backend.foundation import db
from backend.models import * # noqa
from backend.parsers import DygodParser


manager = Manager(app)


@manager.command
def create_db():
    db.create_all()


@manager.command
def add_movie(url):
    from parsers import Parser
    from parsers.dygod import DygodParser
    from tasks import fetch_dygod_detail

    parser = Parser.get_parser(url)
    if isinstance(parser, DygodParser):
        fetch_dygod_detail(url)
    else:
        print "No parser found!"


@manager.command
def test_parser(filename):
    with open(filename, 'rt') as f:
        content = f.read()
        content = content.decode('gb18030')

    parser = DygodParser()
    movie = parser.parse(content)
    pprint(movie)


@manager.command
def test_parse_list():
    from backend.utils import http_get
    import time

    for country in ('china', 'oumei', 'rihan'):
        start = 'http://www.dygod.net/html/gndy/{}/index.html'.format(country)

        url = start
        for i in range(40):
            content = http_get(url).decode('gb18030')
            ulinks, next_page = DygodParser(url).parse_list(content)
            print url, ulinks
            if not next_page:
                break
            url = next_page
            time.sleep(0.5)


@manager.command
def start_dygod():
    from backend.tasks import fetch_dygod
    fetch_dygod.delay()


@manager.command
def get_poster(url):
    from backend.common import fetch_poster
    print fetch_poster(url)


if __name__ == "__main__":
    manager.run()
