from django.db import models

class QuerySetManager(models.Manager):
    """
    http://djangosnippets.org/snippets/734/

    Easy extending of the base manager without needing to define multiple
    managers and queryset classes.  
    
    Example Usage

    from django.db.models import QuerySet
    from fusionbox.db.models import QuerySetManager

    class Foo(models.Model):
        objects = QuerySetManager()
        class QuerySet(QuerySet):
            def published(self):
                return self.filter(is_published=True)
    """
    def get_query_set(self):
        return self.model.QuerySet(self.model)
    def __getattr__(self, attr, *args):
        return getattr(self.get_query_set(), attr, *args)
