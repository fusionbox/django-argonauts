from __future__ import absolute_import

import calendar
import datetime

from django import forms

from fusionbox.forms.models import *


class MonthField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)
        self.choices = [('', ' -- ')] + \
                [(i, "%s - %s" % (i, calendar.month_name[i]))
                        for i in range(1, 13)]
        self.coerce = int

class FutureYearField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        number_of_years = kwargs.pop('number_of_years', 6)
        super(FutureYearField, self).__init__(*args, **kwargs)
        self.choices = [('', ' -- ')] + \
                [(i%100, str(i))
                        for i in range(datetime.datetime.now().year, datetime.datetime.now().year + number_of_years)]
        self.coerce = int
