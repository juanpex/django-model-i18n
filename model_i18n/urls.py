# -*- coding: utf-8 -*-
try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'model_i18n.views.model_i18n_set_language', name='setlang'),
)
