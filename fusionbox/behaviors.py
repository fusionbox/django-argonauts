from django.db import models
from django.db.models.base import ModelBase

class MetaBehavior(ModelBase):
    def __new__(cls, name, bases, attrs):
        new_class = super(MetaBehavior, cls).__new__(cls, name, bases, attrs)
        print new_class.__name__, new_class._meta.abstract
        if not new_class._meta.abstract or False:
            for base in bases:
                if hasattr(base, 'merge_settings_with_child'):
                    base.merge_settings_with_child(new_class)
                if hasattr(base, 'add_fields_to_child'):
                    base.add_fields_to_child(new_class)

        return new_class

class BehaviorSettingsBase:
    pass

class Behavior(models.Model):
    class Meta:
        abstract = True
    __metaclass__ = MetaBehavior

class TimeStampable(Behavior):
    class Meta:
        abstract = True

    class TimeStampable:
        created_at_field_name = 'created_at'
        updated_at_field_name = 'updated_at'

    @classmethod
    def add_fields_to_child(cls, child):
        child.add_to_class(child.TimeStampable.created_at_field_name, models.DateTimeField(auto_now_add=True))
        child.add_to_class(child.TimeStampable.updated_at_field_name, models.DateTimeField(auto_now=True))

    @classmethod
    def merge_settings_with_child(cls, child):
        for name in dir(cls.TimeStampable):
            if name.startswith('__'):
                continue
            if not hasattr(child.TimeStampable, name):
                value = getattr(cls.TimeStampable, name)
                setattr(child.TimeStampable, name, value)

class SEO(Behavior):
    class SEO:
        seo_title_field_name = 'seo_title'
        seo_description_field_name = 'seo_description'
        seo_keywords_field_name = 'seo_keywords'

    class Meta:
        abstract = True

    @classmethod
    def add_fields_to_child(cls, child):
        child.add_to_class(child.SEO.seo_title_field_name, models.CharField(max_length = 255))
        child.add_to_class(child.SEO.seo_description_field_name, models.TextField())
        child.add_to_class(child.SEO.seo_keywords_field_name, models.TextField())

    @classmethod
    def merge_settings_with_child(cls, child):
        for name in dir(cls.SEO):
            if name.startswith('__'):
                continue
            if not hasattr(child.SEO, name):
                value = getattr(cls.SEO, name)
                setattr(child.SEO, name, value)
