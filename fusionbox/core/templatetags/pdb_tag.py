from django import template

register = template.Library()


@register.simple_tag(takes_context=True, name='pdb')
def pdb(context):
    import pdb
    pdb.set_trace()
