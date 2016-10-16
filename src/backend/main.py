# -*- coding: utf-8 -*-

import json
import base64

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
    return jsonify(list(movies))

    movies = sorted(movies, key=lambda x: x['name'])
    return jsonify(movies)


@app.route('/api/v1/movies', methods=['GET'])
def movies_list():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 24))
    total_size = 1024

    movies = []
    keys = cache.keys("film:*")
    targets = keys[(page - 1) * page_size:page * page_size]
    if targets:
        movies = cache.mget(targets)
    movies = [json.loads(m) for m in movies]
    # results = filter(lambda r: len(r['downlist']) > 0, results)
    # results = sorted(results, key=lambda x: x['name'])
    result = dict(
        movies=movies,
        pagination=dict(
            current_page=page,
            page_size=page_size,
            total_size=total_size))
    return jsonify(result)


@app.route('/tasks')
def tasks_view():
    from storage import TaskManager
    status = TaskManager().status()
    return jsonify(status)


if __name__ == '__main__':
    from settings import DEBUG
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
