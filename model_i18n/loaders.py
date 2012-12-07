# -*- coding: utf-8 -*-
from os import path


def autodiscover(module_name=None):

    """
    Auto-discover translations.py files in installed app's directories, fail
    silently if not present. This forces an import on them to register any
    translation bits they may want.

    Based on django's contrib.admin autodiscover().
    """

    import imp
    from model_i18n.utils import import_module
    from model_i18n.conf import settings

    if not module_name:
        module_name = settings.TRANSLATION_FILENAMES or 'translations'

    for app in settings.INSTALLED_APPS:
        if app == 'model_i18n':
            continue
        # For each app, we need to look for `module_name` in that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for translation.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently. Try with dirname of module file if __path__ attribute
        # is not present.
        app_module = import_module(app)
        if hasattr(app_module, '__path__'):
            app_path = app_module.__path__
        else:
            app_path = path.dirname(app_module.__file__)

        # Step 2: use imp.find_module to find the app's `module_name`. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its `module_name` doesn't exist

        try:
            imp.find_module(module_name, app_path)
        except ImportError:
            continue
        # Step 3: import the app's translation file.
        # If this has errors we want them to bubble up.
        import_module('.'.join([app, module_name]))

    if settings.MODEL_I18N_SETTINGS_PATH:
        project_dir = settings.MODEL_I18N_SETTINGS_PATH
    else:
        project_dir = path.dirname(import_module(settings.SETTINGS_MODULE).__file__)
    project_folder = path.basename(project_dir)
    try:

        imp.find_module(module_name, [project_dir, ])
        import_module('.'.join([project_folder, module_name]))
    except ImportError:
        pass

    from model_i18n import translator
    from model_i18n.conf import TRANSLATED_APP_MODELS
    from django.core.exceptions import ImproperlyConfigured

    if TRANSLATED_APP_MODELS:
        for app_path in TRANSLATED_APP_MODELS:
            model_conf = TRANSLATED_APP_MODELS[app_path]
            for model_name in model_conf:
                model_module = import_module(app_path + '.models')
                try:
                    django_model = getattr(model_module, model_name)
                except:
                    raise ImproperlyConfigured("Model %s does not exist on %s" % \
                        (model_name, app_path))
                if django_model not in translator._translator._registry:
                    translator.register(django_model, **model_conf[model_name])


def autodiscover_admin(adminsite=None):
    if not adminsite:
        from django.contrib.admin import site
        adminsite = site

    from model_i18n.translator import _translator
    from model_i18n.admin import setup_admin
    for m, t in _translator._registry_admin.items():
        setup_admin(m, t, adminsite)
