import debug_toolbar.urls

from django.conf.urls.defaults import patterns, include

from fusionbox.panels.user_panel.urls import urlpatterns

debug_toolbar.urls.urlpatterns += patterns('',
    ('', include(urlpatterns)),
)
