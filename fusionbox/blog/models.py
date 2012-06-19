import datetime
import collections

from django.db import models
from ckeditor.fields import RichTextField
from fusionbox import behaviors
from django_extensions.db.fields import AutoSlugField
from south.modelsinspector import add_introspection_rules
import tagging
import tagging.fields
import tagging.managers
from django.contrib.auth.models import User


from fusionbox.behaviors import AdminSearchableQueryset
from fusionbox.db.models import QuerySetManager

add_introspection_rules([], ['^ckeditor\.fields\.RichTextField'])
add_introspection_rules([], ["^tagging\.fields\.TagField"])


class Blog(behaviors.Timestampable, behaviors.SEO, behaviors.Publishable):
    slug = AutoSlugField(populate_from='title')
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, related_name='blogs')
    body = RichTextField()
    tags = tagging.fields.TagField()
    image = models.ImageField(blank=True, upload_to='blog_icons')

    objects = QuerySetManager()
    tagged = tagging.managers.ModelTaggedItemManager()

    def __unicode__(self):
        return self.title


    class QuerySet(AdminSearchableQueryset):
        search_fields = ('title', 'author__first_name', 'author__last_name', 'body', 'tags')

        def published(self):
            # duplicated from behaviors.Publishable because we need a method, not an extra manager
            return self.filter(is_published=True, publish_at__lte=datetime.datetime.now())

        def year_month_groups(self):
            """
            returns a dictionary of year -> (dictionary of month -> list of objects)
            """

            res = collections.defaultdict(lambda: collections.defaultdict(list))
            # this does too many queries, because all the tags are fetched. it
            # should use defer('tags'), but that causes a bug. See the
            # BlogTest.test_year_month_groups for a test that'll fail when
            # defer is used here.
            for obj in self:
                res[obj.created_at.year][obj.created_at.month].append(obj)

            # defaultdicts don't work right in django templates (.items # resolves as ['items'])
            # so convert to normal dicts
            for k in res:
                res[k] = dict(res[k])
            return dict(res)


    @models.permalink
    def get_absolute_url(self):
        return ('blog:fusionbox.blog.views.detail', (), {'slug': self.slug})
