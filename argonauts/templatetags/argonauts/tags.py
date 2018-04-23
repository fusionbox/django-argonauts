from __future__ import absolute_import

import itertools

from .library import register
from . import filters


@register.simple_tag
def json(*args, **kwargs):
    """
    Output the json encoding of its arguments and keyword arguments.

    This will escape all the HTML/XML special characters with their unicode
    escapes, so it is safe to be output anywhere except for inside a tag
    attribute.
    """
    if args and kwargs:
        items = itertools.chain(
            enumerate(args),
            [('length', len(args))],
            kwargs.items(),
        )
        return filters.json({k: v for k, v in items})
    if args:
        return filters.json(args)
    if kwargs:
        return filters.json(kwargs)
    return filters.json(None)

json.is_safe = True
