try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url

from fusionbox.blog.feeds import BlogFeed

"""
To install the blog app for your project add the following to your
urlpatterns:

    `url(r'^blog/', include('fusionbox.blog.urls','blog'))`

Note: It is important that the namespace is set to blog
for the templatetags to work.
"""

urlpatterns = patterns('fusionbox.blog.views',
        url('^$', 'index', name='blog_index'),
        url('^tag/(?P<tag>.+)/$', 'index', name='tag_index'),
        url('^author/(?P<author_id>.+)/$', 'index', name='author'),
        url('^feed/$', BlogFeed(), name="feed"),
        url('^feed/author/(?P<author_id>[^/]+)/$', BlogFeed(), name='author_feed'),
        url('^feed/tag/(?P<tag>[^/]+)/$', BlogFeed(), name='tag_feed'),
        url('^(?P<slug>.+)/$', 'detail', name='blog_detail'),
)
