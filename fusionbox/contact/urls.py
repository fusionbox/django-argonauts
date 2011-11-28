from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('fusionbox.contact.views',
        url(r'^$', 'index', name='contact_index'),
        url(r'^success/$', 'success', name='contact_success'),
    )
