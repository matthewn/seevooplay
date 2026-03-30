from .base import *  # noqa F401

SECRET_KEY = 'django-insecure-test-key-not-for-production'

DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TIME_ZONE = 'UTC'
