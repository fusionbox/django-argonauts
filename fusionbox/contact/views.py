from django.shortcuts import render
from django.contrib.sessions.backends.db import SessionStore
from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.conf import settings

from fusionbox.mail import send_markdown_mail
from fusionbox.http import HttpResponseSeeOther

from fusionbox.contact.forms import ContactForm
from fusionbox.contact.models import Recipient

def index(request, template='contact/index.html',
        email_template='mail/contact_form_submission.md',
        contact_form=ContactForm, extra_context={}):
    """
    View that displays the contact form and handles contact form submissions
    """
    env = extra_context

    if request.method == 'POST':
        form = contact_form(request, request.POST)
        if form.is_valid():
            submission = form.save()
            try:
                recipients = settings.CONTACT_FORM_RECIPIENTS
            except AttributeError:
                recipients = Recipient.objects.filter(is_active = True).values_list('email', flat=True)
            env = {}
            env['submission'] = submission
            env['host'] = request.get_host()
            if recipeints:
                send_markdown_mail(
                        email_template,
                        env,
                        to = recipients,)
            return HttpResponseSeeOther(reverse('contact_success'))
    else:
        form = contact_form(request)

    env['form'] = form

    return render(request, template, env)

def success(request, template='contact/success.html',
        extra_context={}):
    """
    Success page for contact form submissions
    """
    env = extra_context

    env['site_name'] = getattr(settings, 'SITE_NAME', 'Us')

    return render(request, template, env)
