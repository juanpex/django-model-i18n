# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'model_i18n.views.model_i18n_set_language', name='setlang'),
)
