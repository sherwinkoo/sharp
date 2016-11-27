# -*- coding: utf-8 -*-

from foundation import db
from models.movie import Movie, MovieLink


class MovieStorage(object):

    def save(self, name, detail):
        movie = Movie.query.filter_by(name=name).first()
        if not movie:
            movie = Movie(name, poster=detail['poster'])
            db.session.add(movie)
        movie.category = detail.get('category', '')
        movie.tags = detail.get('tags', '')
        movie.country = detail.get('country', '')

        self.save_seeds(movie, detail['links'])
        db.session.commit()

    def save_seeds(self, movie, download_urls):
        urls = set([seed.url for seed in movie.links])
        for down in download_urls:
            if down['download_url'] in urls:
                continue
            seed = MovieLink(
                down['name'], down['source'], down['download_url'],
                movie)
            db.session.add(seed)
