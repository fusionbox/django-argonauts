"""
Common form fields


These can also be accessed from ``fusionbox.forms``.
"""

import calendar
import datetime

from django import forms

class MonthField(forms.TypedChoiceField):
    """
    :class:`MonthField` is a :class:`TypedChoiceField` that selects a month.
    Its python value is a 1-indexed month number.
    """
    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)
        self.choices = [('', ' -- ')] + \
                [(i, "%s - %s" % (i, calendar.month_name[i]))
                        for i in range(1, 13)]
        self.coerce = int

class FutureYearField(forms.TypedChoiceField):
    """
    :class:`FutureYearField` is a :class:`TypedChoiceField` that selects a
    year a defined period in the future. Useful for credit card expiration
    dates.
    """

    def __init__(self, *args, **kwargs):
        number_of_years = kwargs.pop('number_of_years', 6)
        super(FutureYearField, self).__init__(*args, **kwargs)
        self.choices = [('', ' -- ')] + \
                [(i%100, str(i))
                        for i in range(datetime.datetime.now().year, datetime.datetime.now().year + number_of_years)]
        self.coerce = int
