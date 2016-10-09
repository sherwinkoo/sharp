# -*- coding: utf-8 -*-

import json
import base64

from redis import Redis

from utils import safe_utf8


class TaskManager(object):
    cache = Redis()

    def add(self, brief):
        import uuid
        task = dict(
            tid=uuid.uuid4().hex,
            data=brief)
        self.cache.rpush('movie:queue:wait', json.dumps(task))

    def next(self):
        task = self.cache.lpop('movie:queue:wait')
        if task:
            task = json.loads(task)
        return task

    def doing(self, task):
        self.cache.set('movie:doing:{}'.format(task['tid']), json.dumps(task))

    def done(self, task):
        self.cache.delete('movie:doing:{}'.format(task['tid']))
        self.cache.rpush('movie:queue:done', json.dumps(task))

    def status(self):
        tasks_waited_top10 = self.cache.lrange('movie:queue:wait', 0, 10)
        tasks_done_tail10 = self.cache.lrange('movie:queue:done', -10, -1)
        tasks_doing = self.cache.mget(self.cache.keys("movie:doing:*"))
        return {
            "waited": dict(
                count=self.cache.llen('movie:queue:wait'),
                top10=[json.loads(t) for t in tasks_waited_top10]),
            "doing": dict(
                count=len(tasks_doing),
                all=[json.loads(t) for t in tasks_doing]),
            "done": dict(
                count=self.cache.llen('movie:queue:done'),
                tail10=[json.loads(t) for t in tasks_done_tail10]),
        }


class MovieStorage(object):
    cache = Redis()

    def save_downlist(self, name, downlist):
        key = "film:" + base64.b64encode(safe_utf8(name))
        movie = self.cache.get(key)
        if movie:
            movie = json.loads(movie)
        else:
            movie = dict(name=name, downlist=[])

        down_urls = set([down['download_url'] for down in movie['downlist']])
        for down in downlist:
            if down['download_url'] in down_urls:
                continue
            movie['downlist'].append(down)

        self.cache.set(key, json.dumps(movie))
