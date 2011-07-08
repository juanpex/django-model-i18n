# -*- coding: utf-8 -*-
"""
Functions on this module are added to every manager on each multilingual model.
"""
from model_i18n.query import TransQuerySet
from model_i18n.conf import MULTIDB_SUPPORT
from model_i18n import get_do_autotrans

from django.utils.translation import get_language

def get_query_set(self):
    """ Adds TransQuerySet support """
    qs = self.get_query_set_orig()
    kwargs = {'query': qs.query}
    # Pass DB attribute if multi-db support is present.
    if MULTIDB_SUPPORT:
        kwargs['using'] = qs._db
    queryset = TransQuerySet(self.model, **kwargs)
    if get_do_autotrans():
        queryset = queryset.set_language(get_language()[:2])
    return queryset


def set_language(self, language_code):
    """ Sets the current language """
    return self.get_query_set().set_language(language_code[:2])
