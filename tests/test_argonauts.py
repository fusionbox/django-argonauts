import json
import datetime
import decimal
from django.utils.translation import ugettext_lazy, gettext_lazy

import pytest

from django.test.utils import override_settings
from django.template import Template, Context
try:
    from django.utils.datastructures import SortedDict
except ImportError:
    from collections import OrderedDict as SortedDict

from django.views.generic import View
from django.test import RequestFactory
from django.test.client import FakePayload

from argonauts import dumps
from argonauts.views import JsonRequestMixin


class EgObject(object):
    def __init__(self, value):
        self.value = value

    def to_json(self):
        return self.value


class TestJson(object):
    def encode_and_decode(self, v):
        return json.loads(dumps(v))

    def assertion(self, a, b):
        assert self.encode_and_decode(a) == b

    def test_json_encoder(self):
        self.assertion([1], [1])
        self.assertion('a', 'a')
        self.assertion(12, 12)
        self.assertion(EgObject('foo'), 'foo')
        self.assertion([EgObject('foo'), EgObject(1)], ['foo', 1])
        self.assertion(EgObject([EgObject('a'), EgObject('b')]), ['a', 'b'])
        self.assertion(EgObject((EgObject('a'), EgObject('b'))), ['a', 'b'])
        self.assertion(decimal.Decimal('1.1'), '1.1')
        assert '2012-10-16' in self.encode_and_decode(datetime.datetime(2012, 10, 16))

    def test_lazy_promise(self):
        """There were issues with lazy string objects"""
        self.assertion(ugettext_lazy(u'foo'), u'foo')
        self.assertion(gettext_lazy('foo'), 'foo')

    @pytest.mark.django_db
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

        with pytest.raises(AttributeError):
            dumps(Klass(5))


class TestJsonTemplateFilter(object):
    template = "{% load argonauts %}{{ data|json }}"

    def render_data(self, data):
        template = Template(self.template)
        return template.render(Context({'data': data}))

    def render_dictionary(self):
        return self.render_data(SortedDict([
            ('a', 'foo'),
            ('b', EgObject('bar')),
        ]))

    def test_json_escapes_unsafe_characters(self):
        rendered = self.render_data("<script>alert('&XSS!');</script>")

        assert rendered == '"\\u003cscript\\u003ealert(\'\\u0026XSS!\');\\u003c/script\\u003e"'

    @override_settings(DEBUG=True)
    def test_pretty_rendering_in_debug(self):
        rendered = self.render_dictionary()
        assert rendered == """{
    "a": "foo",
    "b": "bar"
}"""

    @override_settings(DEBUG=False)
    def test_compact_rendering_no_debug(self):
        rendered = self.render_dictionary()
        assert rendered == '{"a":"foo","b":"bar"}'


def test_json_resonse_mixin():
    class ViewClass(JsonRequestMixin, View):
        def post(self, request):
            return self.data()

    view = ViewClass.as_view()
    data = u'\N{SNOWMAN}'
    encoded_data = json.dumps(data).encode('utf-16')
    # BBB: Just use RequestFactory.generic in Django >= 1.5
    params = {
        'wsgi.input': FakePayload(encoded_data),
        'CONTENT_TYPE': 'application/json',
        'CONTENT_LENGTH': len(encoded_data),
    }
    request = RequestFactory().post('/', **params)
    request.encoding = 'utf-16'
    response = view(request)
    assert response == data
