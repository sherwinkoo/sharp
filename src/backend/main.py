# -*- coding: utf-8 -*-

import json
import base64

import redis
from flask import Flask
from flask import jsonify

cache = redis.Redis()

app = Flask(__name__)


@app.route('/')
def main():
    with open('front/index.html', 'rt') as f:
        return f.read()


@app.route('/api/v1/search/<keyword>/')
def search_api(keyword):
    keyword = keyword.encode('utf-8')
    targets = []
    keys = cache.keys("film:*")
    for key in keys:
        name = base64.b64decode(key.split(':')[1])
        if name.find(keyword) != -1:
            targets.append(key)
    if targets:
        results = cache.mget(targets)
    else:
        results = []
    results = [json.loads(r) for r in results]
    results = filter(lambda r: len(r['downlist']) > 0, results)
    results = sorted(results, key=lambda x: x['name'])
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
