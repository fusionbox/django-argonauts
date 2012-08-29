"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import urlparse

from django.test import LiveServerTestCase, Client
from django.core import mail

from fusionbox.error_logging.models import Logged404


class ErrorLoggingTest(LiveServerTestCase):
    def setUp(self):
        """
        Sets up two test clients, one which requests pages as internal
        requests, and another that functions as external requests
        """
        self.ic = Client(
                HTTP_REFERER=self.live_server_url + '/',
                HTTP_HOST=urlparse.urlparse(self.live_server_url).netloc,
                )
        self.ec = Client(
                HTTP_REFERER='http://www.google.com/',
                HTTP_HOST=urlparse.urlparse(self.live_server_url).netloc,
                )

    def test_internal_error_logging(self):
        """
        Tests internal 404s are logged correctly
        """
        self.assertFalse(Logged404.objects.filter(is_internal=True).exists())
        url = '/this-is-not-a-registered-url-so-it-404s/'
        self.ic.get(url)
        self.assertTrue(Logged404.objects.filter(is_internal=True).exists())

    def test_internal_404_sends_email_and_logs_database(self):
        """
        Ensures that visiting an internal broken link that an error email and a
        database entry are created
        """
        self.assertFalse(Logged404.objects.exists())
        c = Client(HTTP_REFERER=self.live_server_url + '/')
        url = '/this-is-not-a-registered-url-so-it-404s/'
        c.get(url)
        self.assertTrue(Logged404.objects.exists())
        self.assertEquals(len(mail.outbox), 1)

    def test_404_emails_on_all_internals(self):
        """
        Ensures that when an internal broken link is visited twice that a
        single database entry is generated and two error emails are generated
        """
        self.assertFalse(Logged404.objects.exists())
        url = '/this-is-not-a-registered-url-so-it-404s/'
        self.ic.get(url)
        self.assertEquals(Logged404.objects.count(), 1)
        self.assertEquals(len(mail.outbox), 1)
        self.ic.get(url)
        self.assertEquals(Logged404.objects.count(), 1)
        self.assertEquals(len(mail.outbox), 2)

    def test_external_error_logging(self):
        """
        Tests external 404s are logged correctly
        """
        self.assertFalse(Logged404.objects.filter(is_internal=False).exists())
        url = '/this-is-not-a-registered-url-so-it-404s/'
        self.ec.get(url)
        self.assertTrue(Logged404.objects.filter(is_internal=False).exists())

    def test_external_404_sends_email_and_logs_database(self):
        """
        Ensures that when an external broken link is visited twice that a
        single database entry is generated and single error emails are generated
        """
        self.assertFalse(Logged404.objects.exists())
        url = '/this-is-not-a-registered-url-so-it-404s/'
        self.ec.get(url)
        self.assertEquals(Logged404.objects.count(), 1)
        self.assertEquals(len(mail.outbox), 1)
        self.ec.get(url)
        self.assertEquals(Logged404.objects.count(), 1)
        self.assertEquals(len(mail.outbox), 1)
