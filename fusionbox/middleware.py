from django.forms.forms import BaseForm
from django.template import TemplateDoesNotExist, RequestContext
from django.http import Http404
from django.shortcuts import render_to_response
from django.core.exceptions import ImproperlyConfigured


def generic_template_finder_view(request):
    """
    Find a template based on the request url and render it.

    * ``/`` -> ``index.html``
    * ``/foo/`` -> ``foo.html`` OR ``foo/index.html``
    """
    path = request.path
    if not path.endswith('/'):
        path += '/'
    possibilities = (
            path.strip('/') + '.html',
            path.lstrip('/') + 'index.html',
            path.strip('/'),
            )
    for t in possibilities:
        try:
            return render_to_response(t, context_instance=RequestContext(request))
        except TemplateDoesNotExist:
            pass
    raise Http404('Template not found in any of %r' % (possibilities,))


class GenericTemplateFinderMiddleware(object):
    """
    Response middleware that uses :func:`generic_template_finder_view` to attempt to
    autolocate a template for otherwise 404 responses.

    This is only intended for development.  It will not work with DEBUG set to
    False.
    """
    def process_response(self, request, response):
        if settings.DEBUG is False:
            raise ImproperlyConfigured('You should not have \
                    GenericTemplateFinderMiddleware enabled with DEBUG set to \
                    False')

        if response.status_code == 404 and not getattr(request, '_generic_template_finder_middleware_view_found', False):
            try:
                return generic_template_finder_view(request)
            except Http404:
                return response
        else:
            return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Informs :func:`process_response` that there was a view for this url and that
        it threw a real 404.
        """
        request._generic_template_finder_middleware_view_found = True

class AutoErrorClassOnFormsMiddleware(object):
    """
    Middleware which adds an error class to all form widgets that have a field
    error. 
    
    Requires that views return a TemplateResponse object.

    Iterates through all values in the response context looking for anything
    which inherits from django's BaseForm.  Any fields with field specific
    errors have the class 'error' appended to their widget dictionary of
    attributes.
    """
    def process_template_response(self, request, response):
        for val in response.context_data.values():
            if issubclass(type(val), BaseForm):
                if val._errors:
                    for name in val._errors.keys():
                        if not name in val.fields:
                            continue
                        field = val.fields[name]
                        cls = field.widget.attrs.get('class', '')
                        if 'error' in cls:
                            continue
                        else:
                            cls += ' error'
                            cls = cls.strip()
                        field.widget.attrs['class'] = cls
        return response
