from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.middleware.common import _is_ignorable_404, _is_internal_request
from django.core.mail import mail_managers

from fusionbox.error_logging.models import Logged404, hash_args


class FusionboxCommonMiddleware(object):
    """
    Impliments ``django.middleware.commom.CommonMiddleware`` broken link email
    messages in a slightly different way.  Internal broken links still function
    the same.  External broken links will now only trigger error emails once.
    All broken links are also logged to the database.

    ``FusionboxCommonMiddleware`` is not compatable with the ``mysql`` database
    backend due to length limitations for the database index.

    To enable:

    * add ``fusionbox.error_logging`` to ``INSTALLED_APPS`` add
    * ``fusionbox.error_logging.middleware.FusionboxCommonMiddleware`` to ``MIDDLEWARE_CLASSES``

    This app also registers ``fusionbox.error_logging.admin.Logged404Admin`` to
    the django admin center.
    """
    def __init__(self, *args, **kwargs):
        if settings.SEND_BROKEN_LINK_EMAILS:
            raise ImproperlyConfigured('FusionboxCommonMiddleware may not be active while `SEND_BROKEN_LINK_EMAILS` is set to `True`')
        if not 'fusionbox.error_logging' in settings.INSTALLED_APPS:
            raise ImproperlyConfigured('FusionboxCommonMiddleware requires that `fusionbox.error_logging` be in `INSTALLED_APPS`')
        super(FusionboxCommonMiddleware, self).__init__(*args, **kwargs)

    def process_response(self, request, response):
        """
        Take over CommonMiddleware's error reporting for broken links.
        """
        if response.status_code == 404:
            if settings.FUSIONBOX_SEND_BROKEN_LINK_EMAILS and not settings.DEBUG:
                # If the referrer was from an internal link or a non-search-engine site,
                # send a note to the managers.
                domain = request.get_host()
                referer = request.META.get('HTTP_REFERER', None)
                is_internal = bool(_is_internal_request(domain, referer))
                path = request.get_full_path()
                if referer and not _is_ignorable_404(path) and (is_internal or '?' not in referer):
                    error_hash = hash_args(domain, referer, is_internal, path)
                    try:
                        Logged404.objects.get(hash=error_hash)
                        created = False
                    except Logged404.DoesNotExist:
                        Logged404.objects.create(
                            domain=domain,
                            referer=referer,
                            is_internal=is_internal,
                            path=path,
                            )
                        created = True

                    if is_internal or created:
                        ua = request.META.get('HTTP_USER_AGENT', '<none>')
                        ip = request.META.get('REMOTE_ADDR', '<none>')
                        mail_managers("Broken %slink on %s" % ((is_internal and 'INTERNAL ' or ''), domain),
                            "Referrer: %s\nRequested URL: %s\nUser agent: %s\nIP address: %s\n" \
                                      % (referer, request.get_full_path(), ua, ip),
                                      fail_silently=True)
        return response
