from functools import wraps

from django.settings import DEFAULT_CHARSET
from django.utils import simplejson as json
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseBadRequest


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
            message = 'Expected AJAX request'
            if not request.is_ajax():
                if isinstance(raise_on_error, type):
                    return raise_on_error(message)
                else:
                    return raise_on_error
                return func(request, *args, **kwargs)
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
                try:
                    if encoding:
                        my_encoding = encoding
                    elif request.encoding:
                        my_encoding = request.encoding
                    else:
                        my_encoding = DEFAULT_CHARSET
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
