# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.forms.models import modelform_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.encoding import force_unicode
from django.utils.functional import curry
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from model_i18n.conf import CHANGE_TPL, CHANGE_TRANSLATION_TPL
from model_i18n.decorators import autotranslate_view
from model_i18n.utils import get_translation_opt

csrf_protect_m = method_decorator(csrf_protect)


class TranslationModelAdmin(admin.ModelAdmin):

    lang = None
    change_form_template = CHANGE_TPL
    i18n_inline_instances = []
    i18n_inlines = []
    Tmodel = None

    def __init__(self, *args, **kw):
        super(TranslationModelAdmin, self).__init__(*args, **kw)
        self.Tmodel = self.model._translation_model

    def get_urls(self):
        urls = super(TranslationModelAdmin, self).get_urls()
        return urls[:-1] + patterns('',
            url(r'^(?P<object_id>\d+)/(?P<language>[a-z]{2})/$',
                self.i18n_change_view),
            urls[-1])

    @autotranslate_view
    def add_view(self, *args, **kw):
        self.lang = None
        return super(TranslationModelAdmin, self).add_view(*args, **kw)

    @autotranslate_view
    def change_view(self, *args, **kw):
        self.lang = None
        return super(TranslationModelAdmin, self).change_view(*args, **kw)

    @autotranslate_view
    def changelist_view(self, *args, **kw):
        self.lang = None
        return super(TranslationModelAdmin, self).changelist_view(*args, **kw)

    def i18n_queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = self.Tmodel._default_manager.get_query_set()
        # TODO: this should be handled by some parameter to the ChangeList.
        # otherwise we might try to *None, which is bad ;)
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_i18n_object(self, request, object_id, master, language):
        """
        Returns an instance matching the primary key provided. ``None``  is
        returned if no match is found (or the object_id failed validation
        against the primary key field).
        """
        queryset = self.i18n_queryset(request)
        model = queryset.model
        args = {'_language': language, '_master': master}
        try:
            object_id = model._meta.pk.to_python(object_id)
            return queryset.get(**args)
        except (model.DoesNotExist, ValidationError):
            return self.Tmodel(**args)

    def get_i18n_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        fields = get_translation_opt(self.model, 'translatable_fields')
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        formfield_callback = curry(self.formfield_for_dbfield, request=request)
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": formfield_callback,
        }
        defaults.update(kwargs)
        return modelform_factory(self.Tmodel, **defaults)

    def get_formsets(self, request, obj=None):
        if self.lang:
            return self.get_i18n_formsets(request, obj)
        return super(TranslationModelAdmin, self).get_formsets(request, obj)

    def get_fieldsets(self, request, obj=None):
        if self.lang:
            form = self.get_form(request, obj)
            fields = form.base_fields.keys()
            return [(None, {'fields': fields})]
        return super(TranslationModelAdmin, self).get_fieldsets(request, obj)

    def get_i18n_formsets(self, request, obj=None):
        for inline in self.get_inline_instances():
            defaults = {
                'can_delete': False,
                'extra': 0,
                'form': self.get_inline_form(inline)
            }
            yield inline.get_formset(request, obj, **defaults)

    def get_inline_instances(self):
        return [inline for inline in \
        self.inline_instances if inline.model in \
        [i18n_inline.model for i18n_inline in self.i18n_inlines]]

    def get_form(self, request, obj=None, **kw):
        if self.lang:
            return self.get_i18n_form(request, obj, **kw)
        return super(TranslationModelAdmin, self).get_form(request, obj, **kw)

    def get_inline_form(self, inline):
        class TransInlineForm(inline.form):

            def save(self, *args, **kwargs):
                kwargs['commit'] = False
                obj = super(TransInlineForm, self).save(*args, **kwargs)
                Tmodel = obj.__class__._translation_model
                defaults = {
                    '_master': self.instance,
                    '_language': self.lang
                }
                try:
                    aux = Tmodel.objects.get(**defaults)
                except Tmodel.DoesNotExist:
                    aux = Tmodel(**defaults)
                trans_meta = self.instance._translation_model._transmeta
                fields = trans_meta.translatable_fields
                for name in fields:
                    value = getattr(obj, name, None)
                    if value:
                        setattr(aux, name, value)
                aux.save()
                self.instance.translations.add(aux)
                return aux

        TransInlineForm.lang = self.lang
        return TransInlineForm

    @csrf_protect_m
    @transaction.commit_on_success
    @never_cache
    def i18n_change_view(self, request, object_id, language, extra=None):
        "The 'change' admin view for this model."
        cur_language = translation.get_language()
        translation.activate(language)
        model = self.model
        opts = model._meta
        self.lang = language

        obj = self.get_object(request, unquote(object_id))

        Tobj = self.get_i18n_object(request, unquote(object_id), obj, language)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        master_language = get_translation_opt(self.model, 'master_language')
        if language == master_language:
            # redirect to instance admin on default language
            return HttpResponseRedirect('../')

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r \
            does not exist.') % {'name': force_unicode(opts.verbose_name), \
            'key': escape(object_id)})

        if language not in dict(settings.LANGUAGES):
            raise Http404(_('Incorrect language %(l)s') % {'l': language})

        ModelForm = self.get_form(request, Tobj)
        formsets = []
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=Tobj)
            if form.is_valid():
                form_validated = True
                new_object = self.save_form(request, form, change=True)
            else:
                form_validated = False
                new_object = Tobj
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request, new_object),
                                       self.get_inline_instances()):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(request.POST, request.FILES,
                                  instance=new_object._master, prefix=prefix,
                                  queryset=inline.queryset(request))
                formsets.append(formset)

            all_valid = True
            for fs in formsets:
                if not fs.is_valid():
                    all_valid = False

            if all_valid and form_validated:
                self.save_model(request, new_object, form, change=True)
                form.save_m2m()
                for formset in formsets:
                    self.save_formset(request, form, formset, change=True)

                change_message = \
                self.construct_change_message(request, form, formsets)
                self.log_change(request, new_object, change_message)
                self.lang = None
                return self.response_change(request, new_object)

        else:
            form = ModelForm(instance=Tobj)
            prefixes = {}
            for FormSet, inline in \
                zip(self.get_formsets(request, Tobj._master), \
                    self.get_inline_instances()):

                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=Tobj._master, prefix=prefix,
                                  queryset=None)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj),
            self.prepopulated_fields, self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.get_inline_instances(), formsets):
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title':  _('Translation %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm, 'original': obj,
            'is_popup': ('_popup' in request.REQUEST),
            'errors': admin.helpers.AdminErrorList(form, []),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label, 'trans': True, 'lang': language,
            'current_language': dict(settings.LANGUAGES)[language],
            'inline_admin_formsets': inline_admin_formsets,
            # override some values to provide an useful template
            'add': False, 'change': True,
            'has_change_permission_orig': True,  # backup
            'has_add_permission': False, 'has_change_permission': False,
            'has_delete_permission': False,  # hide delete link for now
            'has_file_field': True, 'save_as': False, 'opts': self.model._meta,
        }
        translation.activate(cur_language)
        self.lang = None
        ctx = RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(CHANGE_TRANSLATION_TPL, context,
                                  context_instance=ctx)
