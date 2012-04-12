import os
import os.path

from django.forms.forms import BaseForm
from django.conf import settings
from django.template import TemplateDoesNotExist, RequestContext
from django.http import Http404
from django.shortcuts import render_to_response
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def generic_template_finder_view(request, base_path=''):
    """
    Find a template based on the request url and render it.

    * ``/`` -> ``index.html``
    * ``/foo/`` -> ``foo.html`` OR ``foo/index.html``
    """
    path = base_path + request.path
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


class RedirectFallbackMiddleware(object):
    """
    Handles redirects.
    """
    @property
    def redirects(self):
        if not hasattr(self, '_redirects'):
            self._redirects = self.get_redirects()
        return self.get_redirects()

    def get_redirects(self):
        # Get redirect directory
        redirect_path = getattr(settings, 'REDIRECTS_DIRECTORY', os.path.join(settings.PROJECT_PATH, 'redirects'))
        if not os.path.isdir(redirect_path):
            return response

        csv_files = []
        for filename in os.listdir(redirect_path):
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(redirect_path, filename))

        redirects = {}
        for file in csv_files:
            reader = csv.DictReader(open(file, 'r'), fieldnames=['old', 'new', 'status_code'])
            for redirect in reader:
                old = redirect['old']
                new = redirect['new']
                status_code = redirect['status_code'] or 301

        return redirects

    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a redirect for non-404 responses.
        path = request.get_full_path()

        r, status_code = self.redirects.get(path, (None, None))
        if r is None and settings.APPEND_SLASH:
            # Try removing the trailing slash.
            r, status_code = self.redirects.get(path[:path.rfind('/')]+path[path.rfind('/')+1:], (None, None))
        if r is not None:
            # Handle different status codes
            return http.HttpResponsePermanentRedirect(r)
        # No redirect was found. Return the response.
        return response
