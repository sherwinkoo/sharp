# -*- coding: utf-8 -*-

from pprint import pprint

from flask_script import Manager

from foundation import app
from foundation import db
from models import * # noqa

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
def test_parser():
    from parsers import DygodParser
    from storage import MovieStorage

    with open('108745.html', 'rt') as f:
        content = f.read()

    parser = DygodParser()
    movie = parser.parse(content)
    pprint(movie)

    MovieStorage().save(movie['name'], movie)


@manager.command
def test_parse_list(url):
    from tasks import fetch_dygod_country_page
    fetch_dygod_country_page(url)


if __name__ == "__main__":
    manager.run()
