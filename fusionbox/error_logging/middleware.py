from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.middleware.common import _is_ignorable_404, _is_internal_request
from django.core.mail import mail_managers

from fusionbox.error_logging.models import Logged404


class FusionboxCommonMiddleware(object):
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
                is_internal = _is_internal_request(domain, referer)
                path = request.get_full_path()
                if referer and not _is_ignorable_404(path) and (is_internal or '?' not in referer):
                    logged_error, created = Logged404.objects.get_or_create(
                            domain=domain,
                            referer=referer,
                            is_internal=is_internal,
                            path=path,
                            )
                    if is_internal or created:
                        ua = request.META.get('HTTP_USER_AGENT', '<none>')
                        ip = request.META.get('REMOTE_ADDR', '<none>')
                        mail_managers("Broken %slink on %s" % ((is_internal and 'INTERNAL ' or ''), domain),
                            "Referrer: %s\nRequested URL: %s\nUser agent: %s\nIP address: %s\n" \
                                      % (referer, request.get_full_path(), ua, ip),
                                      fail_silently=True)
                return response
