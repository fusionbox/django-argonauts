import socket, datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = "Sends an email through the framework to an address specified on the command line."
    args = "<email email...>"
    can_import_settings = True

    def handle(self, *args, **kwargs):
        if not args:
            raise CommandError('You must provide at least one destination email')
        send_mail(
                subject='Test email from %s on %s' % (socket.gethostname(), datetime.datetime.now()),
                message='If you\'re reading this, it was successful.',
                from_email=getattr(settings, 'SERVER_EMAIL',
                                    getattr(settings, 'DEFAULT_FROM_EMAIL',
                                              'root@localhost')),
                recipient_list=args,
                fail_silently=False)
