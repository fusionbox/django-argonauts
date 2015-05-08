import json
import functools

from django.conf import settings
from django.test import Client, TestCase

__all__ = ['JsonTestClient', 'JsonTestCase']


class JsonTestClient(Client):
    def _json_request(self, method, url, data=None, *args, **kwargs):
        method_func = getattr(super(JsonTestClient, self), method)

        if method == 'get':
            encode = lambda x: x
        else:
            encode = json.dumps

        if data is not None:
            resp = method_func(url, encode(data), content_type='application/json', *args, **kwargs)
        else:
            resp = method_func(url, content_type='application/json', *args, **kwargs)

        assert resp['Content-Type'].startswith('application/json')

        charset = resp.charset or settings.DEFAULT_CHARSET
        resp.json = json.loads(resp.content.decode(charset))
        return resp

    def __getattribute__(self, attr):
        if attr in ('get', 'post', 'put', 'delete', 'trace', 'head', 'patch', 'options'):
            return functools.partial(self._json_request, attr)
        else:
            return super(JsonTestClient, self).__getattribute__(attr)


class JsonTestCase(TestCase):
    client_class = JsonTestClient
