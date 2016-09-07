from __future__ import print_function

import os
from os.path import dirname, abspath

CONF_DIR = dirname(dirname(abspath(__file__)))
BASE_DIR = dirname(CONF_DIR)
CONF_DIR_NAME = os.path.relpath(BASE_DIR, CONF_DIR)

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = 'y&-@_e)08kzk711q0qqrklqj^0%d%0z&s5#s9qj!be&i*w+hra'


# Password validation

AUTH_PASSWORD_VALIDATORS = []


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'sqlite3.db'),
    }
}

# Time zone

TIME_ZONE = 'Asia/Kolkata'
