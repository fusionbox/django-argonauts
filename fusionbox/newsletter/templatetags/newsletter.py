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
        $.get('%s', function(data) {
            $('#newsletter_container').html(data);
            $('#newsletter_signup_form').ajaxForm({
                'target': $('#newsletter_container'),
                'replaceTarget':true
            });
        });
    });
</script>
""" % reverse('newsletter:signup_form'))

@register.tag
def newsletter(parser, token):
    return NewsletterNode()
