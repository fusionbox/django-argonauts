from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from debug_toolbar.panels import DebugPanel

class UserPanel(DebugPanel):
    """
    Panel that allows you to login as other recently-logged in users.
    """

    name = 'User'
    has_content = True

    def nav_title(self):
        return _('User')

    def url(self):
        return ''

    def title(self):
        return _('User')

    def nav_subtitle(self):
        return self.request.user.is_authenticated() and self.request.user

    def content(self):
        context = self.context.copy()
        context.update({
            'request': self.request,
        })

        return render_to_string('panel.html', context)

    def process_request(self, request):
        force_secure = not getattr(settings, 'DEBUG_TOOLBAR_USER_PANEL_SECURE', False)
        enabled = request.user.is_superuser or force_secure
        if not 'primary_user' in request.session and enabled:
            request.session['primary_user'] = request.user.id

    def process_response(self, request, response):
        self.request = request
