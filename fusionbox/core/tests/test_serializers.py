import json
import datetime
import decimal

from django.utils import unittest

from fusionbox.core.serializers import FusionboxJSONEncoder


class TestObject(object):
    def __init__(self, value):
        self.value = value

    def to_json(self):
        return self.value


class TestJson(unittest.TestCase):
    def encode_and_decode(self, v):
        return json.loads(json.dumps(v, cls=FusionboxJSONEncoder))

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

    def test_queryset(self):
        from django.contrib.auth.models import User
        self.assertion(User.objects.filter(id=None), [])
