import json

from django.http import HttpResponseRedirect, HttpResponse

from fusionbox.core.serializers.json import FusionboxJSONEncoder


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


class JsonResponse(HttpResponse):
    """
    Takes a jsonable object and returns a response with its encoded value. Also
    sets the Content-Type to json.

    Usage::

        def aview(request):
            return JsonResponse({'foo': 1})
    """


    def __init__(self, context, *args, **kwargs):
        content = json.dumps(context, default=FusionboxJSONEncoder)
        super(JsonResponse, self).__init__(content, *args, **kwargs)
        self['Content-Type'] = 'application/json'
