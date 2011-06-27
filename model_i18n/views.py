# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.utils.translation import check_for_language

from django.views.i18n import set_language


def model_i18n_set_language(request):
    request.POST = request.REQUEST
    request.method = "POST"
    try:
        from django.contrib import messages
        messages.info(request, "Change language to %s" % request.REQUEST.get('language'))
    except:
        pass
    return set_language(request)
