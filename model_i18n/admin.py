# -*- coding: utf-8 -*-
import warnings

try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url


from model_i18n.conf import CHANGE_TPL
from model_i18n.exceptions import OptionWarning


def setup_admin(master_model, translation_model, adminsite):
    """
    Setup django.contrib,admin support.
    """
    madmin = adminsite._registry.get(master_model)

    # if app not define modeladmin exit setup
    if not madmin:
        return

    if madmin.change_form_template:
        # default change view is populated with links to i18n edition
        # sections but won't be available if change_form_template is
        # overrided on model admin options, in such case, extend from
        # model_i18n/template/change_form.html
        msg = '"%s" overrides change_form_template, \
        extend %s to get i18n support' % (madmin, CHANGE_TPL)
        warnings.warn(OptionWarning(msg))

    from model_i18n.admin_helpers import TranslationModelAdmin

    maclass = madmin.__class__

    options = get_options_base_fields(maclass)

    admintranslation_class = type('%sTranslationAdmin' % \
            master_model.__name__, (TranslationModelAdmin, madmin.__class__), options)

    adminsite.unregister(master_model)
    adminsite.register(master_model, admintranslation_class)
    madmin = adminsite._registry.get(master_model)
    maclass = madmin.__class__

    trans_inlines = madmin.inlines
    if not trans_inlines:
        return

    for i in madmin.inlines:
        if i.model in [t.model for t in trans_inlines]:
            inline_base_class = i.__bases__[0]
            options = {
                'model': i.model
            }
            iac = type("%sTranslator" % (i.__name__), (inline_base_class,), options)
            maclass.i18n_inlines.append(iac)

    for iclass in maclass.i18n_inlines:
        inline_instance = iclass(master_model._translation_model, adminsite)
        maclass.i18n_inline_instances.append(inline_instance)

    return
    adminsite.unregister(master_model)
    adminsite.register(master_model, madmin)


def get_options_base_fields(base):
    attr_names = [
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
    ]
    for attr in dict(base.__dict__):
        if not attr in attr_names and not attr in ('__module__', '__doc__', 'media', 'prepopulated_fields'):
            attr_names.append(attr)

    options = {}
    for attr in attr_names:
        options[attr] = getattr(base, attr)
    return options


def get_urls(instance):
    # original urls
    urls = instance.get_urls_orig()
    return urls[:-1] + patterns('',
                url(r'^(?P<obj_id>\d+)/(?P<language>[a-z]{2})/$',
                    instance.i18n_change_view),
                    url(r'^(?P<obj_id>\d+)/(?P<language>[a-z]{2}-[a-z]{2})/$',
                    instance.i18n_change_view),
                urls[-1])
