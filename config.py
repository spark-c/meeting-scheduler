# handles config / environment vars for meeting-scheduler

import os
basedir = os.path.abspath(os.path.dirname(__file__)) # this is a relative path from anywhere
                                                     # basedir is called, to this __file__

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'fluffington'
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql:///meeting-scheduler-dev'


class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'postgres:// ... '
    pass
