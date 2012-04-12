"""
Loads fusionbox.middleware.RedirectFallbackMiddleware to check for problems
"""

import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from fusionbox.middleware import RedirectFallbackMiddleware


redirect_path = getattr(settings, 'REDIRECTS_DIRECTORY', os.path.join(settings.PROJECT_PATH, '..', 'redirects'))

class Command(BaseCommand):
    help = "Loads all CSV redirect files in '{path}' and checks for problems".format(path=redirect_path)

    def handle(self, *args, **options):
        RedirectFallbackMiddleware()
