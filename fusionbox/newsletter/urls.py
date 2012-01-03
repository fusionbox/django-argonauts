from django.conf.urls import patterns, url

urlpatterns = patterns("newsletter.views",
        url(r"^$", "signup", name="signup_form"),
        )
