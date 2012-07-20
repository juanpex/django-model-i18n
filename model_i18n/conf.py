from django.conf import settings
# Translation model's common field default names.
# If you want to get a field name for a specific translation model remember it
# may have been overriden in the ModelTranslation definition, don't import
# these directly use the translation model's _transmeta attrs (or utils
# helpers) insted.
DEFAULT_LANGUAGE_FIELD_NAME = \
    getattr(settings, 'MODEL_I18N_LANGUAGE_FIELD_NAME', '_language')
DEFAULT_MASTER_FIELD_NAME = \
    getattr(settings, 'MODEL_I18N_MASTER_FIELD_NAME', '_master')

# Translation table suffix used when building the table name from master model
# db_table
TRANSLATION_TABLE_SUFFIX = 'translation'
# filename to load in autodiscover
TRANSLATION_FILENAMES = getattr(settings, 'TRANSLATION_FILENAMES', 'translations')

# Master attributes are stored in backups attributes in the form
# <attribute name>_<suffix>, ATTR_BACKUP_SUFFIX allows to define suffix used,
# _master by default
ATTR_BACKUP_SUFFIX = 'master'

# Master model reverse relation related name
RELATED_NAME = 'translations'

# Current loaded languages attribute name
CURRENT_LANGUAGES = 'current_languages'
# Current selected language
CURRENT_LANGUAGE = 'current_language'

# Change form template and translation edition template
CHANGE_TPL = 'i18n/admin/change_form.html'
CHANGE_TRANSLATION_TPL = 'i18n/admin/change_translation_form.html'

# Autogenerate models translations for third party apps
#
# TRANSLATED_APP_MODELS = {
#    'django.contrib.flatpages': {
#        'FlatPage': {'fields': ('title', 'content',)}
#    },
# }
TRANSLATED_APP_MODELS = getattr(settings, 'TRANSLATED_APP_MODELS', {})

MODEL_I18N_DJANGO_ADMIN = getattr(settings, 'MODEL_I18N_DJANGO_ADMIN', True)

MODEL_I18N_DJANGO_ADMIN = getattr(settings, 'MODEL_I18N_DJANGO_ADMIN', True)

DEFAULT_TRANS_MANAGER = getattr(settings, 'DEFAULT_TRANS_MANAGER', None)


for k, v in locals().items():
    if k == k.upper():
        setattr(settings, k, v)


# Do we have multidb support? (post r11952)
try:
    from django.db import DEFAULT_DB_ALIAS
    if DEFAULT_DB_ALIAS:
        MULTIDB_SUPPORT = True
    else:
        MULTIDB_SUPPORT = False
except ImportError:
    MULTIDB_SUPPORT = False
