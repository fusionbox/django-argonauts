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

class NewsletterNode(template.Node):

    def __init__(self, render_html, render_js):
        self.render_js = render_js
        self.render_html = render_html

    def render(self, context):
        html = (self.render_html and
                '<div id="newsletter_container" class="newsletter"></div>'
                or '')
        js = (self.render_js and
"""<script type="text/javascript">
    $(document).ready(function() {
        var newsletter_container = $('#newsletter_container')
        $.get('%s', function(data) {
            newsletter_container.html(data);
        });
        $('#newsletter_signup_form').live('submit', function() {
            var self = $(this);
            $.ajax({
                url: self.attr('action'),
                type: self.attr('method'),
                data: self.serialize(),
                success: function(data) {
                    newsletter_container.fadeOut('slow', function() {
                        newsletter_container.html(data);
                        newsletter_container.fadeIn('slow');
                    });
                }
            });
            return false;
        });
    });
</script>
""" % reverse('newsletter:signup_form') or '')
        return (html + js)

@register.tag
def newsletter(parser, token):
    """
    The newsletter template tag will insert the necessary DOM elements to use
    the newsletter app correctly.

    To use:
        {% newsletter %}

    will create a `div` element with an id attribute `newsletter_container`

    This is where the ajax responses will place the returned HTML from the view.

    `{% newsletter %}` accepts one optional argument `{% newsletter nojs %}`

    This will only create an empty container while allowing the developer to place the
    javascript somewhere other than right after the div element.

    This is to fix an issue where some members of the DOM will not allow <script> elements.
    Also, it is "best practice" to place all <script> tags at the bottom before the </body>

    """
    return NewsletterNode(True, False if token.split_contents().pop() == 'nojs' else True)

@register.tag
def newsletter_js(parser, token):
    """
    {% newsletter_js %}

    Will output the javascript for the newsletter tag

    Probably will be used in conjunction with the `{% newsletter nojs %}`
    version of the tag
    """
    return NewsletterNode(False, True)

