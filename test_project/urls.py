# -*- coding: utf-8 -*-
from django.conf import settings
try:
    from django.conf.urls.defaults import patterns, url, include
except ImportError:
    from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.decorators.cache import never_cache
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from model_i18n import loaders
from app.views import DefaultView, ItemDetailView

admin.autodiscover()
loaders.autodiscover_admin()

urlpatterns = patterns('',
    (r'^$', never_cache(DefaultView.as_view())),
    (r'^item/(?P<slug>[\w-]+)/$', never_cache(ItemDetailView.as_view())),
    (r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('model_i18n.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
