from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.decorators.cache import never_cache

from model_i18n import loaders
from app.views import DefaultView, ItemDetailView

admin.autodiscover()
loaders.autodiscover()

urlpatterns = patterns('',
	(r'^$', never_cache(DefaultView.as_view())),
    (r'^item/(?P<slug>[\w-]+)/$', never_cache(ItemDetailView.as_view())),
	(r'^admin/', include(admin.site.urls)),
    (r'^i18n/', include('model_i18n.urls')),
)
