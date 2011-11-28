from django.template import TemplateDoesNotExist, RequestContext
from django.http import Http404
from django.shortcuts import render_to_response


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
    """
    def process_response(self, request, response):
        if response.status_code == 404:
            return generic_template_finder_view(request)
        else:
            return response
