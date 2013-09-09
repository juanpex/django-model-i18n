# -*- coding: utf-8 -*-
import inspect
from django import VERSION as DJANGO_VERSION
from django.conf import settings
try:
    from django.conf.urls.defaults import patterns, url
except ImportError:
    from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.forms.models import modelform_factory, BaseInlineFormSet
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
from django import forms
from django.utils.safestring import mark_safe

from model_i18n.conf import CHANGE_TPL, CHANGE_TRANSLATION_TPL
from model_i18n.decorators import autotranslate_view
from model_i18n.utils import get_translation_opt


def get_django_version():
    return ".".join([str(v) for v in DJANGO_VERSION])


csrf_protect_m = method_decorator(csrf_protect)


class SpanWidget(forms.Widget):
    '''Renders a value wrapped in a <span> tag.

    Requires use of specific form support. (see ReadonlyForm
    or ReadonlyModelForm)
    '''

    use_post = False

    def render(self, name, value, attrs=None):
        original_value = value
        display_value = value
        try:
            original_value = self.original_value
            display_value = self.display_value
        except:
            pass
        final_attrs = self.build_attrs(attrs, name=name)
        fl_attrs = forms.util.flatatt(final_attrs)
        rep = u'<span%s >%s</span>' % (fl_attrs, display_value)
        if self.use_post:
            rep += u'<input type="hidden"%s value="%s" />' % (fl_attrs, original_value)
        return mark_safe(rep)

    def value_from_datadict(self, data, files, name):
        return self.original_value


class SpanPostWidget(SpanWidget):
    use_post = True


class SpanField(forms.Field):
    '''A field which renders a value wrapped in a <span> tag.

    Requires use of specific form support. (see ReadonlyForm
    or ReadonlyModelForm)
    '''

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', SpanWidget)
        super(SpanField, self).__init__(*args, **kwargs)


class Readonly(object):
    '''Base class for ReadonlyForm and ReadonlyModelForm which provides
    the meat of the features described in the docstings for those classes.
    '''

    readonly_default_value = '---'

    def __init__(self, *args, **kwargs):
        super(Readonly, self).__init__(*args, **kwargs)
        readonly = self.Meta.readonly
        if not readonly:
            return
        for name, field in self.fields.items():
            if name in readonly:
                field.widget = SpanWidget(attrs=field.widget.attrs)
            elif not isinstance(field, SpanField):
                continue
            display_value = self.readonly_default_value
            if hasattr(self.instance, 'get_%s_display' % name):
                display_value = getattr(self.instance, 'get_%s_display' % name)()
            else:
                try:
                    display_value = getattr(self.instance, name)
                except:
                    pass
            field.widget.original_value = display_value


def get_inline_instances_args(cls, request, obj=None):
    fun = getattr(cls, 'get_inline_instances')
    if len(inspect.getargspec(fun).args) > 2:
        return [request, obj]
    return [request]

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
        info = self.model._meta.app_label, self.model._translation_model._meta.module_name
        return urls[:-1] + patterns('',
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^(?P<object_id>.*)/(?P<language>[a-zA-Z]{2})/$',
                self.i18n_change_view, name="%s_add" % info[1]),
            # url(r'^(?P<object_id>.*)/(?P<language>[a-zA-Z]{2}-[a-zA-Z]{2})/$',
            #     self.i18n_change_view, name="%s_%s_add2" % info),
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
        args = {'_language': language.replace("-", ""), '_master': master}
        try:
            #object_id = model._meta.pk.to_python(object_id)
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
        if self.form and hasattr(self.form, 'declared_fields'):
            for field in list(self.form.declared_fields.keys()):
                if field not in fields:
                    self.form.declared_fields.pop(field)
        formfield_callback = curry(self.formfield_for_dbfield, request=request)
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": formfield_callback,
        }
        defaults.update(kwargs)
        f = modelform_factory(self.Tmodel, **defaults)
        f.clean = lambda s: s.cleaned_data
        return f

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
        for inline in self.get_inline_instances(*get_inline_instances_args(self, request, obj)):
            if not hasattr(inline.model, '_translation_model'):
                continue
            defaults = {
                'can_delete': False,
                'extra': 0,
                'form': self.get_inline_form(inline),
                'formset': self.get_inline_formset(inline),
            }
            yield inline.get_formset(request, obj, **defaults)

    def get_prepopulated_fields(self, request, *args, **kwargs):
        # FIX for 1.3
        superadmin = super(TranslationModelAdmin, self)
        if hasattr(superadmin, 'get_prepopulated_fields'):
            prepopulated_fields = superadmin.get_prepopulated_fields(request, *args, **kwargs)
        else:
            prepopulated_fields = self.prepopulated_fields
        translatable_fields = get_translation_opt(self.model, 'translatable_fields')
        for k, v in prepopulated_fields.items():
            if k not in translatable_fields or v not in translatable_fields:
                prepopulated_fields.pop(k)
        return prepopulated_fields

    def get_inline_instances(self, request, obj=None):
        # FIX for 1.3
        superadmin = super(TranslationModelAdmin, self)
        if hasattr(superadmin, 'get_inline_instances'):
            inline_instances = superadmin.get_inline_instances(*get_inline_instances_args(superadmin, request, obj))
        else:
            inline_instances = self.inline_instances
        inline_i18n_models = dict([(i18n_inline.model, i18n_inline) for i18n_inline in self.i18n_inlines])
        instances = []
        for inline in inline_instances:
            if inline.model in inline_i18n_models:
                if 'i18n/admin/edit_inline.html' != inline.template:
                    inline.base_template = unicode(inline.template)
                    inline.template = 'i18n/admin/edit_inline.html'
                instances.append(inline)
        return instances

    def get_form(self, request, obj=None, **kw):
        if self.lang:
            return self.get_i18n_form(request, obj, **kw)
        return super(TranslationModelAdmin, self).get_form(request, obj, **kw)

    def get_inline_formset(self, inline):

        class TransInlineFormSet(BaseInlineFormSet):

            def __init__(self, *args, **kwargs):
                super(TransInlineFormSet, self).__init__(*args, **kwargs)

            def get_queryset(self):
                qs = super(TransInlineFormSet, self).get_queryset()
                qs._default_if_None = ''
                return qs

        TransInlineFormSet.lang = self.lang

        return TransInlineFormSet

    def get_inline_form(self, inline):

        class TransInlineForm(inline.form):

            def __init__(self, *args, **kwargs):
                super(TransInlineForm, self).__init__(*args, **kwargs)
                for fn in self.fields:
                    if fn not in self.i18n_fields:
                        self.fields[fn].widget = SpanPostWidget()  # forms.HiddenInput()
                        if self.instance.pk:
                            val = getattr(self.instance, fn, '')
                            self.fields[fn].widget.original_value = val.pk if hasattr(val, 'pk') else val
                            self.fields[fn].widget.display_value = unicode(val)
                        # self.fields[fn].widget.attrs['READONLY'] = 'READONLY'
                        # choices = getattr(self.fields[fn].widget, 'choices', None)
                        # if choices and 'instance' in kwargs:
                        #     val = getattr(kwargs['instance'], fn, '')
                        #     choices = [(k, v) for k,v in dict(choices).items() if k == val]
                        #     self.fields[fn].widget.choices = choices
                        # else:
                        #     self.fields[fn].widget.attrs['DISABLED'] = 'DISABLED'

            def save(self, *args, **kwargs):
                kwargs['commit'] = False
                obj = super(TransInlineForm, self).save(*args, **kwargs)
                Tmodel = obj.__class__._translation_model
                defaults = {
                    '_master': self.instance,
                    '_language': self.lang.replace("-", "")
                }
                try:
                    aux = Tmodel.objects.get(**defaults)
                except Tmodel.DoesNotExist:
                    aux = Tmodel(**defaults)
                trans_meta = self.instance._translation_model._transmeta
                fields = trans_meta.translatable_fields
                for name in fields:
                    value = getattr(obj, name, None)
                    if not value is None:
                        setattr(aux, name, value)
                aux.save()
                self.instance.translations.add(aux)
                return aux

        TransInlineForm.lang = self.lang
        TransInlineForm.i18n_fields = get_translation_opt(inline.model, 'translatable_fields')

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
                                       self.get_inline_instances(*get_inline_instances_args(self, request, new_object))):
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
                    self.get_inline_instances(*get_inline_instances_args(self, request, Tobj))):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                formset = FormSet(instance=Tobj._master, prefix=prefix,
                                  queryset=None)
                formsets.append(formset)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        def get_prepopulated_fields_inline(inline, request):
            # FIX for 1.3
            if hasattr(inline, 'get_prepopulated_fields'):
                prepopulated_fields = inline.get_prepopulated_fields(request)
            else:
                prepopulated_fields = inline.prepopulated_fields
            translatable_fields = get_translation_opt(inline.model, 'translatable_fields')
            for k, v in prepopulated_fields.items():
                if k not in translatable_fields or v not in translatable_fields:
                    prepopulated_fields.pop(k)
            return prepopulated_fields

        inline_admin_formsets = []
        for inline, formset in zip(self.get_inline_instances(*get_inline_instances_args(self, request, obj)), formsets):
            if not hasattr(inline.model, '_translation_model'):
                continue
            fieldsets = list(inline.get_fieldsets(request))
            readonly = list(inline.get_readonly_fields(request))
            prepopulated = dict(get_prepopulated_fields_inline(inline, request))
            inline_kwargs = {}
            # FIX for 1.3
            if '1.4' in get_django_version():
                inline_kwargs['model_admin'] = self
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, prepopulated, readonly, **inline_kwargs)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        translated_fields = []
        for f in obj._translation_model._transmeta.translatable_fields:
            try:
                v = getattr(obj, '_'.join((f, 'master')))
            except:
                v = getattr(obj, f,)
            v = v or ''
            if hasattr(v, 'replace'):
                v = v.replace("'", "&#39;").replace('"', "&quot;")
                v = v.replace('\r', '')
                v = v.replace('\n', '<br>')
            translated_fields.append((f, v))

        context = {
            'title':  _('Translation %s') % force_unicode(opts.verbose_name),
            'tiny_mce': True,
            'adminform': adminForm, 'original': obj,
            'translated_fields': translated_fields, 'master_language': master_language,
            'is_popup': ('_popup' in request.REQUEST),
            'errors': admin.helpers.AdminErrorList(form, []),
            #'root_path': self.admin_site.root_path,
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
        change_form_template = [
            "admin/%s/%s/change_form.html" % (opts.app_label, opts.object_name.lower()),
            CHANGE_TRANSLATION_TPL,
            "admin/%s/change_form.html" % opts.app_label,
            "admin/change_form.html",
        ]
        return render_to_response(change_form_template, context, context_instance=ctx)
