# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from BeautifulSoup import BeautifulSoup

from app.models import Item, Category, RelatedItem


def testObject(test, item, values):
    for k, v in values.items():
        test(getattr(item, k), v)

itemValue1 = dict(title=u'Title 1 EN', content=u'Content 1 EN', slug=u'title-1-en')
itemValue2 = dict(title=u'Title 2 EN', content=u'Content 2 EN', slug=u'title-2-en')
itemValue3 = dict(title=u'Title 3 EN', content=u'Content 3 EN', slug=u'title-3-en')


class TestTransQueryCase(TestCase):

    def setUp(self):
        # Category
        category1 = Category.objects.create(name='Category 1 EN')
        category1.translations.create(_master=category1, _language=u'es', name=u'Categoría 1 ES')
        category1.translations.create(_master=category1, _language=u'fr', name=u'Catégorie 1 FR')

        category2 = Category.objects.create(name='Category 2 EN')
        category2.translations.create(_master=category2, _language=u'es', name=u'Categoría 2 ES')

        Category.objects.create(name='Category 3 EN')

        # Item
        item1 = Item.objects.create(**itemValue1)
        item1.translations.create(_master=item1, _language=u'es', title=u'Título 1 ES', content=u'Contenido 1 ES')
        item1.translations.create(_master=item1, _language=u'fr', title=u'Titre 1 FR', content=u'Contenu 1 FR')

        item2 = Item.objects.create(**itemValue2)
        item2.translations.create(_master=item2, _language=u'es', title=u'Título 2 ES', content=u'Contenido 2 ES')

        Item.objects.create(**itemValue3)

        # RelatedItem
        related_item1 = RelatedItem.objects.create(item=item1, value=1, data='Data 1')
        related_item1.translations.create(_master=related_item1, _language=u'es', value=11)
        related_item1.translations.create(_master=related_item1, _language=u'fr', value=111)

        related_item2 = RelatedItem.objects.create(item=item2, value=2, data='Data 2')
        related_item2.translations.create(_master=related_item2, _language=u'es', value=22)

        RelatedItem.objects.create(item=item2, value=3, data='Data 3')

    def testTranslations(self):
        queryset = Item.objects.all()
        self.assertEquals(queryset.count(), 3)
        queryset = queryset.filter(title__icontains='Title 1')
        self.assertEquals(queryset.count(), 1)
        obj = queryset[0]
        testObject(self.assertEquals, obj, itemValue1)
        self.assertEquals(queryset.update(title='Title updated'), 1)

    def testUpdateTranslations(self):
        obj = Item.objects.all()[0]
        self.assertEquals(obj.title, u'Title 1 EN')
        obj = Item.objects.set_language('es').all()[0]
        self.assertEquals(obj.title, u'Título 1 ES')
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'Titre 1 FR')
        count = Item.objects.set_language('fr').update(title=u'New Titre FR')
        self.assertEquals(count, 1)
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'New Titre FR')
        obj = Item.objects.all()[0]
        self.assertEquals(obj.title, u'Title 1 EN')
        obj = Item.objects.set_language('es').all()[0]
        self.assertEquals(obj.title, u'Título 1 ES')
        count = Item.objects.set_language('fr').update(title=u'Titre 1 FR')
        self.assertEquals(count, 1)
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'Titre 1 FR')

    def testDeleteTranslations(self):
        obj = Item.objects.all()[0]
        self.assertEquals(obj.title, u'Title 1 EN')
        self.assertEquals(obj.translations.all().count(), 2)
        Item.objects.set_language('fr').delete()
        self.assertEquals(obj.translations.all().count(), 1)
        obj = Item.objects.set_language('fr').all()[0]
        self.assertEquals(obj.title, u'Title 1 EN')
        obj = Item.objects.set_language('es').all()[0]
        self.assertEquals(obj.title, u'Título 1 ES')


class TestTransAdminCase(TestCase):

    def setUp(self):
        username = 'admin'
        pwd = 'admin'
        self.u = User.objects.create_user(username, '', pwd)
        self.u.is_staff = True
        self.u.is_superuser = True
        self.u.save()
        self.assertTrue(self.client.login(username=username, password=pwd),
            "Logging in user %s, pwd %s failed." % (username, pwd))

        Item.objects.all().delete()
        RelatedItem.objects.all().delete()


    def tearDown(self):
        self.client.logout()
        self.u.delete()

    def get_inputs(self, response):
        soup = BeautifulSoup(response.content)
        return dict([(dict(n.attrs).get('name'), (dict(n.attrs).get('type'), dict(n.attrs).get('value'))) for n in soup('input')])

    def get_inputs_by_type(self, inputs, typename):
        return dict([(name, value) for name, (type, value) in inputs.items() if type == typename])

    def get_inputs_by_name(self, inputs, inputname):
        return dict([(name, value) for name, (type, value) in inputs.items() if inputname in name])

    def get_basic_inputs(self, inputs):
        basic_names = ('INITIAL_FORMS', 'MAX_NUM_FORMS', 'TOTAL_FORMS', 'csrfmiddlewaretoken')
        result = {}
        for k, v in inputs.items():
            for j in basic_names:
                if j in k:
                    result[k] = v
        return result

    def get_basic_form_post(self, response):
        inputs = self.get_inputs(response)
        hiddens = self.get_inputs_by_type(inputs, 'hidden')
        return self.get_basic_inputs(hiddens)

    def get_inline_form_post(self, response):
        inputs = self.get_inputs(response)
        return self.get_inputs_by_name(inputs, 'items-0')

    def test_add_item_ok(self):
        self.assertEquals(Item.objects.count(), 0)
        response = self.client.get(reverse('admin:app_item_add'))
        basic_post = self.get_basic_form_post(response)
        post_data = {
            'title': u'Test OK',
            'slug': u'test-ok',
            'content': u'Content OK',
        }
        post_data.update(basic_post)
        response = self.client.post(reverse('admin:app_item_add'), post_data)
        self.assertRedirects(response, reverse('admin:app_item_changelist'))
        self.assertEquals(Item.objects.count(), 1)

    def test_add_item_ok_with_inlines(self):
        self.assertEquals(Item.objects.count(), 0)
        response = self.client.get(reverse('admin:app_item_add'))
        basic_post = self.get_basic_form_post(response)
        post_data = {
            'title': u'Test OK',
            'slug': u'test-ok',
            'content': u'Content OK',
            'items-0-value': 1,
            'items-0-data': 'Data 1',
        }
        post_data.update(basic_post)
        response = self.client.post(reverse('admin:app_item_add'), post_data)
        self.assertRedirects(response, reverse('admin:app_item_changelist'))
        self.assertEquals(Item.objects.count(), 1)
        self.assertEquals(RelatedItem.objects.count(), 1)

    def test_add_item_ok_with_translation(self, language='es'):
        self.test_add_item_ok()
        itm = Item.objects.all()[0]
        edit_url = reverse('admin:app_item_change', args=[itm.pk]) + language + '/'
        response = self.client.get(edit_url)
        basic_post = self.get_basic_form_post(response)
        post_data = {
            'title': u'Test OK %s' % language,
            'content': u'Content OK %s' % language,
        }
        post_data.update(basic_post)
        response = self.client.post(edit_url, post_data)
        self.assertRedirects(response, reverse('admin:app_item_changelist'))
        self.assertEquals(Item.objects.count(), 1)
        trans_model = Item._translation_model
        self.assertEquals(trans_model.objects.count(), 1)
        trans_instance = trans_model.objects.all()[0]
        self.assertEquals(trans_instance._master, itm)
        self.assertEquals(trans_instance._language, language)
        self.assertEquals(trans_instance.title, post_data['title'])
        self.assertEquals(trans_instance.content, post_data['content'])

    def test_add_item_ok_with_inlines_translation(self, language='fr'):
        self.test_add_item_ok_with_inlines()
        itm = Item.objects.all()[0]
        edit_url = reverse('admin:app_item_change', args=[itm.pk]) + language + '/'
        response = self.client.get(edit_url)
        basic_post = self.get_basic_form_post(response)
        inline_post = self.get_inline_form_post(response)
        inline_post.update({'items-0-value': 10})
        post_data = {
            'title': u'Test OK %s' % language,
            'content': u'Content OK %s' % language,
        }
        post_data.update(basic_post)
        post_data.update(inline_post)
        response = self.client.post(edit_url, post_data)
        self.assertRedirects(response, reverse('admin:app_item_changelist'))

        self.assertEquals(Item.objects.count(), 1)
        trans_model = Item._translation_model
        self.assertEquals(trans_model.objects.count(), 1)
        trans_instance = trans_model.objects.all()[0]
        self.assertEquals(trans_instance._master, itm)
        self.assertEquals(trans_instance._language, language)
        self.assertEquals(trans_instance.title, post_data['title'])
        self.assertEquals(trans_instance.content, post_data['content'])

        self.assertEquals(RelatedItem.objects.count(), 1)
        transrel_model = RelatedItem._translation_model
        self.assertEquals(transrel_model.objects.count(), 1)
        relitem_instance = RelatedItem.objects.all()[0]
        transrel_instance = transrel_model.objects.all()[0]
        self.assertEquals(transrel_instance._master, relitem_instance)
        self.assertEquals(transrel_instance._language, language)
        self.assertEquals(transrel_instance.value, post_data['items-0-value'])


