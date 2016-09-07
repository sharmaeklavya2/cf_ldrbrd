from __future__ import print_function

import os
from os.path import dirname, abspath

CONF_DIR = dirname(dirname(abspath(__file__)))
BASE_DIR = dirname(CONF_DIR)
CONF_DIR_NAME = os.path.relpath(BASE_DIR, CONF_DIR)

DEBUG = True
ALLOWED_HOSTS = ['*']
SECRET_KEY = os.environ["SECRET_KEY"]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Database

import dj_database_url
db_from_env = dj_database_url.config()
DATABASES = {'default': db_from_env}

# Time zone

TIME_ZONE = 'Asia/Kolkata'
