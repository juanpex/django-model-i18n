# -*- coding: utf-8 -*-
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Item(models.Model):

    slug = models.SlugField()
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.title


class RelatedItem(models.Model):
    item = models.ForeignKey(Item, related_name='items')
    value = models.IntegerField()
    data = models.CharField(max_length=15, default='')

    def __unicode__(self):
        return unicode(self.value)
