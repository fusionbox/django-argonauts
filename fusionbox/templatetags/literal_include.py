"""
Literal Include template tag
based on Straight Include template tag by @HenrikJoreteg
https://gist.github.com/742160

Django templates don't give us any way to escape template tags.

So if you ever need to include client side templates for ICanHaz.js (or anything else that
may confuse django's templating engine) You can is this little snippet.

Just use it as you would a normal {% include %} tag. It just won't process the included text.

It assumes your included templates are in you django templates directory.

Usage:

{% load literal_include %}

{% literal_include "my_icanhaz_templates.html" %}

"""

from django import template
from django.conf import settings


register = template.Library()

@register.simple_tag
def literal_include(filename):
    for loader in template.loader.template_source_loaders:
        for i in loader.get_template_sources(filename, settings.TEMPLATE_DIRS):
            try:
                with open(i, 'r') as fp:
                    return fp.read()
            except IOError:
                pass
    raise template.base.TemplateDoesNotExist(filename)
