# -*- coding: utf-8 -*-

DEBUG = False

SQLALCHEMY_DATABASE_URI = ''
SQLALCHEMY_TRACK_MODIFICATIONS = True

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_IMPORTS = ('backend.tasks', )
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']


POSTER_DIR = 'backend/static/posters'

from local_settings import *   # NOQA E402
