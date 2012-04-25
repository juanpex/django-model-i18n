# -*- coding: utf-8 -*-
"""
Functions on this module are added to every manager on each multilingual model.
"""
from django.db import models
from django.utils.translation import get_language

from model_i18n.query import TransQuerySet
from model_i18n.conf import MULTIDB_SUPPORT, DEFAULT_TRANS_MANAGER
from model_i18n import get_do_autotrans


try:
    if callable(DEFAULT_TRANS_MANAGER):
        class_default_managers = DEFAULT_TRANS_MANAGER()
    else:
        class_default_managers = DEFAULT_TRANS_MANAGER or models.Manager
except Exception, e:
    class_default_managers = models.Manager


class TransManager(class_default_managers):

    use_for_related_fields = True

    def get_query_set(self):
        """ Adds TransQuerySet support """
        qs = super(TransManager, self).get_query_set()
        kwargs = {'query': qs.query}
        # Pass DB attribute if multi-db support is present.
        if MULTIDB_SUPPORT:
            kwargs['using'] = qs._db
        queryset = TransQuerySet(self.model, **kwargs)
        if get_do_autotrans():
            queryset = queryset.set_language(get_language().replace("-", ""))
        if hasattr(queryset, 'prefetch_related'):
            queryset = queryset.prefetch_related()
        return queryset

    def set_language(self, language_code):
        """ Sets the current language """
        return self.get_query_set().set_language(language_code.replace("-", ""))
