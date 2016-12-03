# -*- coding: utf-8 -*-

from flask import jsonify
from flask import request
from flask import render_template

from backend.foundation import app, db
from backend.models.movie import Movie, MovieLink


@app.route('/<string:template_name>')
def html(template_name):
    return render_template('{}'.format(template_name))


@app.route('/api/v1/search/<keyword>/', methods=['GET'])
def search_api(keyword):
    movies = db.session.query(Movie, MovieLink).\
        filter(Movie.name.like(u'%{}%'.format(keyword))).\
        filter(Movie.id == MovieLink.movie_id).\
        all()

    result = dict()
    for movie, link in movies:
        if movie.id not in result:
            result[movie.id] = dict(
                name=movie.name,
                downlist=[]
            )
        result[movie.id]['downlist'].append(dict(
            name=link.name,
            source=link.source,
            download_url=link.url
        ))

    movies = [data for mid, data in result.iteritems()]
    return jsonify(movies)


@app.route('/api/v1/movies', methods=['GET'])
def movies_list():
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    page_size = int(request.args.get('page_size', 24))
    total_size = Movie.query.count()

    movies = Movie.query.order_by(Movie.name)[(page - 1) * page_size: page * page_size]
    movies = [dict(name=movie.name, poster=movie.poster) for movie in movies]
    result = dict(
        movies=movies,
        pagination=dict(
            current_page=page,
            page_size=page_size,
            total_size=total_size))
    return jsonify(result)
