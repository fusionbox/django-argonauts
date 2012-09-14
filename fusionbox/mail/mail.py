"""
"""

import re
import os.path

import yaml
import markdown

from django.template.loader import get_template
from django.template import Context
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.utils.safestring import mark_safe

from django.conf import settings

try:
    EMAIL_LAYOUT = settings.EMAIL_LAYOUT
except AttributeError:
    EMAIL_LAYOUT = None

# Where should attachment locations be relative to?
# Allows you to say::
#
#       attachments: ['foo.pdf']
#
# In your email template.
EMAIL_ATTACHMENT_ROOT = getattr(
        settings,
        'EMAIL_ATTACHMENT_ROOT',
        os.path.join(settings.PROJECT_PATH, '../attachments/'))


def create_markdown_mail(template,
                       context,
                       to=None,
                       subject=None,
                       from_address=settings.SERVER_EMAIL,
                       layout=EMAIL_LAYOUT):
    """
    Creates a message from a markdown template and returns it as an
    ``EmailMultiAlternatives`` object.
    """
    if layout is None:
        raise ValueError('layout was not defined by settings.EMAIL_LAYOUT and none was provided')

    meta, raw, html = render_template(template, context, layout)

    # this lets the template override the caller
    subject = meta.get('subject', subject)
    if not subject:
        raise Exception("Template didn't give a subject and neither did you")

    to = meta.get('to', to)
    if not to:
        raise Exception("Template didn't give a to and neither did you")
    if isinstance(to, basestring):
        to = (to,)

    from_address = meta.get('from', from_address)

    msg = EmailMultiAlternatives(subject, raw, from_address, to)
    for attachment in meta.get('attachments', []):
        if isinstance(attachment, basestring):
            # filename
            msg.attach_file(os.path.join(EMAIL_ATTACHMENT_ROOT, attachment))
        else:
            msg.attach(*attachment)
    msg.attach_alternative(html, 'text/html')

    return msg


def send_markdown_mail(*args, **kwargs):
    """
    Wrapper around :func:`create_markdown_mail` that creates and sends the
    message in one step.
    """
    msg = create_markdown_mail(*args, **kwargs)
    return msg.send()


def render_template(template, context, layout):
    """
    With a markdown template, a context to render it in, and a layout to
    generate html from it, a 3-tuple of
    (metadata, markdown content, html content) is returned.
    """

    t = get_template(template)
    if not isinstance(context, Context):
        context = Context(context)

    if 'site' not in context and 'django.contrib.sites' in settings.INSTALLED_APPS:
        context['site'] = Site.objects.get_current()

    raw = t.render(context)
    meta, md = extract_frontmatter(raw)

    context.push()
    context['content'] = mark_safe(markdown.markdown(md, ['extra']))

    t = get_template(layout)
    html = t.render(context)

    context.pop()

    return (meta, md, html)


front_matter_re = re.compile('(\s*\n)?^---\n(.*)\n---$\n*', re.MULTILINE | re.DOTALL)


def extract_frontmatter(str):
    r"""
    Given a string with YAML style front matter, returns the parsed header and
    the rest of the string in a 2-tuple.

    >>> extract_frontmatter('---\nfoo: bar\n---\nbody content\n')
    ({'foo': 'bar'}, 'body content\n')
    """

    matches = front_matter_re.match(str)
    if matches:
        meta = yaml.load(matches.group(2))
    else:
        meta = {}
    return (meta, front_matter_re.sub('', str))
