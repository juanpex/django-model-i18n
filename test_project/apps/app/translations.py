from model_i18n import translator

from app.models import Item, Category, RelatedItem


class CategoryTranslation(translator.ModelTranslation):
    fields = ('name',)


class ItemTranslation(translator.ModelTranslation):
    fields = ('title', 'content')
    db_table = 'item_translation'


class RelatedItemTranslation(translator.ModelTranslation):
    fields = ('value',)


translator.register(Category, CategoryTranslation)
translator.register(Item, ItemTranslation)
translator.register(RelatedItem, RelatedItemTranslation)
