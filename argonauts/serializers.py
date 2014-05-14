from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.functional import Promise


class JSONArgonautsEncoder(DjangoJSONEncoder):
    """
    Handles encoding querysets and objects with ``to_json()``.
    """
    def default(self, o):
        if hasattr(o, 'to_json'):
            return o.to_json()

        if isinstance(o, QuerySet):
            return list(o)

        if isinstance(o, Promise) and hasattr(o, 'ljust'):
            # Force lazy string evaluation to prevent errors:
            # - not serializable as JSON without changes
            # - circular reference when converting into text using six.u()
            # While not clean, this seemed a safe method that does not assume
            # whether it's text or binary.
            # FIXME: find a cleaner solution and check if this is a Django bug
            return o.ljust(0)

        return super(JSONArgonautsEncoder, self).default(o)
