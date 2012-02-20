Shortcuts
=========

The package ``'fusionbox.shortcuts'`` has various helper functions.


get_permission_or_403
-----

**get_permission_or_403(callable[, *args][, **kwargs])**
  Calls ``callable(*args, **kwargs)`` and raises a django ``PermissionDenied`` exception if callable returns ``False``.

  Required Argument:
  
  *  ``callable``: A callable that returns ``True`` or ``False`` and may optionally accept any number of named and unnamed arguments.


get_object_page_or_throw
------------------------


**get_object_page_or_throw(queryset, request[, page_param='page'][, page_size_param='page_size'][, page_size_default=10])**
  Paginates a queryset, returning the requested object page or returning an http response if an error occurs.

  Given a non-integer page number, a ``HttpResponseBadRequest`` will be returned.

  Given a page number greater than 1 that returns an empty page, a ``HttpResponseNotFound`` will be returned.

  It is up to you to return the HttpResponse.

  If ``pure_pagination`` is found in the ``INSTALLED_APPS``, this function will use ``pure_pagination.Paginator`` as opposed to the default ``django.core.paginator.Paginator``.

  Required Arguments:
  
  *  ``queryset``: The queryset of objects to be paginated
  *  ``request``: A request object, from which page and page_size values will be extracted

  Optional Arguments:
  *  ``page_param``: The url parameter name for the page number.  Defaults to ``page``
  *  ``page_size_param``: The url parameter name for the page size.  Defaults to ``page_size``
  *  ``page_size_param``: The default page size if no page size is present in the url.  Defaults to ``10``

