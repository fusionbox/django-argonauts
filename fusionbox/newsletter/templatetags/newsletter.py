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
def newsletter(js="js"):
    """
    Basic Usage:

        `{% newsletter %}`

    Using the `{% newsletter %}` tag renders whatever is set in
    `newsletter/newsletter_tag.html`.

    The default template will render a newsletter container to load
    the form and output the javascript necessary to POST the form with
    ajax.

    Alternative:

        `{% newsletter "nojs" %}`

    This will only render the newsletter container and will not output
    javascript.  This might be useful if you wish to place the javascript
    elsewhere on the page.  For instance, if you are outputting the form
    somewhere that <script> tags are not allowed.

    These templates may be overwritten:

        `newsletter/newsletter_tag.html`
        `newsletter/newsletter_container.html`
    """
    return {'render_html': True, 'render_js': js}

@register.inclusion_tag("newsletter/newsletter_js.html")
def newsletter_js():
    """
    `{% newsletter_js %}` === `{% include "newsletter/newsletter_js.html" %}`

    Only outputs the javascript for the newsletter tag.  Useful when you are
    using `{% newsletter "nojs" %}` and want to put the javascript somewhere
    else.
    """
    return {}
