from django import template

register = template.Library()

@register.filter_function
@template.defaultfilters.stringfilter
def starred(cc_number, star_char=u'\u25cf'):
    """
    {{cc_number|starred:'x'}}

    Outputs:
        xxxx xxxx xxxx 1234
    """
    value = '%s%s' % ((len(cc_number) - 4) * star_char, cc_number[-4:])
    return ' '.join([value[i:i+4] for i in range(0, len(value), 4)])

@register.filter_function
@template.defaultfilters.stringfilter
def cc_company(cc_number):
    """
    {{cc_number|cc_company}}

    Outputs:
        DISCOVER
    """
    import re
    cc_patterns = (
        (re.compile(r'^4[0-9]{12}(?:[0-9]{3})?$'), 'VISA'),
        (re.compile(r'^5[1-5][0-9]{14}$'), 'MASTERCARD'),
        (re.compile(r'^3[47][0-9]{13}$'), 'AMERICAN EXPRESS'),
        (re.compile(r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$'), 'DINERS CLUB'),
        (re.compile(r'^6(?:011|5[0-9]{2})[0-9]{12}$'), 'DISCOVER'),
        (re.compile(r'^(?:2131|1800|35\d{3})\d{11}$'), 'JCB')
    )
    for pattern, card in cc_patterns:
        if pattern.match(cc_number):
            return card
    return 'UNKNOWN'
