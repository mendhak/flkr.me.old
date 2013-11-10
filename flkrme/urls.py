from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^(?i)img/(?P<nsid>[A-Za-z0-9@]+)/?(?P<num>[0-9]+)?/?(?P<size>[A-Za-z0-9-]+)?/?(?P<popular>[p]{1})?', 'flickrtools.views.image'),
    url(r'^(?i)url/(?P<nsid>[A-Za-z0-9@]+)/?(?P<num>[0-9]+)?/?(?P<popular>[p]{1})?', 'flickrtools.views.redirect'),
    url(r'^(?i)searchimg/(?P<tags>[A-Za-z0-9-]+)/(?P<num>[0-9]+)/?(?P<size>[A-Za-z0-9-]+)?/?(?P<nsid>[A-Za-z0-9@]+)?', 'flickrtools.views.searchImage'),
    url(r'^(?i)searchurl/(?P<tags>[A-Za-z0-9-]+)/(?P<num>[0-9]+)/?(?P<nsid>[A-Za-z0-9@]+)?','flickrtools.views.searchRedirect'),
    url(r'^(?i)nsid/(?P<username>.+)', 'flickrtools.views.nsid'),
    url(r'^(?i)gettitlefromurl/(?P<url>.+)', 'flickrtools.views.getTitleFromUrl'),
    url(r'^signatures$', 'flickrtools.views.main'),
    url(r'^fullscreen$', 'flickrtools.views.fullscreen'),
    url(r'^(?i)(?P<color>[^/]+)/?(?P<photoid>[0-9]+)?', 'flickrtools.views.showcolor'),
    url(r'^$', TemplateView.as_view(template_name="index.html")),
)
