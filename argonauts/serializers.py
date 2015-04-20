from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.functional import Promise

try:
    from django.utils.encoding import force_text
except ImportError:
    # BBB: Django 1.4
    from django.utils.encoding import force_unicode as force_text


class JSONArgonautsEncoder(DjangoJSONEncoder):
    """
    Handles encoding querysets and objects with ``to_json()``.
    """
    def default(self, o):
        if hasattr(o, 'to_json'):
            return o.to_json()

        if isinstance(o, QuerySet):
            return list(o)

        if isinstance(o, Promise):
            return force_text(o)

        return super(JSONArgonautsEncoder, self).default(o)
