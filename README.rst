================
Django-Argonauts
================

.. image:: https://api.travis-ci.org/fusionbox/django-argonauts.png
   :alt: Building Status
   :target: https://travis-ci.org/fusionbox/django-argonauts


A lightweight collection of JSON helpers for Django. Includes a template filter
for safely outputting JSON, views that encode and decode JSON, and a helper for
writing simple REST views.

A special JSON encoder is used to serialize QuerySets and objects with
``to_json`` methods.

------
Filter
------

You can serialize an object in JSON using the ``|json`` filter. This is useful
to generate safe JavaScript:

.. code:: html

  {% load argonauts %}
  <script type="application/javascript">
    (function () {
        var object_list = {{ object_list|json }};
        // do something with object_list
    })();
  </script>

``|json`` is safe to use anywhere in XML or XHTML except in an attribute. It's
important to use this tag rather than dumping the output of ``json.dumps`` into
HTML, because an attacker could output a closing tag and effect an XSS attack.
For example, if we output ``json.dumps("</script><script>console.log('xss');
//")`` in template like this:

.. code:: html

  <script>
    var somedata = {{ somedata_as_json|safe }};
  </script>

We get:

.. code:: html

  <script>
    var somedata = "</script>
  <script>
    console.log('xss'); //";
  </script>

This allows the attacker to inject their own JavaScript. The ``|json`` tag
prevents this by encoding the closing ``</script>`` tag with JSON's unicode
escapes. If we output ``{{ somedata|json }}``, we get:

.. code:: html

  <script>
    var somedata = "\u0060xscript\u0062x\u0060xscript\u0062xconsole.log('xss');//";
  </script>

It also escapes ampersands in order to generate valid XML. For example, with the value
``foo & bar``:

.. code:: xml

  <document><json>{{ value|json }}</json></document>
  <!-- Results in valid XML:
  <document><json>"foo \u0038x bar"</json></document>
  -->

-----
Views
-----

``JsonResponseMixin``
=====================

``JsonResponseMixin`` implements ``render_to_response`` method that serializes
an object into a JSON response. Thus it is compatible with generic Django
views:

.. code:: python

    from django.db import models
    from django.views.generic.detail import BaseDetailView
    from argonauts.views import JsonResponseMixin

    class Blog(models.Model):
        title = models.CharField(max_length=255)
        body = models.TextField()

        def to_json(self):
            return {
                'title': self.title,
                'body': self.body,
            }

    class BlogDetailView(JsonResponseMixin, BaseDetailView):
        """
        Detail view returning object serialized in JSON
        """
        model = Blog


``JsonRequestMixin``
====================

``JsonRequestMixin`` gives access to the request data through ``data()`` method.

.. code:: python

    from django.views.generic.base import View
    from argonauts.views import JsonRequestMixin:
    from argonauts.http import JsonResponse

    class EchoView(JsonRequestMixin, View):
        def dispatch(self, *args, **kwargs):
            return JsonResponse(self.data())


``RestView``
============

``RestView`` is an abstract class. Subclasses should implement `auth()`, for
handling authentication, and at least one HTTP method.

``RestView`` implements `OPTIONS` http method, and inherits from
``JsonRequestMixin`` and ``JsonResponseMixin``.

.. code:: python

    from django.core.exceptions import PermissionDenied
    from argonauts.views import RestView
    from .utils import get_action

    class CrazyRestView(RestView):
        def auth(self, *args, **kwargs):
            if not self.request.user.is_superuser:
                raise PermissionDenied

        def post(self, *args, **kwargs):
            action = kwargs.pop('action')
            action_func = get_action(action)
            return self.render_to_response(action_func(self.data()))
