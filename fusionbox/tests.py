from pprint import pprint

from django.db import models
from django.utils import unittest
from django.template import Template, Context
from django.http import HttpRequest as Request


from fusionbox.behaviors import *
from fusionbox.templatetags import fusionbox_tags


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
            asdf = models.CharField()

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


class TestHighlightHereTags(unittest.TestCase):
    request = Request()

    def test_simple_highlight_here(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here %}'
                     '<a href="/">Index</a>'
                     '{% endhighlight %}'
                     )
        self.request.path = '/'
        c = Context({'request':self.request})
        self.assertEqual('<a href="/" class="here">Index</a>', t.render(c))

    def test_multiple_simple_highlight_here(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here %}'
                     '<a class="" href="/">Index</a>'
                     '<a class="blog" href="/blog/">Blog</a>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/blog/'
        c = Context({'request':self.request})
        self.assertEqual('<a class="" href="/">Index</a>'
                         '<a class="blog here" href="/blog/">Blog</a>',t.render(c))

    def test_simple_highlight_here_with_class(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here yellow %}'
                     '<a href="/">Index</a>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/'
        c = Context({'request':self.request})
        self.assertEqual('<a href="/" class="yellow">Index</a>', t.render(c))

    def test_simple_highlight_here_with_multiple_classes(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here "yellow red" %}'
                     '<a href="/">Index</a>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/'
        c = Context({'request':self.request})
        self.assertEqual('<a href="/" class="yellow red">Index</a>', t.render(c))

    def test_multiple_highlight_here_with_class(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here yellow %}'
                     '<a class="" href="/">Index</a>'
                     '<a class="blog" href="/blog/">Blog</a>'
                     '{% endhighlight %}'
                     )
        self.request.path = '/blog/'
        c = Context({'request':self.request})
        self.assertEqual('<a class="" href="/">Index</a>'
                         '<a class="blog yellow" href="/blog/">Blog</a>', t.render(c))

    def test_highlight_here_with_variable_path(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here yellow test_object.path %}'
                     '<a class="" href="/">Index</a>'
                     '<a class="blog" href="/blog/">Blog</a>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/'
        test_object = TestObject()
        test_object.path = '/blog/'
        c = Context({'request':self.request, 'test_object' : test_object})
        self.assertEqual('<a class="" href="/">Index</a>'
                         '<a class="blog yellow" href="/blog/">Blog</a>', t.render(c))

    def test_deep_links(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here %}'
                     '<a class="" href="/">Index</a>'
                     '<a class="blog" href="/blog/">Blog</a>'
                     '<a class="blog" href="/blog/detail/foo/">Blog detail</a>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/blog/detail/foo/'
        c = Context({'request':self.request})
        self.assertEqual('<a class="" href="/">Index</a>'
                         '<a class="blog here" href="/blog/">Blog</a>'
                         '<a class="blog here" href="/blog/detail/foo/">Blog detail</a>', t.render(c))

class TestHighlightParentTags(unittest.TestCase):
    request = Request()

    def test_simple_highlight_here_parent(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here_parent %}'
                     '<li>'
                     '<a class="" href="/">Index</a>'
                     '</li>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/'
        c = Context({'request':self.request})
        self.assertEqual('<li class="here">'
                         '<a class="" href="/">Index</a>'
                         '</li>', t.render(c))

    def test_multiple_simple_highlight_here_parent(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here_parent %}'
                     '<li>'
                     '<a class="" href="/">Index</a>'
                     '</li>'
                     '<li><a class="blog" href="/blog/">Blog</a>'
                     '</li>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/blog/'
        c = Context({'request':self.request})
        self.assertEqual('<li>'
                         '<a class="" href="/">Index</a>'
                         '</li>'
                         '<li class="here">'
                         '<a class="blog" href="/blog/">Blog</a>'
                         '</li>', t.render(c))

    def test_simple_highlight_here_parent_with_class(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here_parent yellow %}'
                     '<li>'
                     '<a class="" href="/">Index</a>'
                     '</li>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/'
        c = Context({'request':self.request})
        self.assertEqual('<li class="yellow">'
                         '<a class="" href="/">Index</a>'
                         '</li>', t.render(c))

    def test_multiple_highlight_here_parent_with_class(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here_parent yellow %}'
                     '<li>'
                     '<a class="" href="/">Index</a>'
                     '</li>'
                     '<li class="blog">'
                     '<a class="blog" href="/blog/">Blog</a></li>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/blog/'
        c = Context({'request':self.request})
        self.assertEqual('<li>'
                         '<a class="" href="/">Index</a>'
                         '</li>'
                         '<li class="blog yellow">'
                         '<a class="blog" href="/blog/">Blog</a>'
                         '</li>', t.render(c))

    def test_highlight_here_parent_with_variable_path(self):
        t = Template('{% load fusionbox_tags %}'
                     '{% highlight_here_parent yellow test_object.path %}'
                     '<li>'
                     '<a class="" href="/">Index</a>'
                     '</li>'
                     '<li class="blog">'
                     '<a class="blog" href="/blog/">Blog</a></li>'
                     '{% endhighlight %}'
                    )
        self.request.path = '/'
        test_object = TestObject()
        test_object.path = '/blog/'
        c = Context({'request':self.request, 'test_object' : test_object})
        self.assertEqual('<li>'
                         '<a class="" href="/">Index</a>'
                         '</li>'
                         '<li class="blog yellow">'
                         '<a class="blog" href="/blog/">Blog</a>'
                         '</li>', t.render(c))

