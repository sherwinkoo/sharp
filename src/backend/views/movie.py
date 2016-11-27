# -*- coding: utf-8 -*-

from pymongo import MongoClient

from flask import Flask
from flask import jsonify
from flask import request

client = MongoClient()
movie_doc = client['movie-db']['movie']

app = Flask(__name__)


@app.route('/')
def main():
    with open('front/index.html', 'rt') as f:
        return f.read()


@app.route('/list.html')
def list_view():
    with open('front/list.html', 'rt') as f:
        return f.read()


@app.route('/api/v1/search/<keyword>/', methods=['GET'])
def search_api(keyword):
    keyword = keyword.encode('utf-8')
    movies = movie_doc.find({'name': {'$regex': '.*{}.*'.format(keyword)}})
    movies = list(movies)
    for m in movies:
        del m['_id']

    movies = sorted(movies, key=lambda x: x['name'])
    return jsonify(movies)


@app.route('/api/v1/movies', methods=['GET'])
def movies_list():
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    page_size = int(request.args.get('page_size', 24))
    total_size = 1024

    movies = movie_doc.find()
    movies = list(movies)
    for m in movies:
        del m['_id']
    movies = sorted(movies, key=lambda x: x['name'])

    movies = movies[(page - 1) * page_size:page * page_size]
    result = dict(
        movies=movies,
        pagination=dict(
            current_page=page,
            page_size=page_size,
            total_size=total_size))
    return jsonify(result)
