# -*- coding: utf-8 -*-
from model_i18n import set_do_autotrans


def autotranslate_view(fun):

    def wrap(*args, **kwargs):
        set_do_autotrans(False)
        resp = fun(*args, **kwargs)
        set_do_autotrans(True)
        return resp

    return wrap
