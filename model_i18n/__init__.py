# -*- coding: utf-8 -*-
import inspect
from threading import local

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import patches
from utils import import_module


VERSION = (0, 2, 1, 'alpha', 0)
_active = local()


def get_version():
    """ Returns application version """
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    if VERSION[3:] == ('alpha', 0):
        version = '%s pre-alpha' % version
    else:
        if VERSION[3] != 'final':
            version = '%s %s %s' % (version, VERSION[3], VERSION[4])
    return version


def get_do_autotrans():
    return getattr(_active, "value", True)


def set_do_autotrans(v):
    _active.value = v

# def singleton(cls):
#     instances = {}
#     def getinstance():
#         if cls not in instances:
#             instances[cls] = cls()
#         return instances[cls]
#     return getinstance

def _load_conf(*args, **kwargs):
        
        """
        Ensures the configuration module gets
        imported when importing model_i18n.
        """
        # This is an idea from haystack app. We need to run the code that
        # follows only once, no matter how many times the main module is imported.
        # We'll look through the stack to see if we appear anywhere and simply
        # return if we do, allowing the original call to finish.
        stack = inspect.stack()
        for stack_info in stack[1:]:
            if '_load_conf' in stack_info[3]:
                return

        if not hasattr(settings, 'MODEL_I18N_CONF'):
            raise ImproperlyConfigured('You must define the MODEL_I18N_CONF \
            setting, it should be a python module path string, \
            for example "myproject.i18n_conf"')
        if not hasattr(settings, 'MODEL_I18N_MASTER_LANGUAGE'):
            raise ImproperlyConfigured('You must define the \
            MODEL_I18N_MASTER_LANGUAGE setting.')

        if settings.MODEL_I18N_CONF and settings.USE_I18N:
            # Import config module
            import_module(settings.MODEL_I18N_CONF)

_load_conf()

# #@singleton
# class ConfLoader(object):

#     _counter = 0

#     def __call__(self):
#         self._load_conf()
#         self._counter += 1
#         print self._counter

#     def _load_conf(self, **kwargs):
        
#         """
#         Ensures the configuration module gets
#         imported when importing model_i18n.
#         """
#         # This is an idea from haystack app. We need to run the code that
#         # follows only once, no matter how many times the main module is imported.
#         # We'll look through the stack to see if we appear anywhere and simply
#         # return if we do, allowing the original call to finish.
#         # stack = inspect.stack()
#         # for stack_info in stack[0:]:
#         #     if '_load_conf' in stack_info[3]:
#         #         return

#         if not hasattr(settings, 'MODEL_I18N_CONF'):
#             raise ImproperlyConfigured('You must define the MODEL_I18N_CONF \
#             setting, it should be a python module path string, \
#             for example "myproject.i18n_conf"')
#         if not hasattr(settings, 'MODEL_I18N_MASTER_LANGUAGE'):
#             raise ImproperlyConfigured('You must define the \
#             MODEL_I18N_MASTER_LANGUAGE setting.')

#         if settings.MODEL_I18N_CONF and settings.USE_I18N:
#             # Import config module
#             import_module(settings.MODEL_I18N_CONF)


# conf = ConfLoader()
# conf()



# from django.db.models.manager import signals

# def ensure_models(sender, **kwargs):

#     from model_i18n import loaders
#     loaders.autodiscover()

# signals.class_prepared.connect(ensure_models)
