# -*- coding: utf-8 -*-

# (major, minor, bugfix): (1, 0, 0) -> 1.0.0
# (major, minor, bugfix, phase): (1, 1, 5, 'alpha') -> 1.0.5alpha
# (major, minor, bugfix, phase, phaseversion): (1, 1, 0, 'rc', 5) -> 1.1.0rc5

VERSION = (1, 0, 0)


def get_version():
    from . import version
    return version.to_string(VERSION)


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
