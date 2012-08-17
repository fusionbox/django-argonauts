from django.db import models
from django.utils import unittest
from django.test import SimpleTestCase
from django.template import Template, Context
from django.http import HttpRequest as Request
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS, ImproperlyConfigured
import warnings

from fusionbox.middleware import get_redirect, preprocess_redirects
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


class TestRandomTags(SimpleTestCase):

    def test_random_order_empty(self):
        t = Template(
            '{% load random_order from fusionbox_tags %}'
            '{% random_order %}'
            '{% endrandom %}')
        self.assertHTMLEqual('', t.render(Context({})))

    def test_random_order_one(self):
        t = Template(
            '{% load random_order from fusionbox_tags %}'
            '{% load choice from fusionbox_tags %}'
            '{% random_order %}'
            '{% choice %}'
            '<p>Hello</p>'
            '{% endchoice %}'
            '{% endrandom %}')
        self.assertHTMLEqual('<p>Hello</p>', t.render(Context({})))

    def test_random_order_mixed_many(self):
        hello_count = goodbye_count = 0
        for x in xrange(0, 100):
            t = Template(
                '{% load random_order from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random_order %}'
                '<p>Candy</p>'
                '{% choice %}'
                '<p>Hello</p>'
                '{% endchoice %}'
                '<p>Bacon</p>'
                '{% choice %}'
                '<p>Goodbye</p>'
                '{% endchoice %}'
                '<p>Donuts</p>'
                '{% endrandom %}')
            try:
                self.assertHTMLEqual('<p>Candy</p><p>Hello</p><p>Bacon</p><p>Goodbye</p><p>Donuts</p>', t.render(Context({})))
                hello_count += 1
            except AssertionError:
                self.assertHTMLEqual('<p>Candy</p><p>Goodbye</p><p>Bacon</p><p>Hello</p><p>Donuts</p>', t.render(Context({})))
                goodbye_count += 1
        print "\n----------"
        print "`test_random_order_mixed_many` passes with:"
        print "Hello First: %s" % hello_count
        print "Goodbye First: %s" % goodbye_count
        print "----------"

    def test_random_order_seq_many(self):
        hello_count = goodbye_count = 0
        for x in xrange(0, 100):
            t = Template(
                '{% load random_order from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random_order %}'
                '{% choice %}'
                '<p>Hello</p>'
                '{% endchoice %}'
                '{% choice %}'
                '<p>Goodbye</p>'
                '{% endchoice %}'
                '{% endrandom %}')
            try:
                self.assertHTMLEqual('<p>Hello</p><p>Goodbye</p>', t.render(Context({})))
                hello_count += 1
            except AssertionError:
                self.assertHTMLEqual('<p>Goodbye</p><p>Hello</p>', t.render(Context({})))
                goodbye_count += 1
        print "\n----------"
        print "`test_random_order_seq_many` passes with:"
        print "Hello First: %s" % hello_count
        print "Goodbye First: %s" % goodbye_count
        print "----------"

    def test_random_choice_empty(self):
        with self.assertRaises(IndexError):
            Template(
                    '{% load random_choice from fusionbox_tags %}'
                    '{% random_choice %}'
                    '{% endrandom %}'
                    )

    def test_random_choice_one(self):
        t = Template(
                '{% load random_choice from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random_choice %}'
                '{% choice %}'
                '<p>Hello</p>'
                '{% endchoice %}'
                '{% endrandom %}'
                )
        self.assertHTMLEqual('<p>Hello</p>', t.render(Context({})))

    def test_random_choice_many(self):
        hello_count = goodbye_count = 0
        for x in xrange(0, 100):
            t = Template(
                    '{% load random_choice from fusionbox_tags %}'
                    '{% load choice from fusionbox_tags %}'
                    '{% random_choice %}'
                    '{% choice %}'
                    '<p>Hello</p>'
                    '{% endchoice %}'
                    '{% choice %}'
                    '<p>Goodbye</p>'
                    '{% endchoice %}'
                    '{% endrandom %}'
                    )
            try:
                self.assertHTMLEqual('<p>Hello</p>', t.render(Context({})))
                hello_count += 1
            except AssertionError:
                self.assertHTMLEqual('<p>Goodbye</p>', t.render(Context({})))
                goodbye_count += 1
        print "\n----------"
        print "`test_random_choice_many` passes with:"
        print "Hello: %s" % hello_count
        print "Goodbye: %s" % goodbye_count
        print "----------"


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

class TestRedirectMiddleware(unittest.TestCase):
    def setUp(self):
        raw_redirects = (
                {'source': '/foo/', 'target': '/bar/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': '/foo/302/', 'target': '/bar/', 'status_code': 302, 'filename': '', 'line_number':1},
                {'source': '/foo/303/', 'target': '/bar/', 'status_code': 303, 'filename': '', 'line_number':1},
                {'source': 'http://www.fusionbox.com/asdf/', 'target': '/foo/bar/', 'status_code': None, 'filename': '', 'line_number':1},
                )
        self.redirects = preprocess_redirects(raw_redirects)

    def test_basic_redirect(self):
        path = '/foo/'
        response = get_redirect(self.redirects, path, '')
        self.assertEqual(response['Location'], '/bar/')
        self.assertEqual(response.status_code, 301)

    def test_basic_redirect_with_domain(self):
        path = '/asdf/'
        full_path = 'http://www.fusionbox.com/asdf/'
        response = get_redirect(self.redirects, path, full_path)
        self.assertEqual(response['Location'], '/foo/bar/')
        self.assertEqual(response.status_code, 301)

    def test_302_redirect(self):
        path = '/foo/302/'
        response = get_redirect(self.redirects, path, '')
        self.assertEqual(response['Location'], '/bar/')
        self.assertEqual(response.status_code, 302)

    def test_303_redirect(self):
        path = '/foo/303/'
        response = get_redirect(self.redirects, path, '')
        self.assertEqual(response['Location'], '/bar/')
        self.assertEqual(response.status_code, 303)

    def test_410_gone(self):
        path = '/bar/'
        redirects = (
                {'source': '/bar/', 'target': None, 'status_code': None, 'filename': '', 'line_number':1},
            )
        response = get_redirect(preprocess_redirects(redirects), path, '')
        self.assertEqual(response.status_code, 410)

    def test_circular_redirect(self):
        redirects = (
                {'source': '/bar/', 'target': '/bar/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with self.assertRaises(ImproperlyConfigured):
            preprocess_redirects(redirects)
        redirects = (
                {'source': '/bar/', 'target': '/baz/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': '/foo/', 'target': '/bar/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with self.assertRaises(ImproperlyConfigured):
            preprocess_redirects(redirects)
        redirects = (
                {'source': '/foo/', 'target': '/bar/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': '/bar/', 'target': '/baz/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with self.assertRaises(ImproperlyConfigured):
            preprocess_redirects(redirects)

    def test_domain_circular_redirect(self):
        redirects = (
                {'source': 'http://www.fusionbox.com/bar/', 'target': '/bar/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with self.assertRaises(ImproperlyConfigured):
            preprocess_redirects(redirects)
        redirects = (
                {'source': 'http://www.fusionbox.com/bar/', 'target': '/foo/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': 'http://www.google.com/foo/', 'target': '/asdf/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        preprocess_redirects(redirects)
        redirects = (
                {'source': 'http://www.fusionbox.com/foo/', 'target': '/asdf/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': 'http://www.fusionbox.com/bar/', 'target': '/foo/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with self.assertRaises(ImproperlyConfigured):
            preprocess_redirects(redirects)
        redirects = (
                {'source': 'http://www.fusionbox.com/bar/', 'target': '/foo/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': 'http://www.fusionbox.com/foo/', 'target': '/asdf/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with self.assertRaises(ImproperlyConfigured):
            preprocess_redirects(redirects)

    def test_duplicate_redirect(self):
        redirects = (
                {'source': '/bar/', 'target': '/baz/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': '/bar/', 'target': '/asdf/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with warnings.catch_warnings(record=True) as w:
            preprocess_redirects(redirects)
            assert len(w)

    def test_possible_circular_redirect(self):
        redirects = (
                {'source': '/bar/', 'target': 'http://fusionbox.com/foo/', 'status_code': None, 'filename': '', 'line_number':1},
                {'source': '/foo/', 'target': '/asdf/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with warnings.catch_warnings(record=True) as w:
            preprocess_redirects(redirects)
            assert len(w)
        redirects = (
                {'source': '/foo/', 'target': 'http://fusionbox.com/foo/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        with warnings.catch_warnings(record=True) as w:
            preprocess_redirects(redirects)
            assert len(w)

    def test_cross_domain_redirect(self):
        redirects = (
                {'source': 'http://www.fusionbox.com/bar/', 'target': 'http://www.google.com/bar/', 'status_code': None, 'filename': '', 'line_number':1},
            )
        preprocess_redirects(redirects)
