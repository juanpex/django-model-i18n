# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib import admin

from model_i18n.conf import CHANGE_TPL
from model_i18n.exceptions import OptionWarning
from model_i18n.utils import get_translation_opt


def setup_admin(master_model, translation_model):
    """
    Setup django.contrib,admin support.
    """
    madmin = admin.site._registry.get(master_model)

    # if app not define modeladmin exit setup
    if not madmin:
        return

    maclass = madmin.__class__
    if madmin.change_form_template:
        # default change view is populated with links to i18n edition
        # sections but won't be available if change_form_template is
        # overrided on model admin options, in such case, extend from
        # model_i18n/template/change_form.html
        msg = '"%s" overrides change_form_template, \
        extend %s to get i18n support' % (maclass, CHANGE_TPL)
        warnings.warn(OptionWarning(msg))

    from model_i18n.admin_helpers import TranslationModelAdmin

    TranslationModelAdmin = copy_base_fields(maclass, TranslationModelAdmin)

    admin.site.unregister(master_model)
    admin.site.register(master_model, TranslationModelAdmin)
    madmin = admin.site._registry.get(master_model)
    maclass = madmin.__class__

    trans_inlines = get_translation_opt(master_model, 'inlines')
    if not trans_inlines:
        return

    for i in madmin.inlines:
        if i.model in [t.model for t in trans_inlines]:
            inline_base_class = i.__bases__[0]
            iac = type("%sTranslator" % (i.__name__), (inline_base_class,), {})
            inline_admin_class = iac
            inline_admin_class.model = i.model
            maclass.i18n_inlines.append(inline_admin_class)

    for iclass in maclass.i18n_inlines:
        inline_instance = iclass(master_model._translation_model, admin.site)
        maclass.i18n_inline_instances.append(inline_instance)


def copy_base_fields(base, admin):
    attr_names = (
    'list_display',
    'list_display_links',
    'list_filter',
    'list_select_related',
    'list_per_page',
    'list_editable',
    'search_fields',
    'date_hierarchy',
    'save_as',
    'save_on_top',
    'ordering',
    'inlines',
    'add_form_template',
    'change_list_template',
    'delete_confirmation_template',
    'delete_selected_confirmation_template',
    'object_history_template',
    'actions',
    'action_form',
    'actions_on_top',
    'actions_on_bottom',
    'actions_selection_counter',
    'fieldsets'
    )
    for attr in attr_names:
        setattr(admin, attr, getattr(base, attr))
    return admin


def get_urls(instance):
    # original urls
    urls = instance.get_urls_orig()
    return urls[:-1] + patterns('',
                url(r'^(?P<obj_id>\d+)/(?P<language>[a-z]{2})/$',
                    instance.i18n_change_view),
                urls[-1])
