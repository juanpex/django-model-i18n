from model_i18n import translator

from django.contrib.flatpages.models import FlatPage


class FlatPageTranslation(translator.ModelTranslation):
    fields = ('title', 'content')


translator.register(FlatPage, FlatPageTranslation)
