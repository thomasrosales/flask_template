import os
from os import environ, path
from dotenv import load_dotenv


BASEDIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASEDIR, '.env'))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
    JWT_HEADER_TYPE = os.getenv('JWT_HEADER_TYPE')
    SESSION_COOKIE_DOMAIN = os.getenv('SESSION_COOKIE_DOMAIN')
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_BLACKLIST_ENABLED = os.getenv('JWT_BLACKLIST_ENABLED')
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS') or [
        'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']


class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    TESTING = False


class DevelopmentConfig(Config):
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_ENV = os.getenv('FLASK_ENV')
    DEBUG = os.getenv('DEBUG')
    SERVER_NAME = os.getenv('SERVER_NAME')


class TestingConfig(Config):
    DEBUG = True
