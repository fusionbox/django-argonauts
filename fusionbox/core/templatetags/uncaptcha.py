from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True, name='uncaptcha')
def uncaptcha(context, form=None):
    """
    Renders the uncaptcha field for a form.
    """
    if form is None:
        field = context['form']['uncaptcha']
    else:
        field = form['uncaptcha']

    context['field'] = field

    rendered_uncaptcha = render_to_string('forms/fields/uncaptcha.html', context)
    context.pop()
    return rendered_uncaptcha
