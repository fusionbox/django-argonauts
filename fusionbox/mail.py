"""
Markdown-templated email.

An email template looks like this::

    ---
    subject: Hello, {{user.first_name}}
    ---
    Welcome to the site.

When using :func:`send_markdown_mail`, its output is placed in a layout to
produce a full html document::

    <!DOCTYPE html>
    <html>
        <body>
            {{content}}
        </body>
    </html>

The default layout is specified in ``settings.EMAIL_LAYOUT``, but can be
overridden on a per-email basis.
"""

import re

import yaml
import markdown

from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.utils.safestring import mark_safe

import settings


def send_markdown_mail(template,
                       context,
                       to=None,
                       subject=None,
                       from_address=settings.SERVER_EMAIL,
                       layout=settings.EMAIL_LAYOUT):

    """
    The top-level email-sending function.
    """

    meta, raw, html = render_template(template, context, layout)

    # these let the template override the caller, should it be the
    # other way around?
    subject = meta.get('subject', subject)
    if not subject:
        raise Exception("Template didn't give a subject and neither did you")

    to = meta.get('to', to)
    if not subject:
        raise Exception("Template didn't give a to and neither did you")

    from_address = meta.get('from', from_address)

    msg = EmailMultiAlternatives(subject, raw, from_address, to)
    msg.attach_alternative(html, 'text/html')

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
