"WSGI config: It exposes the WSGI callable as a module-level variable named ``application``."

import os
from os.path import dirname, abspath

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

CONF_DIR = dirname(abspath(__file__))
BASE_DIR = dirname(CONF_DIR)
CONF_DIR_NAME = os.path.relpath(CONF_DIR, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", CONF_DIR_NAME + ".settings")
application = get_wsgi_application()
application = DjangoWhiteNoise(get_wsgi_application())
