================
Django-Argonauts
================

.. image:: https://api.travis-ci.org/fusionbox/django-argonauts.png
   :alt: Building Status
   :target: https://travis-ci.org/fusionbox/django-argonauts


Lightweight collection of helpers for Rest Views serving JSON.

------
Filter
------

You can serialize an object in JSON using ``|json`` filter. This is useful to
generate safe javascript:

.. code:: html

  {% load argonauts %}
  <script type="application/javascript">
    (function (document) {
        var object_list = {{ object_list|json }};
        var list = document.createElement("ul");
        for (var i in object_list) {
            if (object_list.hasOwnProperty(i)) {
                var item = document.createElement("li");
                item.appendChild(document.createTextNode(object_list[i]);
                list.appendChild(paragraph);
            }
        }
        document.body.appendChild(list);
    })(document);
  </script>


-----
Views
-----

``JsonResponseMixin``
=====================

``JsonResponseMixin`` implements ``render_to_response`` method that serialize an object into a
JSON response. Thus it is compatible with generic Django views:

.. code:: python

    from django.views.generic.detail import BaseDetailView
    from argonauts.views import JsonResponseMixin

    class JsonDetailView(JsonResponseMixin, BaseDetailView):
        """
        Detail view returning object serialized in JSON
        """
        pass


``JsonRequestMixin``
====================

``JsonRequestMixin`` gives access to the request data through ``data()`` method.

.. code:: python

    from django.views.generic.base import View
    from argonauts.views import JsonRequestMixin:
    from argonauts.http import JsonResponse

    class JsonView(JsonRequestMixin, View):
        def dispatch(self, *args, **kwargs):
            return JsonResponse(self.data())


``RestView``
============

``RestView`` is an abstract class. Subclasses should implement `auth()` for
handlering authentication. And at least one HTTP method.

``RestView`` implements `OPTIONS` http method, and inherits from ``JsonRequestMixin``.

.. code:: python

    from argonauts.views import RestView
    from django.core.exceptions import PermissionDenied

    class CrazyRestView(RestView):

        def auth(self, *args, **kwargs):
            try:
                if self.data()['username'] == 'admin':
                    return
            except KeyError:
                pass
            raise PermissionDenied
