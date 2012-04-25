# -*- coding: utf-8 -*-
from os.path import abspath, dirname, join
import django
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
sys.path.append(PROJECT_DIR)
sys.path.append(join(PROJECT_DIR, '..'))
sys.path.append(join(PROJECT_DIR, 'apps'))


SOUTH_TESTS_MIGRATE = False

TEMPLATE_DIRS = (
    join(PROJECT_DIR, "templates"),
)

INSTALLED_APPS = (
    'model_i18n',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'app',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Context Processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)


MIDDLEWARE_CLASSES += ('django.middleware.locale.LocaleMiddleware',)
TEMPLATE_CONTEXT_PROCESSORS += ('django.core.context_processors.i18n',)

if 'django.contrib.messages' in INSTALLED_APPS:
    TEMPLATE_CONTEXT_PROCESSORS += \
        ('django.contrib.messages.context_processors.messages',)
    MIDDLEWARE_CLASSES += \
        ('django.contrib.messages.middleware.MessageMiddleware',)

MEDIA_ROOT = PROJECT_DIR + '/media/'

MEDIA_URL = '/media/'

STATIC_ROOT = PROJECT_DIR + '/static/'

STATIC_URL = '/static/'

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

PYTHON_VERSION = '%s.%s' % sys.version_info[:2]
DJANGO_VERSION = django.get_version()

JUNIT_OUTPUT_DIR = join(
    PROJECT_DIR,
    '..',
    'junit-dj%s-py%s' % (DJANGO_VERSION, PYTHON_VERSION)
)

try:
    from local_settings import *
except ImportError:
    NEW_INSTALLED_APPS = ()
    NEW_MIDDLEWARE_CLASSES = ()
    NEW_TEMPLATE_CONTEXT_PROCESSORS = ()

INSTALLED_APPS += NEW_INSTALLED_APPS
MIDDLEWARE_CLASSES += NEW_MIDDLEWARE_CLASSES
TEMPLATE_CONTEXT_PROCESSORS += NEW_TEMPLATE_CONTEXT_PROCESSORS
