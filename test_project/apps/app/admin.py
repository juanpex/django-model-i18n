# -*- coding: utf-8 -*-
from django.contrib import admin

from app.models import Item

class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Item, ItemAdmin)
