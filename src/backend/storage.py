# -*- coding: utf-8 -*-

import json
import base64

from redis import Redis

from xunbo import XunboHandler

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)

cache = Redis()


class StorageLoop(object):

    def __init__(self):
        self.engines = [
            XunboHandler(),
        ]

    def fetch_next(self):
        return cache.rpop('film_name_queue')

    def push(self, name):
        cache.lpush('film_name_queue', name)

    def do_search_engine(self, name):
        results = []
        for engine in self.engines:
            films = []
            films = engine.search(name)
            # print [film['name'] for film in films]
            names = ', '.join([film['name'] for film in films]).decode('utf-8')
            # logging.info("search from %s: %s-%s", engine.SOURCE, name, names)
            results.extend(films)

        return self.merge_films(results)

    def save(self, film_list):
        print film_list
        for name, film in film_list.iteritems():
            key = "film:" + base64.b64encode(name)
            cache.set(key, json.dumps(film, ensure_ascii=False))

    def merge_films(self, results):
        film_dict = {}
        for r in results:
            if r['name'] in film_dict:
                film_dict[r['name']]['downlist'].extend(r['downlist'])
            else:
                film_dict[r['name']] = r
        return film_dict

    def start(self):
        import time

        while True:
            try:
                # 1. 读取需要搜索的电影名称
                name = self.fetch_next()
                if name is None:
                    continue

                try:
                    # 2. 依次启动个搜索引擎搜索，合并结果
                    result = self.do_search_engine(name)
                except:
                    if name is not None:
                        self.push(name)
                    raise

                # 3. 保存结果到redis
                self.save(result)
            except Exception as ex:
                logging.error(ex)

            time.sleep(0.5)


if __name__ == "__main__":
    StorageLoop().start()
