# -*- coding: utf-8 -*-


def model_i18n_set_language(request):
    from django.views.i18n import set_language
    from django.conf import settings
    request.POST = request.REQUEST
    request.method = "POST"
    try:
        if 'django.contrib.messages' in settings.INSTALLED_APPS:
            from django.contrib import messages
            msg = "Change language to %s" % request.REQUEST.get('language')
            messages.info(request, msg)
    except:
        pass
    return set_language(request)
