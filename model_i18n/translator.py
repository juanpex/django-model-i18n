# -*- coding: utf-8 -*-
import copy
import new

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_i18n import managers
from django.db import transaction

from model_i18n.conf import CURRENT_LANGUAGES, CURRENT_LANGUAGE, \
     ATTR_BACKUP_SUFFIX, MODEL_I18N_DJANGO_ADMIN
from model_i18n.exceptions import AlreadyRegistered
from model_i18n.managers import TransManager
from model_i18n.options import ModelTranslation
from model_i18n.utils import import_module, get_translation_opt


__all__ = ['register', 'ModelTranslation']


class Translator(object):
    """
    Manages all the site's multilingual models.
    """

    def __init__(self):
        self._registry = {}  # model_class class -> translation_class instance
        self._registry_admin = {}

    def register(self, master_model, translation_class=None, **options):
        if type(master_model) is str:
            app_path = ".".join(master_model.split(".")[:-1])
            master_module_models = import_module(app_path + '.models')
            master_model = getattr(master_module_models, master_model.split(".")[-1])
        if master_model in self._registry:
            raise AlreadyRegistered('The model "%s" has is already \
            registered for translation' % master_model.__name__)

        # If not translation_class given use default options.
        if not translation_class:
            translation_class = ModelTranslation

        # If we got **options then dynamically construct a
        # subclass of translation_class with those **options.
        if options:
            translation_class = type('%sTranslation' % \
            master_model.__name__, (translation_class,), options)

        # Validate the translation_class (just in debug mode).
        if settings.DEBUG:
            from model_i18n.validation import validate
            validate(translation_class, master_model)

        transmanager_class = type('%sTransManager' % master_model.__name__, (TransManager, master_model.objects.__class__,), {})
        try:
            livetransmanager_class = type('%sLiveTransManager' % master_model.__name__, (TransManager, master_model.live_objects.__class__,), {})
        except:
            livetransmanager_class = type('%sLiveTransManager' % master_model.__name__, (TransManager, master_model.objects.__class__,), {})

        master_model.add_to_class('_default_manager', TransManager())
        master_model.add_to_class('_base_manager', TransManager())
        master_model.add_to_class('objects', transmanager_class())
        master_model.add_to_class('live_objects', livetransmanager_class())

        opts = translation_class(master_model)

        # Set up master_model as a multilingual model
        # using translation_class options
        tmodel = self.create_translation_model(master_model, opts)
        tmodel.__unicode__ = lambda s: unicode(getattr(s, s._transmeta.master_field_name))
        defaults = {'blank': True, 'null': True, 'editable': False, 'related_name': '%(app_label)s_%(class)s_related'}
        m2mfield = models.ManyToManyField(tmodel, **defaults)
        master_model.add_to_class("translations", m2mfield)

        # This probably will become a class method soon.
        self.setup_master_model(master_model, tmodel)
        if MODEL_I18N_DJANGO_ADMIN:
            self._registry_admin[master_model] = tmodel

        # Register the multilingual model and the used translation_class.
        self._registry[master_model] = opts

    def create_translation_model(self, master_model, opts):
        attrs = {'__module__': master_model.__module__}

        if opts.master_language not in dict(settings.LANGUAGES):
            from model_i18n.exceptions import OptionWarning
            msg = '\nCode language "%s" not exist: Avaible languages are: %s.\n The model %s take master languages "%s"' % \
            (opts.master_language, " ".join(dict(settings.LANGUAGES).keys()), master_model.__name__, settings.MODEL_I18N_MASTER_LANGUAGE)
            print OptionWarning(msg)

        # creates unique_together for master_model
        trans_unique_together = []
        base_unique_together = \
            (opts.master_field_name, opts.language_field_name)
        trans_unique_together.append(base_unique_together)
        if master_model._meta.unique_together:
            for rule in master_model._meta.unique_together:
                trans_rule_fields = []
                for trans_rule_field in rule:
                    if trans_rule_field in opts.fields:
                        trans_rule_fields.append(trans_rule_field)
                nut = tuple(trans_rule_fields) + base_unique_together
                trans_unique_together.append(nut)

        class Meta:
            app_label = master_model._meta.app_label
            db_table = opts.db_table
            master_model._meta.unique_together
            unique_together = tuple(set(trans_unique_together))
        attrs['Meta'] = Meta

        class TranslationMeta:
            default_language = opts.default_language
            master_language = opts.master_language
            translatable_fields = opts.fields
            language_field_name = opts.language_field_name
            master_field_name = opts.master_field_name
            related_name = opts.related_name
            inlines = opts.inlines
        attrs['_transmeta'] = TranslationMeta
        opts.related_name = "parents"

        # Common translation model fields
        common_fields = {

            # Translation language
            opts.language_field_name: models.CharField(db_index=True,
                verbose_name=_('language'), max_length=10,
                choices=settings.LANGUAGES),

            # Master instance FK
            opts.master_field_name: models.ForeignKey(master_model, \
                db_index=True, verbose_name=_('master'), \
                related_name=opts.related_name),
        }
        attrs.update(common_fields)

        # Add translatable fields
        model_name = master_model.__name__ + 'Translation'
        for field in master_model._meta.fields:
            if field.name not in opts.fields:
                continue
            if field.name in common_fields:
                raise ImproperlyConfigured('%s: %s field name "%s" \
                    conflicts with the language or master FK common \
                    fields, try changing language_field_name or \
                    master_field_name ModelTranslation option.'
                    % (model_name, master_model.__name__, field.attname))
            newfield = copy.copy(field)
            newfield.primary_key = False

            attrs[newfield.name] = newfield
        # setup i18n languages on master model for easier access
        master_model.i18n_languages = settings.LANGUAGES
        master_model.i18n_default_language = opts.master_language
        master_model.i18n_instance_language = opts.master_language
        return type(model_name, (models.Model,), attrs)

    def setup_master_model(self, master_model, translation_model):
        master_model._translation_model = translation_model
        master_model.switch_language = switch_language
        master_model.save = trans_save(master_model.save)
        master_model.lang = lang

    def setup_manager(self, manager):
        # Backup get_query_set to use in translation get_query_set
        manager.get_query_set_orig = manager.get_query_set

        # Add translation methods into a manager instance
        for method_name in ('get_query_set', 'set_language'):
            im = new.instancemethod(getattr(managers, method_name))
            setattr(manager, method_name, im, manager, manager.__class__)


def trans_save(method):

    def wrapper(self, *args, **kwargs):
        obj = self
        values = kwargs.pop('values', {})
        delete = kwargs.pop('delete', False)
        if hasattr(self, 'current_language'):
            if self.current_language \
            and self.current_language != self.i18n_default_language:
                obj = i18n_save(obj, self.current_language, values, delete)
        else:
            obj = method(self, *args, **kwargs)
        return obj

    return wrapper


@transaction.commit_on_success
def i18n_save(instance, language, values={}, delete=False):
    if language not in dict(settings.LANGUAGES):
        raise ValueError(_('Incorrect language %(lang)s') % {'lang': language})

    master_language = get_translation_opt(instance, 'master_language')
    if language == master_language:
        return instance.save()
    trans_id = getattr(instance, 'id_%s' % language, None)
    if not trans_id and delete:
        # This objects has no translation to language "language"
        return
    if delete:
        instance._translation_model.objects.filter(id=trans_id).delete()
    else:
        return instance._translation_model.objects.filter(id=trans_id).update(**values)


def lang(instance, lang=None):
    if not instance:
        return instance
    if not lang:
        return instance
    setattr(instance, CURRENT_LANGUAGE, lang)
    return instance


def switch_language(instance, lang=None, default_if_None=None):
    """Here we overrides the default fields with their translated
    values. We keep the default if there's no value in the translated
    field or more than one language was requested.
        instance.switch_language('es')
            will load attribute values for 'es' language
        instance.switch_language()
            will load attribute values for master default language
    """
    current_languages = getattr(instance, CURRENT_LANGUAGES, None)
    current = getattr(instance, CURRENT_LANGUAGE, None)
    if current_languages:  # any translation?
        trans_meta = instance._translation_model._transmeta
        fields = trans_meta.translatable_fields
        if not lang or lang == trans_meta.master_language:  # use defaults
            for name in fields:
                value = getattr(instance, '_'.join((name, ATTR_BACKUP_SUFFIX)),
                                None)
                setattr(instance, name, value)
        elif lang in current_languages and lang != current:  # swtich language
            for name in fields:
                value = getattr(instance, '_'.join((name, lang)), default_if_None)
                value = value or default_if_None
                if value is not None:  # Ignore None, means not translated
                    setattr(instance, name, value)
        setattr(instance, CURRENT_LANGUAGE, lang)

# Just one Translator instance is needed.
_translator = Translator()


## API
def register(model, translation_class=None, **options):
    """ Register and set up `model` as a multilingual model. """
    return _translator.register(model, translation_class, **options)
