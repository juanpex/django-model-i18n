# -*- coding: utf-8 -*-
import inspect
from threading import local

from django.db.models.manager import signals

import patches


VERSION = (0, 4, 0, 'alpha', 0)
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


def ensure_models(**kwargs):
    stack = inspect.stack()
    for stack_info in stack[1:]:
        if '_load_conf' in stack_info[3]:
            return
    from model_i18n import loaders
    loaders.autodiscover()


if hasattr(signals, 'installed_apps_loaded'):
    def installed_apps_loaded(**kwargs):
        ensure_models()

    signals.installed_apps_loaded.connect(installed_apps_loaded)
else:
    ensure_models()
