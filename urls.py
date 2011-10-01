"""
URL configuration module.

This file is used by django to set up the URL routes appropriately. You must
include this in your site-wide urls.py as follows:

from rainbeard.urls import urls as rainbeard_urls

urlpatterns = patterns('',
                ...
                url(r'', include(rainbeard_urls))
"""

import views, ajax
from django.conf.urls.defaults import patterns, url

urls = patterns('',
         url(r'^logout/?', views.logout_view),
         url(r'^register/?', views.register_view),
         url(r'^login(/.*)?$', views.login_view),
         url(r'^/?$', views.main_view),
         url(r'^query/?$', views.query_view),
         url(r'^ajax/givens/get?$', ajax.get_givens))
