from django.db import models
from django.utils import unittest
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS, ImproperlyConfigured

from fusionbox.behaviors import *


class TestObject(object):
    """
    dummy class for testing objects
    """
    pass


class TestBehaviorBase(unittest.TestCase):
    def test_meta_inheritance(self):
        class BaseBehavior(Behavior):
            class BaseBehavior:
                base_setting = 'a'

        class ChildBehavior(BaseBehavior):
            class BaseBehavior:
                child_base_setting = 'b'
            class ChildBehavior:
                child_setting = 'c'

        class ThirdBehavior(ChildBehavior):
            class BaseBehavior:
                base_setting = 'd'

        self.assertTrue(BaseBehavior.BaseBehavior.base_setting == 'a')

        self.assertTrue(ChildBehavior.BaseBehavior.base_setting == 'a')
        self.assertTrue(ChildBehavior.BaseBehavior.child_base_setting == 'b')
        self.assertTrue(ChildBehavior.ChildBehavior.child_setting == 'c')

        self.assertTrue(ThirdBehavior.BaseBehavior.base_setting == 'd')
        self.assertTrue(ThirdBehavior.ChildBehavior.child_setting == 'c')
        self.assertTrue(ThirdBehavior.BaseBehavior.child_base_setting == 'b')

    def test_declared_fields_doesnt_break_modelbase(self):
        # I'm not sure if this actually tests anything
        from django.core.management.validation import get_validation_errors
        from StringIO import StringIO

        class AppMod(object):
            __name__ = 'fusionbox.behaviors'
            class Sluggable(Behavior):
                slug = models.CharField(max_length=255)
                class Meta:
                    abstract = True
                    unique_together = (('slug',),)
            class AbstractSluggableModel(Sluggable, models.Model):
                class Meta:
                    unique_together = (('slug',),)
                    abstract = True
            class TheActualModel(AbstractSluggableModel):
                pass

        app_mod = AppMod()
        errors = StringIO()
        get_validation_errors(errors, app_mod)
        errors = errors.getvalue()
        self.assertTrue(errors == '')

    def test_sharing(self):
        class SharedModel1(SEO):
            class SEO:
                seo_title = 'name'
        class SharedModel2(SEO):
            class SEO:
                seo_title = 'asdf'

        get_field_dict(SharedModel1)['name']
        get_field_dict(SharedModel2)['asdf']

class TestMultiInheritMRO(unittest.TestCase):
    def test_improper_mro_multi_inheritance(self):
        class UpperBase(models.Model):
            pass

        with self.assertRaises(ImproperlyConfigured):
            class MultiInherited(UpperBase, Behavior):
                pass

    def test_proper_mro_multi_inheritance(self):
        class UpperBase(models.Model):
            pass

        class MultiInherited(Behavior, UpperBase):
            pass


def get_field_dict(model):
    """
    Make a dictionary of field name -> field class
    """
    return dict((field.name, field) for field in model._meta.fields)


class TestTimestampable(unittest.TestCase):
    def test_bare(self):
        class TestModel(Timestampable):
            pass

        x = TestModel()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

    #@unittest.expectedFailure
    #def test_same_name(self):
    #    # This is actually a problem with django, it won't let you have two
    #    # model classes with the same name in the same app
    #    class TestModel(Timestampable):
    #        class Timestampable:
    #            created_at = 'asdf'
    #
    #    x = TestModel()
    #
    #    fields = get_field_dict(x)
    #
    #    self.assertTrue(isinstance(fields['asdf'], models.DateTimeField))
    #    self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

    def test_custom(self):
        # This tests fails if the models share a name. see test_same_name
        class Test2Model(Timestampable):
            class Timestampable:
                created_at = 'asdf'

        x = Test2Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['asdf'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))


    def test_proxy(self):
        class TestProxyParentModel(Timestampable):
            pass
        class TestProxyProxyModel(TestProxyParentModel):
            class Meta:
                proxy = True
        field_names = [i.attname for i in TestProxyProxyModel._meta.fields]

        # without careful treatment, proxy models
        # could have fields added twice. verify that
        # there are no duplicate field names.
        self.assertTrue(len(set(field_names)) == len(field_names))


class TestValidation(unittest.TestCase):
    def test_bare(self):
        class ValidationTestModel(Validation):
            foo = models.CharField(max_length=1)

            def validate(self):
                raise ValidationError('Generic Error')

            def validate_foo(self):
                raise ValidationError('Foo Error')

        x = ValidationTestModel()

        self.assertFalse(x.is_valid())
        self.assertIsInstance(x.validation_errors(), dict)
        expected_errors = {
            NON_FIELD_ERRORS: [u'Generic Error'],
            'foo': [u'This field cannot be blank.', u'Foo Error']
        }
        self.assertEqual(x.validation_errors(), expected_errors)

        try:
            x.save()
            self.assertTrue(False)
        except ValidationError:
            pass

class TestMergedQuerySet(unittest.TestCase):
    def test_bare(self):
        from django.db.models.query import QuerySet
        class QuerySetTestModel_A(models.Model):
            class QuerySet(QuerySet):
                def foo(self):
                    pass

        class QuerySetTestModel_B(models.Model):
            class QuerySet(QuerySet):
                def bar(self):
                    pass

        class QuerySetTestModel_C(ManagedQuerySet, QuerySetTestModel_A, QuerySetTestModel_B):
            class QuerySet(QuerySet):
                def baz(self):
                    pass

        x = QuerySetTestModel_C()

        self.assertTrue(hasattr(x.QuerySet, 'foo'))
        self.assertTrue(hasattr(x.QuerySet, 'bar'))
        self.assertTrue(hasattr(x.QuerySet, 'baz'))


class TestSEO(unittest.TestCase):
    def test_bare(self):
        class Test3Model(SEO):
            pass

        x = Test3Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

    def test_overridden_field(self):
        class Test14Model(SEO):
            seo_title = models.IntegerField()

        x = Test14Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.IntegerField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

    def test_nonsense_config(self):
        class Test13Model(SEO):
            blahblah = 'foo'
            asdf = models.CharField(max_length=255)

        x = Test13Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))


    def test_override(self):
        class Test4Model(SEO):
            class SEO:
                seo_title = 'foo'

        x = Test4Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['foo'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

    def test_deep_inheritance(self):
        class ParentModel(SEO):
            class SEO:
                seo_title = 'foo'
        class Test7Model(ParentModel):
            class SEO:
                seo_keywords = 'asdfasdf'

        x = Test7Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['foo'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['asdfasdf'], models.TextField))

    def test_deep_inheritance_abstract(self):
        class ParentModelAbstract(SEO):
            class SEO:
                seo_title = 'foo'
            class Meta:
                abstract = True
        class Test8Model(ParentModelAbstract):
            class SEO:
                seo_keywords = 'asdfasdf'

        x = Test8Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['foo'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['asdfasdf'], models.TextField))

    def test_deep_inheritance_settings(self):
        class ParentModelNoSettings(SEO):
            class Meta:
                abstract = True
        class Test9Model(ParentModelNoSettings):
            class SEO:
                seo_keywords = 'asdfasdf'

        x = Test9Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['asdfasdf'], models.TextField))





class TestTwoBehaviors(unittest.TestCase):
    def test_bare(self):
        class Test5Model(SEO, Timestampable):
            pass

        x = Test5Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

    def test_override(self):
        class Test6Model(SEO, Timestampable):
            class SEO:
                seo_title = 'asdf'
            class Timestampable:
                updated_at = 'foo'
            pass

        x = Test6Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['asdf'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['foo'], models.DateTimeField))

    def test_new_behavior(self):
        class SeoAndTime(SEO, Timestampable):
            class SEO:
                seo_title = 'seo_and_time_title'
            pass

        class Test10Model(SeoAndTime):
            class Timestampable:
                updated_at = 'asdf'
            class SEO:
                seo_description = 'foo'

        x = Test10Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_and_time_title'], models.CharField))
        self.assertTrue(isinstance(fields['foo'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['asdf'], models.DateTimeField))

    def test_namespacings(self):
        class SeoAndTime2(SEO, Timestampable):
            class SEO:
                seo_title = 'seo_and_time_title'
            pass

        class Test11Model(SeoAndTime2):
            class Timestampable:
                seo_description = 'asdf'

        x = Test11Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_and_time_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

