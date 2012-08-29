from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.http import Http404

if 'pure_pagination' in settings.INSTALLED_APPS:
    from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
else:
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_permission_or_403(callable, *args, **kwargs):
    if not callable(*args, **kwargs):
        raise PermissionDenied


def get_object_page_or_throw(queryset, request, page_param='page', page_size_param='page_size', page_size_default=10):
    page = request.GET.get(page_param, 1)
    page_size = request.GET.get(page_size_param, page_size_default)

    try:
        if 'pure_pagination' in settings.INSTALLED_APPS:
            object_page = Paginator(queryset, page_size, request=request).page(page)
        else:
            object_page = Paginator(queryset, page_size).page(page)
    except PageNotAnInteger:
        raise Http404("The page parameter must be an integer")
    except EmptyPage:
        raise Http404("The page requested could not be found")

    return object_page

