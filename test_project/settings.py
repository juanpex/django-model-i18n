# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join
import sys

LANGUAGES = (
  ('en', 'English'),
  ('es', 'Español'),
  ('fr', 'Français'),
)
LANGUAGE_CODE = 'en'

# translations settings

MODEL_I18N_CONF = 'test_project.i18n_conf'
MODEL_I18N_MASTER_LANGUAGE = LANGUAGE_CODE

PROJECT_DIR = dirname(abspath(__file__))
sys.path.append(join(PROJECT_DIR, 'apps'))
sys.path.append(join(PROJECT_DIR, '..'))

TEMPLATE_DIRS = (
    join(PROJECT_DIR, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'model_i18n',
    'app',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
)

MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/admin_media/'

ROOT_URLCONF = 'test_project.urls'

SECRET_KEY = '+h78sko_^A,k,sm77^s(CRGsL&^5laxR()/)&1&sw(290nm'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '%s/test_project.db' % PROJECT_DIR,
    }
}

TEST_DATABASE_CHARSET = "utf8"
TEST_DATABASE_COLLATION = "utf8_general_ci"

DATABASE_SUPPORTS_TRANSACTIONS = True

DEBUG = True
TEMPLATE_DEBUG = DEBUG

USE_I18N = True

CACHE_BACKEND = 'locmem:///'


try:
    from local_settings import *
except ImportError:
    pass
