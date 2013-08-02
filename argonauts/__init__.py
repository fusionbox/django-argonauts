# -*- coding: utf-8 -*-

# (major, minor): (1, 0) -> 1.0
# (major, minor, phase): (1, 1, 'alpha') -> 1.0alpha
# (major, minor, phase, phaseversion): (1, 1, 'rc', 5) -> 1.1rc5

VERSION = (0, 9, 'alpha')


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
