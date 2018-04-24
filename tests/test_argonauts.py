import re
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


class RenderingTestMixin(object):
    def render_dictionary(self):
        return self.render_data(SortedDict([
            ('a', 'foo'),
            ('b', EgObject('bar')),
        ]))

    def test_json_escapes_unsafe_characters(self):
        rendered = self.render_data("<script>alert('&XSS!');</script>")

        assert rendered == r'"\u003cscript\u003ealert(\u0027\u0026XSS!\u0027);\u003c/script\u003e"'

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


class TestJsonTemplateFilter(RenderingTestMixin):
    template = "{% load argonauts %}{{ data|json }}"

    def render_data(self, data):
        template = Template(self.template)
        return template.render(Context({'data': data}))


class TestJsonTemplateTag(RenderingTestMixin):
    def template(self, extra, **kwargs):
        template = "{% load argonauts %}{% json " + extra + " %}"
        return Template(template).render(Context(kwargs))

    def render(self, *args, **kwargs):
        return json.loads(self.template(*args, **kwargs))

    def render_data(self, data):
        return re.sub(
            r'^    ',
            '',
            re.sub(
                r'^{\s*"data":\s*(.*?)\s*}\s*$',
                r'\1',
                self.template('data=data', data=data),
                flags=re.DOTALL,
            ),
            flags=re.MULTILINE,
        )

    def test_array(self):
        assert self.render('a b c', a='1', b='2', c='3') == ["1","2","3"]

    def test_object(self):
        assert self.render('a=c b=b c=a', a='1', b='2', c='3') == {"a":"3","b":"2","c":"1"}

    def test_object_array(self):
        assert self.render('a b c=d d=c', a='1', b='2', c='3', d='4') == {"0":"1","1":"2","length":2,"c":"4","d":"3"}

    def test_object_array_length_override(self):
        assert self.render('a b c=d d=c length=e', a='1', b='2', c='3', d='4', e='ov') == {"0":"1","1":"2","length":"ov","c":"4","d":"3"}

    def test_none(self):
        assert self.render('') == None


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
