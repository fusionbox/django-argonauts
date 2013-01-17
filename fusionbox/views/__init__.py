"""
Fusionbox generic views.
"""
from urlparse import urlparse
import urllib

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from .rest import RestView  # NOQA
from .base import StaticServe  # NOQA


def DecoratorMixin(decorator):
    """
    Convers a decorator written for a function view into a mixin for a
    class-based view.

    ::

        LoginRequiredMixin = DecoratorMixin(login_required)

        class MyView(LoginRequiredMixin):
            pass

        class SomeView(DecoratorMixin(some_decorator),
                       DecoratorMixin(something_else)):
            pass

    """

    class Mixin(object):
        __doc__ = decorator.__doc__

        @classmethod
        def as_view(cls, *args, **kwargs):
            view = super(Mixin, cls).as_view(*args, **kwargs)
            return decorator(view)

    Mixin.__name__ = 'DecoratorMixin(%s)' % decorator.__name__
    return Mixin


class WithNextUrlMixin(object):
    """
    This view will use whatever value was submitted as `next` as the success
    url, as long as the url resolves correctly.

    This also provides two template context variables

    1. next - the value of the next url, defaults to None.
    2. next_input - a hidden input with the next value.
    """
    def get_success_url(self):
        return self.get_next_url() or super(WithNextUrlMixin, self).get_success_url()

    def get_next_url(self):
        next = self.request.REQUEST.get('next')

        # From django.contrib.auth.views.login
        if next:
            netloc = urlparse(next)[1]
            if netloc and not netloc == self.request.get_host():
                return
            return next

    def get_context_data(self, **kwargs):
        kwargs = super(WithNextUrlMixin, self).get_context_data(**kwargs)
        # Hangle 'next' value for login redirect
        next = self.get_next_url()
        if next:
            kwargs['next'] = next
            kwargs['next_input'] = mark_safe('<input type="hidden" name="next" value="{0}">'.format(next))
        return kwargs

    @staticmethod
    def with_next(view, next_url, args=None, kwargs=None):
        return '{0}?{1}'.format(
            reverse(view, args=args, kwargs=kwargs),
            urllib.urlencode({'next': next_url}),
            )
