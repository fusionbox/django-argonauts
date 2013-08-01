import datetime
import logging
import hashlib
import time
import re
from functools import wraps

from django.conf import settings
from django.utils import simplejson as json
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest
from django.core.cache import cache

logger = logging.getLogger(__name__)


require_PUT = require_http_methods(['PUT'])
require_DELETE = require_http_methods(['DELETE'])


def require_AJAX(func, raise_on_error=HttpResponseBadRequest):
    """
    Decorator that returns an ``HttpResponseBadRequest`` if the request is not
    an AJAX request.  The response can be customized using the
    ``raise_on_error`` argument::

        @require_AJAX
        def my_view(request):
            # ...

        @require_AJAX(raise_on_error=HttpResponseForbidden)
        def my_view(request):
            # ...
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.is_ajax():
                return func(request, *args, **kwargs)

            message = 'Expected AJAX request'
            if isinstance(raise_on_error, type):
                return raise_on_error(message)
            else:
                return raise_on_error
        return inner

    if func:
        return decorator(func)
    return decorator


def require_JSON(func, raise_on_error=HttpResponseBadRequest, encoding=None):
    """
    Decorator to parse JSON requests.  If the JSON data is not present,
    or if it is malformed, an error response is returned.  Otherwise,
    the JSON data will be decoded (using ``encoding``) and made available
    in request.payload.  The error can be disabled or customized by setting
    raise_on_error to Falsey (disable) an ``HttpResponse`` instance, or a class
    (the JSON error message will be assigned to the constructor).  If the
    error is disabled, the message will be in ``request.JSON_ERROR``::

        @require_JSON
        def my_view(request):
            print request.JSON
            # ...

        @require_JSON(encoding='utf-16', raise_on_error=None)
        def my_view(request):
            if request.JSON:
                print request.JSON
            else:
                print request.JSON_ERROR
            # ...
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            message = 'Expected Content-Type application/json'
            if request.META.get('CONTENT_TYPE') == 'application/json':
                if encoding:
                    my_encoding = encoding
                elif request.encoding:
                    my_encoding = request.encoding
                else:
                    my_encoding = settings.DEFAULT_CHARSET
                try:
                    request.payload = json.loads(request.read().decode(my_encoding))
                    return func(request, *args, **kwargs)
                except ValueError as e:
                    request.JSON_ERROR = message = e.message
            if not raise_on_error:
                return func(request, *args, **kwargs)

            if isinstance(raise_on_error, type):
                return raise_on_error(message)
            else:
                return raise_on_error
        return inner
    if func:
        return decorator(func)
    return decorator


def args_kwargs_to_call(args, kwargs):
    """
    Turns args (a list) and kwargs (a dict) into a string that looks like it
    could be used to call a function with positional and keyword arguments.

    >>> args_kwargs_to_call([1], {})
    '1'
    >>> args_kwargs_to_call([1,2], {})
    '1, 2'
    >>> args_kwargs_to_call([1], {'foo':'bar'})
    "1, foo='bar'"

    """
    ret = []
    for arg in args:
        if ret:
            ret.append(", ")
        ret.append(repr(arg))
    for k, v in kwargs.iteritems():
        if ret:
            ret.append(", ")
        ret.append("%s=%r" % (k, v))
    return ''.join(ret)


WHITESPACE_RE = re.compile('\s')

def cached(keyfn, timeout=300):
    """
    Returns a decorator that caches a function's return valued based on the
    keyfn applied to the inner function's arguments. The result is cached for
    `timeout` seconds, or `timeout` timedelta.

    ::

        @cached(lambda a, b, date: [str(a), str(b), date.isoformat()])
        def generate_report(a, b, date):
            return frobnicate(
                slow_api_call(a, date),
                slow_api_call(b, date),
                munge(process_range(a, b)),
            )

    It works on methods too::

        @cached(lambda self, a: [self.id, a])
        def whatever(self, a):
            # ...
    """

    if isinstance(timeout, datetime.timedelta):
        # timeout = timeout.total_seconds()  # python >= 2.7
        timeout = (timeout.microseconds + (timeout.seconds + timeout.days * 24 * 3600) * 10**6) / float(10**6)
    def decorator(fn):
        def cache_key(args, kwargs):
            key = [fn.__name__] + list(keyfn(*args, **kwargs))
            key = ':'.join(key)
            if WHITESPACE_RE.search(key):
                # memcache doesn't allow whitespace in keys
                return 'sha256:' + hashlib.sha256(key).hexdigest()
            else:
                return 'raw:' + key

        def calculate_and_set(key, args, kwargs):
            start = time.time()
            r = fn(*args, **kwargs)
            end = time.time()
            logger.info("%s(%s) took %s" % (fn.__name__, args_kwargs_to_call(args, kwargs), end - start))
            cache.set(key, r, timeout)
            return r

        @wraps(fn)
        def refresh(*args, **kwargs):
            """
            'Refreshes' the cached value, calculating and setting it without
            checking if its already cached. For warming the cache in a
            background job.

            ::

                for a, b, date in all_possible_combinations:
                    generate_report.refresh(a, b, date)
                # All reports are now precalculated and stored, any future
                # calls to generate_report() will use the cache until it
                # expires.
            """
            key = cache_key(args, kwargs)
            return calculate_and_set(key, args, kwargs)

        @wraps(fn)
        def inner(*args, **kwargs):
            """
            Wraps `fn` as a cached function, using the previous value if it has
            already been called with the same args and kwargs.
            """
            key = cache_key(args, kwargs)
            r = cache.get(key)
            if r is not None:
                logger.info("%s(%s) gotten from cache" % (fn.__name__, args_kwargs_to_call(args, kwargs)))
                return r
            else:
                return calculate_and_set(key, args, kwargs)

        def clear_cache(*args, **kwargs):
            """
            Clears the cache based on args and kwargs

            ::

               generate_report(a, b, date)  # result is cached for these arguments
               generate_report.clear_cache(a, b, date)  # result is no longer cached,
                                                        # another call will regenerate the report.

            If decorating a method, you must pass in the `self` argument explicitly::

                obj.calculate(obj, a)
            """
            key = cache_key(args, kwargs)
            cache.delete(key)

        inner.clear_cache = clear_cache
        inner.refresh = refresh
        return inner
    return decorator
