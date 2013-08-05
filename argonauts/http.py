from django.http import HttpResponse

from argonauts import dumps


class JsonResponse(HttpResponse):
    """
    Takes a jsonable object and returns a response with its encoded value. Also
    sets the Content-Type to json.

    Usage::

        def aview(request):
            return JsonResponse({'foo': 1})
    """

    def __init__(self, context, *args, **kwargs):
        content = dumps(context)
        super(JsonResponse, self).__init__(content, *args, **kwargs)
        self['Content-Type'] = 'application/json'
