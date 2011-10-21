# -*- coding: utf-8 -*-
from django.conf import settings
from django.views.i18n import set_language


def model_i18n_set_language(request):
    request.POST = request.REQUEST
    request.method = "POST"
    #try:
        #if 'django.contrib.messages' in settings.INSTALLED_APPS:
            #from django.contrib import messages
            #msg = "Change language to %s" % request.REQUEST.get('language')
            #messages.info(request, msg)
    #except Exception, e:
        #pass
    return set_language(request)
