import copy
import urllib

from django import forms
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.datastructures import SortedDict

class Headers(SortedDict):
    """
    Extension of djangos built in sorted dictionary class which iterates
    through the values rather than keys.
    """
    def __iter__(self):
        for name in self.keys():
            yield self[name]


class BaseChangeListForm(forms.Form):
    """
    Base class for SearchForm, FilterForm, and SortForm mixin classes for
    displaying, sorting, searching and filtering a model.
    """
    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        super(BaseChangeListForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.queryset is None:
            return self.model.objects.all()
        return self.queryset


class SearchForm(BaseChangeListForm):
    """
    Base form class for implementing searching on a model.

    # Example Usage

        class UserSearchForm(SearchForm):
            SEARCH_FIELDS = ('username', 'email', 'profile__role')
            model = User

        >>> form = UserSearchForm(request.GET, queryset=User.objects.filter(is_active=True))
        >>> form
        <accounts.forms.UserSearchForm object at 0x102ea18d0>
        >>> form.get_queryset()
        [<User: admin>, <User: test@test.com>, <User: test2@test.com>]

    `SEARCH_FIELDS` should be an iterable of valid django queryset field lookups.
    Lookups can span foreign key relationships.

    By default, searches will be case insensitive.  Set `CASE_SENSITIVE` to
    `True` to make searches case sensitive.
    """
    SEARCH_FIELDS = tuple()
    CASE_SENSITIVE = False
    q = forms.CharField(label="Search", required=False, min_length=3)

    def pre_search(self, qs):
        """
        Hook for modifying the queryset prior to the search
        """
        return qs

    def post_search(self, qs):
        """
        Hook for modifying the queryset after the search
        """
        return qs

    def get_queryset(self):
        qs = super(SearchForm, self).get_queryset()

        # Ensure that the form is valid
        if not self.is_valid():
            return qs

        qs = self.pre_search(qs)

        # Do Searching
        q = self.cleaned_data.get('q', None)
        if q:
            args = []
            for field in self.SEARCH_FIELDS:
                if self.CASE_SENSITIVE:
                    kwarg = {field + '__contains': q}
                else:
                    kwarg = {field + '__icontains': q}
                args.append(Q(**kwarg))
            qs = qs.filter(reduce(lambda x,y: x|y, args))

        qs = self.post_search(qs)

        return qs

class SortForm(BaseChangeListForm):
    """
    Base class for implementing sorting on a model.

    # Example Usage

    class UserSortForm(SortForm):
        HEADERS = (
            {'column': 'username', 'title': 'Username', 'sortable': True},
            {'column': 'email', 'title': 'Email Address', 'sortable': True},
            {'column': 'is_active', 'title': 'Active', 'sortable': False},
        model = User

    The sort field for this form defaults to a HiddenInput widget which should
    be output within your form to preserve sorting accross any form
    submissions.

    From within your template, this form gives access to very useful methods
    for producing table headers and links for progressive or singular
    searching.

    {{ form.headers }}
        - iterable of headers

    {{ header.title }}
        - title declared for this header

    {{ header.sortable }}
        - boolean for whether this header is sortable

    {{ header.active }}
        - boolean for whether the queryset is currently being sorted by this header

    {{ header.classes }}
        - list of css classes for this header. (active, ascending|descending)

    {{ header.priority }}
        - numeric index for which place this header is being used for ordering.

    {{ header.querystring }}
        - querystring for use with progressive sorting (sorting by multiple fields)

    {{ header.remove }}
        - querystring which can be used to remove this header from sorting

    {{ header.singular }}
        - querystring which can be used to sort only by this header
    """
    HEADERS = tuple()
    sort = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean_sort(self):
        cleaned_data = self.cleaned_data
        sorts = cleaned_data.get('sort', '').split('.')
        sorts = filter(bool, sorts)
        if not sorts:
            return []
        # Ensure that the sort parameter does not contain non-numeric sort indexes
        if not all([sort.strip('-').isdigit() for sort in sorts]):
            raise ValidationError("Unknown or invalid sort '{sort}'".format(sort=cleaned_data.get('sort', '')))
        sorts = [int(sort) for sort in sorts]
        # Ensure not un-sortable fields are being sorted by
        for sort in map(abs, sorts):
            header = self.HEADERS[sort-1]
            if not header['sortable']:
                raise ValidationError("Invalid sort parameter '{sort}'".format(sort=cleaned_data.get('sort', '')))
        # Ensure that all of our sort parameters are in range of our header values
        if any([abs(sort) > len(self.HEADERS) for sort in sorts]):
            raise ValidationError("Invalid sort parameter '{sort}'".format(sort=cleaned_data.get('sort', '')))

        return sorts

    def headers(self):
        headers = Headers()
        if self.is_valid():
            sorts = self.cleaned_data.get('sort', '')
        else:
            sorts = []
        params = copy.copy(self.data)
        #for index, column, title, sortable in self.SORT_CHOICES:
        for index, header in enumerate(self.HEADERS, 1):
            header = copy.copy(header)
            header['classes'] = []

            if header['sortable']:
                # compute sort parameter
                if sorts and abs(sorts[0]) == index:
                    header_sorts = [sorts[0] * -1] + sorts[1:]
                else:
                    header_sorts = [index] + filter(lambda x: not abs(x) == index, sorts)

                # handles form prefixing on querystring parameters
                sort_param = ((self.prefix or '') + '-sort').strip('-')

                # Progressive sort querystring
                params[sort_param] = '.'.join(map(str, header_sorts))
                header['querystring'] = urllib.urlencode(params)
                # Single sort querystring
                params[sort_param] = str(index)
                header['singular'] = urllib.urlencode(params)
                # Remove sort querystring
                params[sort_param] = '.'.join(map(str, header_sorts[1:]))
                header['remove'] = urllib.urlencode(params)

                # set sort priority display
                try:
                    header['priority'] = map(abs, sorts).index(index) + 1
                    header['classes'].append('active')
                    if index in sorts:
                        header['classes'].append('ascending')
                    else:
                        header['classes'].append('descending')
                except ValueError:
                    header['priority'] = None

            #headers.append(header)
            headers[header.get('name', header['column'])] = header
        return headers

    def pre_sort(self, qs):
        """
        Hook for doing pre-sort modification of the queryset
        """
        return qs

    def post_sort(self, qs):
        """
        Hook for doing post-sort modification of the queryset
        """
        return qs

    def get_queryset(self):
        qs = super(SortForm, self).get_queryset()

        # Ensure that the form is valid
        if not self.is_valid():
            return qs

        qs = self.pre_sort(qs)

        # Do Sorting
        sorts = self.cleaned_data.get('sort', [])
        order_by = []
        for sort in sorts:
            param = self.HEADERS[abs(sort)-1]['column']
            if sort < 0:
                param = '-' + param
            order_by.append(param)

        if order_by:
            qs = qs.order_by(*order_by)

        qs = self.post_sort(qs)

        return qs

class FilterForm(BaseChangeListForm):
    """
    Base class for implementing filtering on a model.

    # Example Usage

    class UserFilterForm(FilterForm):
        FILTERS = {
            'active': 'is_active',
            'staff': 'is_staff',
            'date_joined': 'date_joined__gte',
            }
        model = User

        active = forms.BooleanField(required=False)
        staff = forms.BooleanField(required=False)
        date_joined = forms.DateTimeField(required=False)

    `FILTERS` defines a mapping of form fields to queryset filters.
    """
    FILTERS = {}

    def pre_filter(self, qs):
        """
        Hook for doing pre-filter modification to the queryset
        """
        return qs

    def post_filter(self, qs):
        """
        Hook for doing post-filter modification to the queryset
        """
        return qs

    def get_queryset(self):
        qs = super(FilterForm, self).get_queryset()

        #  Ensure that the form is valid
        if not self.is_valid():
            return qs

        qs = self.pre_filter(qs)

        # Do filtering
        for field, column_name in self.FILTERS.items():
            if column_name and self.cleaned_data.get(field, ''):
                qs = qs.filter(**{column_name: self.cleaned_data[field]})

        qs = self.post_filter(qs)

        return qs
