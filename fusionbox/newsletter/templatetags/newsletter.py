"""
The newsletter template tag library

`{% load newsletter %}`

To use the newsletter template tags.  It is required
to have jquery.forms.js installed.

This is included with the installation under the `static` directory.

"""
from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.inclusion_tag("newsletter/newsletter_tag.html")
def newsletter():
    return {'render_html': True, 'render_js': True}

