#!/usr/bin/env python
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.testproject.settings")

import django
from django.test.utils import get_runner
from django.conf import settings

def runtests():
    if hasattr(django, 'setup'):
        # django >= 1.7
        django.setup()
    # Stolen from django/core/management/commands/test.py
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['argonauts'])
    sys.exit(bool(failures))
