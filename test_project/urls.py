from django.conf.urls.defaults import *
from django.contrib import admin
from model_i18n import loaders
from model_i18n.views import set_language
from app.views import DefaultView

admin.autodiscover()
loaders.autodiscover()

urlpatterns = patterns('',
	(r'^$', DefaultView.as_view()),
	url(r'^setlang/$', set_language, name='setlang'),
    (r'^admin/', include(admin.site.urls)),
)
