from django.utils import unittest
from django.test import SimpleTestCase
from django.template import Template, Context, TemplateSyntaxError
from django.http import HttpRequest as Request
from django.core.exceptions import ImproperlyConfigured
import warnings

from fusionbox.middleware import get_redirect, preprocess_redirects

class TestObject(object):
    """
    dummy class for testing objects
    """
    pass

class TestRandomTags(SimpleTestCase):

    def test_random_invalid_args(self):
        with self.assertRaises(TemplateSyntaxError):
            Template(
                '{% load random from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random a %}'
                '{% endrandom %}')
        with self.assertRaises(TemplateSyntaxError):
            Template(
                '{% load random from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random 1.0 %}'
                '{% endrandom %}')

    def test_random_int_arg_none(self):
        t = Template(
            '{% load random from fusionbox_tags %}'
            '{% load choice from fusionbox_tags %}'
            '{% random 2 %}'
            '{% endrandom %}')
        self.assertHTMLEqual('', t.render(Context({})))

    def test_random_no_args_none(self):
        t = Template(
            '{% load random from fusionbox_tags %}'
            '{% load choice from fusionbox_tags %}'
            '{% random %}'
            '{% endrandom %}')
        self.assertHTMLEqual('', t.render(Context({})))

    def test_random_int_arg_one(self):
        t = Template(
            '{% load random from fusionbox_tags %}'
            '{% load choice from fusionbox_tags %}'
            '{% random 2 %}'
            '{% choice %}'
            '<p>Hello</p>'
            '{% endchoice %}'
            '{% endrandom %}')
        self.assertHTMLEqual('<p>Hello</p>', t.render(Context({})))

    def test_random_no_arg_one(self):
        t = Template(
            '{% load random from fusionbox_tags %}'
            '{% load choice from fusionbox_tags %}'
            '{% random %}'
            '{% choice %}'
            '<p>Hello</p>'
            '{% endchoice %}'
            '{% endrandom %}')
        self.assertHTMLEqual('<p>Hello</p>', t.render(Context({})))

    def test_random_many_limit(self):
        hello_count = goodbye_count = 0
        for x in xrange(0, 100):
            t = Template(
                '{% load random from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random 1 %}'
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
                self.assertHTMLEqual('<p>Candy</p><p>Hello</p><p>Bacon</p><p>Donuts</p>', t.render(Context({})))
                hello_count += 1
            except AssertionError:
                self.assertHTMLEqual('<p>Candy</p><p>Goodbye</p><p>Bacon</p><p>Donuts</p>', t.render(Context({})))
                goodbye_count += 1
        print "\n----------"
        print "`test_random_mixed_many_limit` passes with:"
        print "Hello First: %s" % hello_count
        print "Goodbye First: %s" % goodbye_count
        print "----------"

    def test_random_many(self):
        hello_count = goodbye_count = 0
        for x in xrange(0, 100):
            t = Template(
                '{% load random from fusionbox_tags %}'
                '{% load choice from fusionbox_tags %}'
                '{% random %}'
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
        print "`test_random_mixed_many` passes with:"
        print "Hello First: %s" % hello_count
        print "Goodbye First: %s" % goodbye_count
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
