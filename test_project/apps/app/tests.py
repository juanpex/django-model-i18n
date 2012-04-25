# -*- coding: utf-8 -*-
from django.test import TestCase
from app.models import Item


class MyTestCase(TestCase):

    def setUp(self):
        item = Item.objects.create(title=u'Title EN', content=u'Content EN', slug=u"title-en")
        item.translations.create(_master=item, _language=u'es', title=u'Título ES', content=u'Contenido ES')
        item.translations.create(_master=item, _language=u'fr', title=u'Titre FR', content=u'Contenu FR')

    def testUpdateTranslations(self):
        obj = Item.objects.all()[0]
        self.assertEquals(obj.title, u'Title EN')
        obj = Item.objects.set_language('es').all()[0]
        self.assertEquals(obj.title, u'Título ES')
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'Titre FR')
        count = Item.objects.set_language('fr').update(title=u'New Titre FR')
        self.assertEquals(count, 1)
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'New Titre FR')
        obj = Item.objects.all()[0]
        self.assertEquals(obj.title, u'Title EN')
        obj = Item.objects.set_language('es').all()[0]
        self.assertEquals(obj.title, u'Título ES')
        count = Item.objects.set_language('fr').update(title=u'Titre FR')
        self.assertEquals(count, 1)
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'Titre FR')

    def testDeleteTranslations(self):
        obj = Item.objects.all()[0]
        self.assertEquals(obj.title, u'Title EN')
        self.assertEquals(obj.translations.all().count(), 2)
        Item.objects.set_language('fr').delete()
        self.assertEquals(obj.translations.all().count(), 1)
        Item.objects.set_language('fr')
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'Title EN')
        obj = Item.objects.set_language('es').all()[0]
        self.assertEquals(obj.title, u'Título ES')
