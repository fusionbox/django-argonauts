"""
View classes to help facilitate the creation of REST APIs
"""
import json

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, Http404
from django.views.generic.base import View
from django.conf import settings

from argonauts import dumps


class JsonResponseMixin(object):
    """
    Sets the response MIME type to ``application/json`` and serializes the
    context obj as a JSON string.
    """
    def render_to_response(self, obj, **response_kwargs):
        """
        Returns an ``HttpResponse`` object instance with Content-Type:
        application/json.

        The response body will be the return value of ``self.serialize(obj)``
        """
        return HttpResponse(self.serialize(obj), content_type='application/json', **response_kwargs)

    def serialize(self, obj):
        """
        Returns a json serialized string object encoded using
        `argonauts.serializers.JSONArgonautsEncoder`.
        """
        return dumps(obj)

    def http_method_not_allowed(self, *args, **kwargs):
        """
        Returns super after setting the Content-Type header to
        ``application/json``
        """
        resp = super(JsonResponseMixin, self).http_method_not_allowed(*args, **kwargs)
        resp['Content-Type'] = 'application/json'

        return resp


class JsonRequestMixin(object):
    """
    Adds a ``data`` method on the view instance.  It returns the GET parameters
    if it is a GET request.  It will return the python representation of the
    JSON sent with the request body.
    """
    def data(self):
        """
        Helper class for parsing JSON POST data into a Python object.
        """
        if self.request.method == 'GET':
            return self.request.GET
        else:
            assert self.request.META['CONTENT_TYPE'].startswith('application/json')
            charset = self.request.encoding or settings.DEFAULT_CHARSET
            return json.loads(self.request.body.decode(charset))


class RestView(JsonResponseMixin, JsonRequestMixin, View):
    """
    Inherit this base class to implement a REST view.

    This view will handle:
        - authentication (throuh the ``auth`` method)
        - dispatching to the proper HTTP method function
        - returning a proper error status code.

    It also implements a default response for the OPTIONS HTTP request method.
    """
    def auth(self, *args, **kwargs):
        """
        Hook for implementing custom authentication.

        Raises ``NotImplementedError`` by default.  Subclasses must overwrite
        this.
        """
        raise NotImplementedError("If you really want no authentication, override this method")

    def dispatch(self, *args, **kwargs):
        """
        Authenticates the request and dispatches to the correct HTTP method
        function (GET, POST, PUT,...).

        Translates exceptions into proper JSON serialized HTTP responses:
            - ValidationError: HTTP 409
            - Http404: HTTP 404
            - PermissionDenied: HTTP 403
            - ValueError: HTTP 400
        """
        try:
            self.auth(*args, **kwargs)
            return super(RestView, self).dispatch(*args, **kwargs)
        except ValidationError as e:
            return self.render_to_response(e.message_dict, status=409)
        except Http404 as e:
            return self.render_to_response(str(e), status=404)
        except PermissionDenied as e:
            return self.render_to_response(str(e), status=403)
        except ValueError as e:
            return self.render_to_response(str(e), status=400)

    def options(self, request, *args, **kwargs):
        """
        Implements a OPTIONS HTTP method function returning all allowed HTTP
        methods.
        """
        allow = []
        for method in self.http_method_names:
            if hasattr(self, method):
                allow.append(method.upper())
        r = self.render_to_response(None)
        r['Allow'] = ','.join(allow)
        return r
