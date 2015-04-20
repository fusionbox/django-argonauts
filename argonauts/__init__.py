# -*- coding: utf-8 -*-
import pkg_resources

__version__ = pkg_resources.get_distribution('django-argonauts').version

# BBB: This was here before we switch to zest.releaser.
VERSION = tuple(__version__.split('.'))
def get_version():
    return __version__


def dumps(*args, **kwargs):
    """
    Wrapper for json.dumps that uses the JSONArgonautsEncoder.
    """
    import json

    from django.conf import settings
    from argonauts.serializers import JSONArgonautsEncoder

    kwargs.setdefault('cls', JSONArgonautsEncoder)
    # pretty print in DEBUG mode.
    if settings.DEBUG:
        kwargs.setdefault('indent', 4)
        kwargs.setdefault('separators', (',', ': '))
    else:
        kwargs.setdefault('separators', (',', ':'))

    return json.dumps(*args, **kwargs)
