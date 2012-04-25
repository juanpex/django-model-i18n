# -*- coding: utf-8 -*-
from django.views.i18n import set_language


def model_i18n_set_language(request):
    request.POST = request.REQUEST
    request.method = "POST"
    return set_language(request)
