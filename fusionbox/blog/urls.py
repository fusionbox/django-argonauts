from django.conf.urls import patterns, include, url
"""
To install the blog app for your project add the following to your
urlpatterns:

    `url(r'^blog/', include('fusionbox.blog.urls','blog'))`

Note: It is important that the namespace is set to newsletter for the templatetags to work.
"""

from django.conf.urls import patterns, url

urlpatterns = patterns('fusionbox.blog.views',
        url('^$', 'index'),
        url('^tag/(?P<tag>.+)/$', 'index'),
        url('^(?P<slug>.+)/$', 'detail'),
)
