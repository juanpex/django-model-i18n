=================
django-model-i18n
=================

django-model-i18n is a django application that tries to make multilingual data in models less painful.

The main features/goals are:

* Easy installation and integration. No data or schema migration pain.
* Each multilingual model stores it's translations in a separate table, which from django is just a new model dynamically created, we call this model the translation model.
* You can add (or even drop) i18n support for a model at any time and you won't need to migrate any data or affect the original model (we call this the master model) table definition. This allows you to develop your apps without thinking in the i18n part (you even can load data for the main language and you won't need to migrate it) and when you are comfortable with it register the multilingual options and start working with the content translations.
* 3rd party apps friendly. You can add i18n support to the existing models without modifying their definition at all (think in apps you can't modify directly for example djago.contrib.flatpages).

Installation
===========

* cloning repository

Configuration
=============

Go to urls.py into root project directory and put this

    from model_i18n import loaders

    loaders.autodiscover_admin()

also add 'django.middleware.locale.LocaleMiddleware' into MIDDLEWARE_CLASSES::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        ## IF CACHE MIDDLEWARE IS SETTING PUT HERE
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    )

and finally put in INSTALLED_APPS::

    INSTALLED_APPS = (
        'model_i18n',
        ...
        'django.contrib.admin',
        ...
    )

**When putting model_i18n must be first in the list of INSTALLED_APPS.**


Usage
=====

1) In the directory of the application create a translations.py
2) Inside the file you need to register translations like this example::

    from model_i18n import translator
    from app.models import Item

    class ItemTranslation(translator.ModelTranslation):
        fields = ('title',)

    translator.register(Item, ItemTranslation)

Translations may also be recorded in this way

    from model_i18n import translator

    class ItemTranslation(translator.ModelTranslation):
        fields = ('title',)

    translator.register('app.models.Item', ItemTranslation)


Notes
=====

If you will translate models that are into django.contrib.* such as flatpages
put this on settings:

    TRANSLATED_APP_MODELS['django.contrib.flatpages'] = {
        'FlatPage': {
        'fields': ('title', 'content'),
        'master_language': 'es',
        }
    }

and if you need use south you must use SOUTH_MIGRATION_MODULES setting like this::

    SOUTH_MIGRATION_MODULES  = {
            'flatpages': 'migrations.flatpages'
        }


It has good integration with django.contib.admin. It automatically configures ModelAdmin and inlines that apply.

API EXAMPLES
============

Filtering
---------

    Item.objects.set_language("es").filter(translations__title__contains='sometext')
    items = Item.objects.filter(Q(translations___language='en') | Q(translations___language='es'))

    items = items.exclude(category__name='stuff')
    items = items.filter(Q(title__icontains='book') | Q(translations__title__icontains='toy'))


Updating
---------
    Item.objects.set_language("es").filter(translations__title__contains='sometext').update(title=u'new text')

Deleting
---------
    Item.objects.set_language("fr").filter(translations__title__contains='titres à éliminer').delete()


Currently the project test_project has some simple tests.




