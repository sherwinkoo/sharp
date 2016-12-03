# -*- coding: utf-8 -*-

import os
import md5

from backend.utils import http_get


def fetch_poster(url):
    from backend.foundation import app

    data = http_get(url)
    name = md5.new(data).hexdigest()
    path = os.path.join(app.config['POSTER_DIR'], name)
    with open(path, 'wb') as f:
        f.write(data)
    return '/static/posters/{}'.format(name)
