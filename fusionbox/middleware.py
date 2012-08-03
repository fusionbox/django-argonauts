import os
import csv
import urlparse
import warnings

from collections import defaultdict

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
        """
        Ensures that
        404 raised from view functions are not caught by
        ``GenericTemplateFinderMiddleware``.
        """
        if response.status_code == 404 and not getattr(request, '_generic_template_finder_middleware_view_found', False):
            try:
                return generic_template_finder_view(request)
            except Http404:
                return response
            except UnicodeEncodeError:
                return response
        else:
            return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Informs :func:`process_response` that there was a view for this url and that
        it threw a real 404.
        """
        request._generic_template_finder_middleware_view_found = True


def get_redirect(redirects, path, full_uri):
    if full_uri in redirects:
        redirect = redirects[full_uri]
    elif path in redirects:
        redirect = redirects[path]
    else:
        return None

    #target = redirec['target']
    #status_code = redirec['status_code']
    target = redirect.target
    status_code = redirect.status_code

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


class Redirect(object):
    """
    Encapulates all of the information about a redirect.
    """
    def __init__(self, source, target, status_code, filename, line_number):
        self.source = source.strip()
        self.parsed_source = urlparse.urlparse(self.source)
        self.target = (target or '').strip()
        self.parsed_target = urlparse.urlparse(self.target)
        if target:
            self.status_code = int(status_code or 301)
        else:
            self.status_code = 410

        self.filename = filename or ''
        self.line_number = line_number or ''

        self._errors = None

    def __str__(self):
        return self.source

    @property
    def errors(self):
        if self._errors is None:
            self.validate()
        return self._errors

    def is_valid(self):
        if self._errors is None:
            self.validate()
        return bool(self._errors)

    def add_error(self, field, message):
        if self._errors is None:
            self._errors = {}

    def validate(self):
        self._errors = self._errors or {}
        if self.status_code < 300 or self.status_code > 399 and not self.status_code == 410:
            self.add_error(
                    'status_code', 
                    "ERROR: {redirect.filename}:{redirect.line_number} - Non 3xx/410 status code({redirect.status_code})".format(redirect=self),
                    )


def preprocess_redirects(lines, raise_errors=True):
    """
    Takes a list of dictionaries read from the csv redirect files, creates
    Redirect objects from them, and validates the redirects, returning a
    dictionary of Redirect objects.
    """
    error_messages = defaultdict(list) 
    warning_messages = defaultdict(list)

    processed_redirects = {}
    for line in lines:
        redirect = Redirect(**line)
        # Runs internal validation on the redirect
        if not redirect.is_valid():
            for message in redirect.errors.values():
                error_messages[redirect.source] = message

        # Catch duplicate declaration of source urls.
        if redirect.source in processed_redirects:
            first = processed_redirects[redirect.source]
            warning_messages[redirect.source].append("WARNING: {filename}:{line_number} -  Duplicate declaration of url".format(**line))
        processed_redirects[redirect.source] = redirect

    def validate_redirect(redirect, with_slash=False):
        """
        Finds circular and possible circular redirects.
        """
        to_url = redirect.parsed_target
        if with_slash:
            if not to_url.path.endswith('/'):
                to_url = to_url._replace(path=to_url.path + '/')
            else:
                return
        if redirect.target in processed_redirects or redirect.target == redirect.parsed_source.path:
            error_messages[redirect.source].append('ERROR: {redirect.filename}:{redirect.line_number} - Circular redirect: {redirect.source} => {redirect.target}'.format(redirect=redirect))
        elif urlparse.urljoin(redirect.source, to_url.path) in processed_redirects and not redirect.status_code == 410:
            if not to_url.netloc:
                error_messages[redirect.source].append('ERROR: {redirect.filename}:{redirect.line_number} - Circular redirect: {redirect.source} => {redirect.target}'.format(redirect=redirect))
            elif to_url.netloc and not redirect.parsed_source.netloc:
                warning_messages[redirect.source].append('WARNING: {redirect.filename}:{redirect.line_number}: - Possible circular redirect if hosting on domain {redirect.parsed_target.netloc}: {redirect.source} => {redirect.target}'.format(redirect=redirect))
    
    # Check for circular redirects.
    for source, redirect in processed_redirects.items():
        validate_redirect(redirect)
        if settings.APPEND_SLASH:
            validate_redirect(redirect, with_slash=True)

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
    ``<project_path>/redirects/`` or an absolute path declared in
    ``settings.REDIRECTS_DIRECTORY``.

    CSV files should not contain any headers, and be in the format ``source_url,
    target_url, status_code`` where ``status_code`` is optional and defaults to 301.
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
