import os
import csv
import urlparse
import warnings

from collections import defaultdict

from django.forms.forms import BaseForm
from django.conf import settings
from django.template import TemplateDoesNotExist, RequestContext
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import requires_csrf_token
from django.core.exceptions import ImproperlyConfigured


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


def get_redirect(redirects, path, full_uri):
    if full_uri in redirects:
        redirec = redirects[full_uri]
    elif path in redirects:
        redirec = redirects[path]
    else:
        return None

    target = redirec['target']
    status_code = redirec['status_code']

    response = HttpResponse('', status=status_code)
    response['Location'] = target or None

    return response

def scrape_redirects(redirect_path):
    lines = []
    for filename in os.listdir(redirect_path):
        if filename.endswith('.csv'):
            path = os.path.join(redirect_path, filename)
            reader = csv.DictReader(open(path, 'r'), fieldnames=['source', 'target', 'status_code'])
            for index, line in enumerate(reader):
                line['filename'] = filename
                line['line_number'] = index
                lines.append(line)
    return lines

def preprocess_redirects(lines, raise_errors=True):
    error_messages = defaultdict(list) 
    warning_messages = defaultdict(list)

    processed_redirects = {}
    for line in lines:
        source = line['source'].strip()
        target = (line['target'] or '').strip()
        if target:
            status_code = int(line['status_code'] or 301)
        else:
            # set status codes to 410 if no target url is given
            status_code = 410

        # Catch non 3xx or 410 status codes.
        if status_code < 300 or status_code > 399 and not status_code == 410:
            error_messages[source].append("ERROR: {filename}:{line_number} - Non 3xx/410 status code({line.status_code})".format(**line))

        # Catch duplicate declaration of source urls.
        if source in processed_redirects:
            first = processed_redirects[source]
            warning_messages[source].append("WARNING: {filename}:{line_number} -  Duplicate declaration of url".format(**line))
        processed_redirects[source] = {
                'target': target,
                'status_code': status_code,
                'filename': line['filename'],
                'line_number': line['line_number'],
                }

    def validate_redirect(source, redirect, with_slash=False):
        from_url = urlparse.urlparse(source)
        to_url = urlparse.urlparse(redirect['target'])
        if with_slash:
            if not to_url.path.endswith('/'):
                to_url = to_url._replace(path=to_url.path + '/')
            else:
                pass
        format_kwargs = {'source': source, 'from': from_url, 'to': to_url}
        format_kwargs.update(redirect)
        if redirect['target'] in processed_redirects or redirect['target'] == from_url.path:
            error_messages[source].append('ERROR: {filename}:{line_number} - Circular redirect: {source} => {target}'.format(**format_kwargs))
        elif urlparse.urljoin(from_url.geturl(), to_url.path) in processed_redirects and not redirect['status_code'] == 410:
            if not to_url.netloc:
                error_messages[source].append('ERROR: {filename}:{line_number} - Circular redirect: {source} => {target}'.format(**format_kwargs))
            elif to_url.netloc and not from_url.netloc:
                warning_messages[source].append('WARNING: {filename}:{line_number}: - Possible circular redirect if hosting on domain {to.netloc}: {source} => {target}'.format(**format_kwargs))
    
    # Check for circular redirects.
    for source, redirect in processed_redirects.items():
        validate_redirect(source, redirect)
        if settings.APPEND_SLASH:
            validate_redirect(source, redirect, with_slash=True)

    # Now that we're done, either raise an exception if an error was raised and
    # we are not just running in validation mode
    if error_messages and raise_errors:
        raise ImproperlyConfigured('There were errors while parsing redirects.  Run ./manage.py validate_redirects for error details')
    # Output warnings for all errors and warnings found.
    for messages in warning_messages.values() + error_messages.values():
        for message in messages:
            warnings.warn(message)

    return processed_redirects


class RedirectFallbackMiddleware(object):
    """
    This middleware handles 3xx redirects and 410s.

    Only 404 responses will be redirected, so if something else is returning a
    non 404 error, this middleware will not produce a redirect

    Redirects should be formatted in CSV files located in either
    `<project_path>/redirects/` or an absolute path declared in
    `settings.REDIRECTS_DIRECTORY`.

    CSV files should not contain any headers, and be in the format `source_url,
    target_url, status_code` where `status_code` is optional and defaults to 301.
    To issue a 410, leave off target url and status code.
    """
    def __init__(self, *args, **kwargs):
        raise_errors = kwargs.pop('raise_errors', True)
        super(RedirectFallbackMiddleware, self).__init__(*args, **kwargs)
        raw_redirects = self.get_redirects()
        self.redirects = preprocess_redirects(raw_redirects, raise_errors)

    def get_redirects(self):
        # Get redirect directory
        redirect_path = getattr(settings, 'REDIRECTS_DIRECTORY',
                               os.path.join(settings.PROJECT_PATH, '..', 'redirects'))

        # Crawl the REDIRECTS_DIRECTORY scraping any CSV files found
        lines = scrape_redirects(redirect_path)

        #redirects = preprocess_redirects(lines)
        return lines

    def process_response(self, request, response):
        if response.status_code != 404:
            return response  # No need to check for a redirect for non-404 responses.
        path = request.get_full_path()
        full_uri = request.build_absolute_uri()

        return get_redirect(self.redirects, path, full_uri) or response
