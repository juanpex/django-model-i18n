# -*- coding: utf-8 -*-
import inspect
from threading import local

VERSION = (0, 5, 1, 'alpha', 0)

# Dynamically calculate the version based on VERSION tuple
if len(VERSION) > 2 and VERSION[2] is not None:
    if isinstance(VERSION[2], int):
        str_version = "%s.%s.%s" % VERSION[:3]
    else:
        str_version = "%s.%s_%s" % VERSION[:3]
else:
    str_version = "%s.%s" % VERSION[:2]

__version__ = str_version

_active = local()


def get_do_autotrans():
    return getattr(_active, "value", True)


def set_do_autotrans(v):
    _active.value = v


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


def ensure_models(**kwargs):
    stack = inspect.stack()
    for stack_info in stack[1:]:
        if '_load_conf' in stack_info[3]:
            return
    from model_i18n import loaders
    loaders.autodiscover()


try:
    from django.db.models.manager import signals
    import patches

    if hasattr(signals, 'installed_apps_loaded'):
        def installed_apps_loaded(**kwargs):
            ensure_models()

        signals.installed_apps_loaded.connect(installed_apps_loaded)
    else:
        ensure_models()
except:
    pass
