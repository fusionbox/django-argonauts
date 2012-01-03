"""
To install the newsletter app for your project add the following to your
urlpatterns:

    `url(r'^newsletter/', include('newsletter.urls','newsletter'))`

    Note: It is important that the namespace is set to newsletter for the templatetags to work.
    """
from django.conf.urls import patterns, url

urlpatterns = patterns("newsletter.views",
        url(r"^$", "signup", name="signup_form"),
        )
