# -*- coding: utf-8 -*-

from foundation import db


class Movie(db.Model):
    """ 电影的内容  """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)
    poster = db.Column(db.String(1024))
    category = db.Column(db.String(128))
    tags = db.Column(db.String(128))
    country = db.Column(db.String(40))

    def __init__(self, name, poster):
        self.name = name
        self.poster = poster


class MovieLink(db.Model):
    """ 电影的下载链接 """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    source = db.Column(db.String(256))
    url = db.Column(db.String(512))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    movie = db.relationship(
        'Movie',
        backref=db.backref('links', lazy='dynamic'))

    def __init__(self, name, source, url, movie):
        self.name = name
        self.source = source
        self.url = url
        self.movie = movie
