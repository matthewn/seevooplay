from .base import *   # noqa F401
from .local import *  # noqa F401

if DEBUG:  # noqa F405
    INSTALLED_APPS = INSTALLED_APPS + ['django_extensions']  # noqa F405
