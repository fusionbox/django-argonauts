import StringIO
import copy
import csv
import urllib

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.datastructures import SortedDict

from fusionbox.forms.fields import UncaptchaField


class IterDict(SortedDict):
    """
    Extension of djangos built in sorted dictionary class which iterates
    through the values rather than keys.
    """
    def __iter__(self):
        for name in self.keys():
            yield self[name]


class BaseChangeListForm(forms.Form):
    """
    Base class for all ``ChangeListForms``.
    """
    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        """
        Takes an option named argument ``queryset`` as the base queryset used in
        the ``get_queryset`` method.
        """
        self.queryset = kwargs.pop('queryset', None)
        super(BaseChangeListForm, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """
        If the form was initialized with a queryset, this method returns that
        queryset.  Otherwise it returns ``Model.objects.all()`` for whatever
        model was defined for the form.
        """
        if self.queryset is None:
            return self.model.objects.all()
        return self.queryset


class SearchForm(BaseChangeListForm):
    """
    Base form class for implementing searching on a model.

    # Example Usage
    ::

        class UserSearchForm(SearchForm):
            SEARCH_FIELDS = ('username', 'email', 'profile__role')
            model = User

    ::

        >>> form = UserSearchForm(request.GET, queryset=User.objects.filter(is_active=True))
        >>> form
        <accounts.forms.UserSearchForm object at 0x102ea18d0>
        >>> form.get_queryset()
        [<User: admin>, <User: test@test.com>, <User: test2@test.com>]

    ``SEARCH_FIELDS`` should be an iterable of valid django queryset field lookups.
    Lookups can span foreign key relationships.

    By default, searches will be case insensitive.  Set ``CASE_SENSITIVE`` to
    ``True`` to make searches case sensitive.
    """
    SEARCH_FIELDS = tuple()
    CASE_SENSITIVE = False
    q = forms.CharField(label="Search", required=False, min_length=3)

    def pre_search(self, qs):
        """
        Hook for modifying the queryset prior to the search

        Runs prior to any searching and is run regardless form validation.
        """
        return qs

    def post_search(self, qs):
        """
        Hook for modifying the queryset after the search.  Will not be called
        on an invalid form.

        Runs only if the form validates.
        """
        return qs

    def get_queryset(self):
        """
        Constructs an '__contains' or '__icontains' filter across all of the
        fields listed in ``SEARCH_FIELDS``.
        """
        qs = super(SearchForm, self).get_queryset()

        qs = self.pre_search(qs)

        # Ensure that the form is valid
        if not self.is_valid():
            return qs

        # Do Searching
        q = self.cleaned_data.get('q', None).strip()
        if q:
            args = []
            for field in self.SEARCH_FIELDS:
                if self.CASE_SENSITIVE:
                    kwarg = {field + '__contains': q}
                else:
                    kwarg = {field + '__icontains': q}
                args.append(Q(**kwarg))
            if len(args) > 1:
                qs = qs.filter(reduce(lambda x, y: x | y, args))
            elif len(args) == 1:
                qs = qs.filter(args[0])

        qs = self.post_search(qs)

        return qs


class SortForm(BaseChangeListForm):
    """
    Base class for implementing sorting on a model.

    # Example Usage
    ::

        class UserSortForm(SortForm):
            HEADERS = (
                {'column': 'username', 'title': 'Username', 'sortable': True},
                {'column': 'email', 'title': 'Email Address', 'sortable': True},
                {'column': 'is_active', 'title': 'Active', 'sortable': False},
            model = User

    The sort field for this form defaults to a HiddenInput widget which should
    be output within your form to preserve sorting accross any form
    submissions.

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
            header = self.HEADERS[sort - 1]
            if not header['sortable']:
                raise ValidationError("Invalid sort parameter '{sort}'".format(sort=cleaned_data.get('sort', '')))
        # Ensure that all of our sort parameters are in range of our header values
        if any([abs(sort) > len(self.HEADERS) for sort in sorts]):
            raise ValidationError("Invalid sort parameter '{sort}'".format(sort=cleaned_data.get('sort', '')))

        return sorts

    def headers(self):
        """
        Returns an object with the following template variables:

        ``{{ form.headers }}``
            - access to the header

        ``{{ header.title }}``
            - title declared for this header

        ``{{ header.sortable }}``
            - boolean for whether this header is sortable

        ``{{ header.active }}``
            - boolean for whether the queryset is currently being sorted by this header

        ``{{ header.classes }}``
            - list of css classes for this header. (active, ascending|descending)

        ``{{ header.priority }}``
            - numeric index for which place this header is being used for ordering.

        ``{{ header.querystring }}``
            - querystring for use with progressive sorting (sorting by multiple fields)

        ``{{ header.remove }}``
            - querystring which can be used to remove this header from sorting

        ``{{ header.singular }}``
            - querystring which can be used to sort only by this header

        Example:
        ::
            {% for header in form.headers %}
              {% if header.priority %}
              <th scope="col" class="active {{ form.prefix }}-{{ header.column }}">
                <div class="sortoptions {{ header.classes|join:' ' }}">
                  <a class="sortremove" href="?{{ header.remove }}" title="Remove from sorting">X</a>
                  <span class="sortpriority" title="Sorting priority: {{ header.priority }}">{{ header.priority }}</span>
                  <a href="?{{ header.querystring }}" class="toggle" title="Toggle sorting"></a>
                </div>
              {% else %}
              <th scope="col" class="{{ form.prefix }}-{{ header.column }}">
              {% endif %}

              {% if header.sortable %}
                 <div class="text"><a href="?{{ header.querystring }}">{{ header.title }}</a></div>
              {% else %}
                 <div class="text">{{ header.title|safe }}</div>
              {% endif %}
              </th>
            {% endfor %}
        """
        headers = IterDict()
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
        Hook for doing pre-sort modification of the queryset.

        Runs regardless 
        """
        return qs

    def post_sort(self, qs):
        """
        Hook for doing post-sort modification of the queryset.  Will not be
        called on an invalid form.
        """
        return qs

    def get_queryset(self):
        """
        Returns an ordered queryset, sorted based on the values submitted in
        the sort parameter.
        """
        qs = super(SortForm, self).get_queryset()

        qs = self.pre_sort(qs)

        # Ensure that the form is valid
        if not self.is_valid():
            return qs

        # Do Sorting
        sorts = self.cleaned_data.get('sort', [])
        order_by = []
        for sort in sorts:
            param = self.HEADERS[abs(sort) - 1]['column']
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

    ::

        class UserFilterForm(FilterForm):
            FILTERS = {
                'active': 'is_active',
                'date_joined': 'date_joined__gte',
                'published': None, # Custom filtering
                }
            model = User

            PUBLISHED_CHOICES = (
                    ('', 'All'),
                    ('before', 'Before Today'),
                    ('after', 'After Today'),
                    )

            active = forms.BooleanField(required=False)
            date_joined = forms.DateTimeField(required=False)
            published = forms.ChoiceField(choices=PUBLISHED_CHOICES, widget=forms.HiddenInput())

            def pre_filter(self, queryset):
                published = self.cleaned_data.get('published')
                if published == '':
                    return queryset
                elif published == 'before':
                    return queryset.filter(published_at__lte=datetime.datetime.now())
                elif published == 'after':
                    return queryset.filter(published_at__gte=datetime.datetime.now())

    ``FILTERS`` defines a mapping of form fields to queryset filters.

    When displaying in the template, this form also provides you with url querystrings for all of your filters.

    ``form.filters`` is a dictionary of all of the filters defined on your form.

    In the example above, you could do the following in the template for display links for the published filter

    ::

        {% for choice in form.filters.published %}
            {% if choice.active %}
                {{ choice.display }} (<a href='?{{ choice.remove }}'>remove</a>)
            {% else %}
                <a href='?{{ choice.querystring }}'>{{ choice.display }}</a>
            {% endif %}
        {% endfor %}
    """
    FILTERS = {}

    @property
    def filters(self):
        """
        Generates a dictionary of filters with proper queryset links to
        maintian multiple filters.
        """
        filters = IterDict()
        for key in self.FILTERS:
            filter = IterDict()
            filter_param = ((self.prefix or '') + '-' + key).strip('-')

            for value, display in self.fields[key].choices:
                choice = {}
                choice['value'] = value
                choice['display'] = display

                # These are raw values so they must come from data, and be
                # coerced to strings
                choice['active'] = str(value) == self.data.get(filter_param, '')

                params = copy.copy(self.data)
                # Filter by this current choice
                params[filter_param] = value
                choice['querystring'] = urllib.urlencode(params)
                # remove this filter
                params[filter_param] = ''
                choice['remove'] = urllib.urlencode(params)

                filter[value] = choice
            filters[key] = filter
        return filters

    def pre_filter(self, qs):
        """
        Hook for doing pre-filter modification to the queryset

        Runs prior to any form filtering and is run regardless form validation.
        """
        return qs

    def post_filter(self, qs):
        """
        Hook for doing post-filter modification to the queryset.  This is also
        the place where any custom filtering should take place.

        Runs only if the form validates.
        """
        return qs

    def get_queryset(self):
        """
        Performs the following steps:
            - Returns the queryset if the form is invalid.
            - Otherwise, filters the queryset based on the filters defined on the
              form.
            - Returns the filtered queryset.
        """
        qs = super(FilterForm, self).get_queryset()

        qs = self.pre_filter(qs)

        #  Ensure that the form is valid
        if not self.is_valid():
            return qs

        # Do filtering
        for field, column_name in self.FILTERS.items():
            if column_name and self.cleaned_data.get(field, ''):
                qs = qs.filter(**{column_name: self.cleaned_data[field]})

        qs = self.post_filter(qs)

        return qs


def csv_getattr(obj, attr_name):
    """
    Helper function for CsvForm class that gets an attribute from a model with
    a custom exception.
    """
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        raise AttributeError('CsvForm: No \'{0}\' attribute found on \'{1}\' object'.format(
            attr_name,
            obj._meta.object_name,
            ))


def csv_getvalue(obj, path):
    """
    Helper function for CsvForm class that retrieves a value from an object
    described by a django-style query path.  The value can be a model field,
    property method, foreign key field, or instance method on the model.

    Example:
    ::
        >>> # full_name is a property method
        >>> csv_getvalue(instance, 'project__employee__full_name')
        u'David Sanders'
    """
    path = path.split('__', 1)
    attr_name = path[0]

    if obj is None:
        # Record object is empty, return None
        return None
    if len(path) == 1:
        # Return the last leaf of the path after evaluation
        attr = csv_getattr(obj, attr_name)

        if isinstance(attr, models.Model):
            # Attribute is a model instance.  Return unicode.
            return unicode(attr)
        elif hasattr(attr, '__call__'):
            # Attribute is a callable method.  Return its value when called.
            return attr()
        else:
            # Otherwise, assume attr is a simple value
            return attr
    elif len(path) == 2:
        # More of path is remaining to be traversed
        attr = csv_getattr(obj, attr_name)

        if attr is None:
            return None
        elif isinstance(attr, models.Model):
            # If attribute is a model instance, traverse into it
            return csv_getvalue(attr, path[1])
        else:
            raise AttributeError('CsvForm: Attribute \'{0}\' on object \'{1}\' is not a related model'.format(
                attr_name,
                obj._meta.object_name,
                ))


class CsvForm(BaseChangeListForm):
    """
    Base class for implementing csv generation on a model.

    Example:

    # Given this class...
    ::

        class UserFilterForm(FilterForm):
            model = User

            CSV_COLUMNS = (
                    {'column': 'id', 'title': 'Id'},
                    {'column': 'username', 'title': 'Username'},
                    {'column': 'email__domain_name', 'title': 'Email Domain'},
                    )

            FILTERS = {
                'active': 'is_active',
                'date_joined': 'date_joined__gte',
                'published': None, # Custom filtering
                }

            PUBLISHED_CHOICES = (
                    ('', 'All'),
                    ('before', 'Before Today'),
                    ('after', 'After Today'),
                    )

            active = forms.BooleanField(required=False)
            date_joined = forms.DateTimeField(required=False)
            published = forms.ChoiceField(choices=PUBLISHED_CHOICES, widget=forms.HiddenInput())

            def pre_filter(self, queryset):
                published = self.cleaned_data.get('published')
                if published == '':
                    return queryset
                elif published == 'before':
                    return queryset.filter(published_at__lte=datetime.datetime.now())
                elif published == 'after':
                    return queryset.filter(published_at__gte=datetime.datetime.now())

    ::

        >>> # This code in a repl will produce a string buffer with csv output for
        >>> # the form's queryset
        >>> form = UserFilterForm(request.GET, queryset=User.objects.all())
        >>> form.csv_content()
        <StringIO.StringO object at 0x102fd2f48>
        >>>


    ``CSV_COLUMNS`` defines a list of properties to fetch from each obj in the
    queryset which will be output in the csv content.  The ``column`` key defines
    the lookup path for the property.  This can lookup a field, property
    method, or method on the model which may span relationships.  The ``title``
    key defines the column header to use for that property in the csv content.

    The :func:`csv_content` method returns a string buffer with csv content for the
    form's queryset.
    """
    def csv_content(self):
        """
        Returns the objects in the form's current queryset as csv content.
        """
        if not hasattr(self, 'CSV_COLUMNS'):
            raise NotImplementedError('Child classes of CsvForm must implement the CSV_COLUMNS constant')

        # Get column fields and headers
        csv_columns = [i['column'] for i in self.CSV_COLUMNS]
        csv_headers = [i['title'].encode('utf-8') for i in self.CSV_COLUMNS]

        # Build data for csv writer
        csv_data = []
        for obj in self.get_queryset():
            csv_data.append([unicode(csv_getvalue(obj, column)).encode('utf-8') for column in csv_columns])

        # Create buffer with csv content
        content = StringIO.StringIO()
        writer = csv.writer(content)
        writer.writerow(csv_headers)
        writer.writerows(csv_data)
        content.seek(0)

        return content


class UncaptchaBase(object):
    """
    Base class for Uncaptcha forms to centralize the uncaptcha validation.
    """
    def clean_uncaptcha(self):
        value = self.cleaned_data['uncaptcha']
        if value is not None and not value == self.data.get('csrfmiddlewaretoken'):
            raise forms.ValidationError("Incorrect uncaptcha value")
        return value


class UncaptchaForm(UncaptchaBase, forms.Form):
    """
    Extension of ``django.forms.Form`` which adds an UncaptchaField to the
    form.
    """
    uncaptcha = UncaptchaField(required=False)
