from django.db import models

from ckeditor.fields import RichTextField
from fusionbox import behaviors
from django_extensions.db.fields import AutoSlugField
from south.modelsinspector import add_introspection_rules
import tagging, tagging.fields, tagging.managers

add_introspection_rules([], ['^ckeditor\.fields\.RichTextField'])
add_introspection_rules([], ["^tagging\.fields\.TagField"])

class Blog(behaviors.Timestampable, behaviors.SEO, behaviors.Publishable):
    slug = AutoSlugField(populate_from='title')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    body = RichTextField()
    tags = tagging.fields.TagField()

    objects = models.Manager()
    tagged = tagging.managers.ModelTaggedItemManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('blog.views.detail', (), {'slug': self.slug})
