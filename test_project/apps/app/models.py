# -*- coding: utf-8 -*-
from django.db import models


class Item(models.Model):

    slug = models.SlugField()
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.title
