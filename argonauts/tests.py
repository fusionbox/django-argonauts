# coding=utf-8

import json
import datetime
import decimal

try:
    from django.utils import unittest
except ImportError:  # Django >= 1.7
    import unittest

try:
    from django.test.utils import override_settings
except ImportError: # Django < 1.4
    from override_settings import override_settings

import django
from django.template import Template, Context
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy
from django.test.client import RequestFactory

from argonauts import dumps
from argonauts.views import RestView


class TestObject(object):
    def __init__(self, value):
        self.value = value

    def to_json(self):
        return self.value


class TestJson(unittest.TestCase):
    def encode_and_decode(self, v):
        return json.loads(dumps(v))

    def assertion(self, a, b):
        self.assertEqual(self.encode_and_decode(a), b)

    def test_json_encoder(self):
        self.assertion([1], [1])
        self.assertion('a', 'a')
        self.assertion(12, 12)
        self.assertion(TestObject('foo'), 'foo')
        self.assertion([TestObject('foo'), TestObject(1)], ['foo', 1])
        self.assertion(TestObject([TestObject('a'), TestObject('b')]), ['a', 'b'])
        self.assertion(TestObject((TestObject('a'), TestObject('b'))), ['a', 'b'])
        self.assertion(decimal.Decimal('1.1'), '1.1')
        self.assertIn('2012-10-16', self.encode_and_decode(datetime.datetime(2012, 10, 16)))

    def test_lazy_promise(self):
        """There were issues with lazy string objects"""
        self.assertion([ugettext_lazy(u'foo')], [u'foo'])

    def test_queryset(self):
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
        except ImportError:
            from django.contrib.auth.models import User  # NOQA
        self.assertion(User.objects.filter(id=None), [])

    def test_attribute_error(self):

        class Klass(object):
            def __init__(self, i):
                self.value = i

            def to_json(self):
                # Value is an int() it doesn't have a pk
                return {'value': self.value.pk}

        with self.assertRaises(AttributeError):
            dumps(Klass(5))


class TestJsonTemplateFilter(unittest.TestCase):
    template = "{% load argonauts %}{{ data|json }}"

    def render_data(self, data):
        template = Template(self.template)
        return template.render(Context({'data': data}))

    def render_dictionary(self):
        return self.render_data(SortedDict([
            ('a', 'foo'),
            ('b', TestObject('bar')),
        ]))

    def test_json_escapes_unsafe_characters(self):
        rendered = self.render_data("<script>alert('&XSS!');</script>")

        self.assertEqual(rendered, '"\\u003cscript\\u003ealert(\'\\u0026XSS!\');\\u003c/script\\u003e"')

    @override_settings(DEBUG=True)
    def test_pretty_rendering_in_debug(self):
        rendered = self.render_dictionary()
        self.assertEqual(rendered, """{
    "a": "foo",
    "b": "bar"
}""")

    @override_settings(DEBUG=False)
    def test_compact_rendering_no_debug(self):
        rendered = self.render_dictionary()
        self.assertEqual(rendered, '{"a":"foo","b":"bar"}')


class TestRestViewEncoding(unittest.TestCase):
    factory = RequestFactory()
    hello = u'你好'

    def setUp(self):
        class View(RestView):
            auth = lambda *args, **kwargs: None
            testcase = None

            def post(self, *args, **kwargs):
                self.testcase.assertEqual(self.data()['foo'], self.testcase.hello)
                return self.render_to_response(self.data())

        self.viewfn = View.as_view(testcase=self)

    # See https://github.com/fusionbox/django-argonauts/pull/11#issuecomment-59742088
    @unittest.skipIf(django.VERSION < (1, 5),
                     "Django<1.5 only supports utf-8 payload encodings.")
    def test_request_encoding(self):
        data = '{"foo": "%s"}' % self.hello
        # I tried to manually encode the data as big5, but the RequestFactory
        # calls force_bytes on the data, which tries to decode the bytestring
        # as utf-8 and then reencode as big5.
        request = self.factory.post('/', data, content_type='application/json; charset=big5')
        response = self.viewfn(request)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['foo'], self.hello)

    def test_request_no_encoding(self):
        data = '{"foo": "%s"}' % self.hello
        request = self.factory.post('/', data, content_type='application/json')
        response = self.viewfn(request)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['foo'], self.hello)
