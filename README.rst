django-model-i18n
=================

django-model-i18n is a django application that tries to make multilingual data in models less painful.

The main features/goals are:

* Easy installation and integration. No data or schema migration pain.
* Each multilingual model stores its translations in a separate table, which from django is just a new model dynamically created, we call this model the translation model.
* You can add (or even drop) i18n support for a model at any time and you won't need to migrate any data or affect the original model (we call this the master model) table definition. This allows you to develop your apps without thinking about i18n (you even can load data for the main language and you won't need to migrate it) and when you are comfortable with it register the multilingual options and start working with the content translations.
* 3rd party apps friendly. You can add i18n support to the existing models without modifying their definition at all (think in apps you can't modify directly for example djago.contrib.flatpages).

Installation
===========

Clone the git repository::

    git clone https://github.com/juanpex/django-model-i18n.git

or install with pip::

    pip install git+https://github.com/juanpex/django-model-i18n.git#egg=django-model-i18n

Configuration
=============

Add ``model_i18n`` admin loaders to your root project ``urls.py``::

    from model_i18n import loaders

    loaders.autodiscover_admin()

and add ``'django.middleware.locale.LocaleMiddleware'`` into ``MIDDLEWARE_CLASSES``::

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

and finally add ``model_i18n`` **as the first item** of ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        'model_i18n',
        ...
        'django.contrib.admin',
        ...
    )


Usage
=====

1) Create a ``translations.py`` in each app directory where you want to use ``model_i18n``
2) Register translations per-model::

    from model_i18n import translator
    from .models import Poll

    class PollTranslation(translator.ModelTranslation):
        fields = ('title',)

    translator.register(Poll, PollTranslation)


3) Don't forget to update the database: a new ``schemamigration`` if you're using South, or ``syncdb`` if not.

Notes
=====

If you want to translate models that are in ``django.contrib.*``, *e.g.* flatpages, you can create a ``translations.py`` in your root project directory and register them like this::
    
    from model_i18n import translator
    from django.contrib.flatpages.models import FlatPage

    class FlatPageTranslation(translator.ModelTranslation):
        fields = ('title', 'content')
    
    translator.register(FlatPage, FlatPageTranslation)


and if you use south, you must also set the ``SOUTH_MIGRATION_MODULES`` setting to pick up this change::

    SOUTH_MIGRATION_MODULES  = {
        'flatpages': 'migrations.flatpages'
    }


``django_i18n`` has good integration with `django.contib.admin`; it automatically configures ``ModelAdmin`` and inlines that apply.

API EXAMPLES
============

Filtering
---------

::

    Item.objects.set_language("es").filter(translations__title__contains='sometext')
    items = Item.objects.filter(Q(translations___language='en') | Q(translations___language='es'))

    items = items.exclude(category__name='stuff')
    items = items.filter(Q(title__icontains='book') | Q(translations__title__icontains='toy'))


Updating
---------

::

   Item.objects.set_language("es").filter(translations__title__contains='sometext').update(title=u'new text')

Deleting
---------

::

    Item.objects.set_language("fr").filter(translations__title__contains='titres à éliminer').delete()
