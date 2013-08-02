from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet


class JSONArgonautEncoder(DjangoJSONEncoder):
    """
    Handles encoding querysets and objects with ``to_json()``.
    """
    def default(self, o):
        try:
            return o.to_json()
        except AttributeError:
            pass

        if isinstance(o, QuerySet):
            return list(o)

        return super(JSONArgonautEncoder, self).default(o)
