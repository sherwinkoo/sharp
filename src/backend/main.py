# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify

from xunbo import XunboHandler

app = Flask(__name__)


def get_handler(source):
    return XunboHandler


@app.route('/')
def main():
    with open('front/index.html', 'rt') as f:
        return f.read()


@app.route('/api/v1/<source>/<keyword>')
def search_api(source, keyword):
    handler = get_handler(source)
    r = handler().search(keyword)
    return jsonify(r)


if __name__ == '__main__':
    app.run()
