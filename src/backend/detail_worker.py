# -*- coding: utf-8 -*-

import logging

from storage import TaskManager
from storage import MovieStorage

from xunbo import XunboHandler


class MainLoop(object):

    def __init__(self):
        self.engines = [
            XunboHandler(),
        ]
        self.task_manager = TaskManager()
        self.storage = MovieStorage()

    def _get_engine(self, brief):
        import urlparse
        domain = urlparse.urlparse(brief['detail_url']).hostname
        engine = filter(lambda e: e.DOMAIN == domain, self.engines)
        if not engine:
            logging.error("ENGINE NOT FOUND: %s", brief['detail_url'])
            return None
        return engine[0]

    def do_search_engine(self, brief):
        name = brief['name']
        detail_url = brief['detail_url']
        if isinstance(name, str):
            name = name.decode('utf-8')

        engine = self._get_engine(brief)
        info = engine.detail(name, detail_url)

        return info

    def start(self):
        import time

        while True:
            try:
                # 1. 读取需要搜索的电影名称
                task = self.task_manager.next()
                if task is None:
                    time.sleep(1)
                    continue

                try:
                    # 2. 依次启动个搜索引擎搜索，合并结果
                    brief = task['data']
                    self.task_manager.doing(task)
                    detail = self.do_search_engine(brief)

                    # 3. 保存结果到redis
                    self.storage.save_detail(brief['name'], detail)
                    self.task_manager.done(task)
                except:
                    self.task_manager.add(brief)
                    raise

            except Exception as ex:
                raise
                logging.error(ex)

            time.sleep(0.5)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
    )
    MainLoop().start()
