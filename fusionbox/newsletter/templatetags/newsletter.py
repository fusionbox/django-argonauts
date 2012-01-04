"""
The newsletter template tag library

To load the tag in a Django template:

`{% load newsletter %}`

"""

from django import template
from django.core.urlresolvers import reverse

register = template.Library()

class NewsletterNode(template.Node):

    def render(self, context):
        return (
"""
<div id="newsletter_container" class="newsletter"></div>

<script type="text/javascript">
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
""" % reverse('newsletter:signup_form'))

@register.tag
def newsletter(parser, token):
    """
    The newsletter template tag will insert the necessary DOM elements to use
    the newsletter app correctly.

    To use:
        {% newsletter %}

    will create a `div` element with an id attribute `newsletter_container`

    This is where the ajax responses will place the returned HTML from the view.

    """
    return NewsletterNode()
