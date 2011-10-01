from pprint import pprint

from django.db import models
from django.utils import unittest

from fusionbox.behaviors import *

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


def get_field_dict(model):
    """
    Make a dictionary of field name -> field class
    """
    return dict((field.name, field) for field in model._meta.fields)


class TestTimestampable(unittest.TestCase):
    def test_bare(self):
        class TestModel(TimeStampable):
            pass

        x = TestModel()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

    @unittest.expectedFailure
    def test_same_name(self):
        # I'm not sure if this is a problem with django or the behaviors
        class TestModel(TimeStampable):
            class TimeStampable:
                created_at_field_name = 'asdf'

        x = TestModel()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['asdf'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

    def test_custom(self):
        # This tests fails if the models share a name. see test_same_name
        class Test2Model(TimeStampable):
            class TimeStampable:
                created_at_field_name = 'asdf'

        x = Test2Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['asdf'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))



class TestSEO(unittest.TestCase):
    def test_bare(self):
        class Test3Model(SEO):
            pass

        x = Test3Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

    def test_override(self):
        class Test4Model(SEO):
            class SEO:
                seo_title_field_name = 'foo'

        x = Test4Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['foo'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

    def test_deep_inheritance(self):
        class ParentModel(SEO):
            class SEO:
                seo_title_field_name = 'foo'
        class Test7Model(ParentModel):
            class SEO:
                seo_keywords_field_name = 'asdfasdf'

        x = Test7Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['foo'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['asdfasdf'], models.TextField))

    def test_deep_inheritance_abstract(self):
        class ParentModelAbstract(SEO):
            class SEO:
                seo_title_field_name = 'foo'
            class Meta:
                abstract = True
        class Test8Model(ParentModelAbstract):
            class SEO:
                seo_keywords_field_name = 'asdfasdf'

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
                seo_keywords_field_name = 'asdfasdf'

        x = Test9Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['asdfasdf'], models.TextField))





class TestTwoBehaviors(unittest.TestCase):
    def test_bare(self):
        class Test5Model(SEO, TimeStampable):
            pass

        x = Test5Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['seo_title'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['updated_at'], models.DateTimeField))

    def test_override(self):
        class Test6Model(SEO, TimeStampable):
            class SEO:
                seo_title_field_name = 'asdf'
            class TimeStampable:
                updated_at_field_name = 'foo'
            pass

        x = Test6Model()

        fields = get_field_dict(x)

        self.assertTrue(isinstance(fields['asdf'], models.CharField))
        self.assertTrue(isinstance(fields['seo_description'], models.TextField))
        self.assertTrue(isinstance(fields['seo_keywords'], models.TextField))

        self.assertTrue(isinstance(fields['created_at'], models.DateTimeField))
        self.assertTrue(isinstance(fields['foo'], models.DateTimeField))


