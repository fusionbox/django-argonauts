from django.db import models
from django.db.models.base import ModelBase

class MetaBehavior(ModelBase):
    '''
    Base Metaclass for Behaviors
    '''
    def __new__(cls, name, bases, attrs):
        new_class = super(MetaBehavior, cls).__new__(cls, name, bases, attrs)
        new_class.merge_parent_settings()
        if not new_class._meta.abstract:
            try:
                Behavior
                new_class.modify_schema()
            except NameError: # creating Behavior
                pass
        return new_class

class Behavior(models.Model):
    '''
    Base class for all Behaviors

    Behaviors are implemented through model inheritance, and support
    multi-inheritance as well.  Each behavior adds a set of default fields
    and/or methods to the model.  Field names can be customized like example B.

    EXAMPLE A
    class MyModel(FooBehavior):
        pass

    MyModel will have whatever fields FooBehavior adds with default field
    names.

    EXAMPLE B
    class MyModel(FooBehavior):
        class FooBehavior:
            bar_field_name = "bar"
            baz_field_name = "baz"

    MyModel will have the fields from FooBehavior added, but the field names
    will be "bar" and "baz" respectively.

    EXAMPLE C
    class MyModel(FooBehavior, BarBehavior):
        pass

    MyModel will have the fields from both FooBehavior and BarBehavior, each
    with default field names.  To customizing field names can be done just like
    it was in example B.

    '''
    class Meta:
        abstract = True
    __metaclass__ = MetaBehavior

    @classmethod
    def modify_schema(cls):
        """
        Hook for behaviors to modify their model class just after it's created
        """
        pass

    @classmethod
    def merge_parent_settings(cls):
        behaviors = [behavior.__name__ for behavior in cls.base_behaviors()]
        for parent in reversed(cls.mro()):
            for behavior in behaviors:
                parent_settings = dict(getattr(parent, behavior, object).__dict__)
                child_settings = getattr(cls, behavior, object).__dict__
                parent_settings.update(child_settings)
                getattr(cls, behavior).__dict__ = parent_settings

    @classmethod
    def base_behaviors(cls):
        behaviors = []
        for parent in cls.mro():
            if hasattr(parent, parent.__name__):
                behaviors.append(parent)
        return behaviors


class TimeStampable(Behavior):
    '''
    Base class for adding timestamping behavior to a model.

    Added Fields:
        Field 1:
            field: DateTimeField(auto_now_add=True)
            description: Timestamps set at the creation of the instance
            default_name: created_at
        Field 2:
            field: DateTimeField(auto_now_add=True)
            description: Timestamps set each time the save method is called on the instance
            default_name: updated_at

    '''
    class Meta:
        abstract = True

    class TimeStampable:
        created_at_field_name = 'created_at'
        updated_at_field_name = 'updated_at'

    @classmethod
    def modify_schema(cls):
        cls.add_to_class(cls.TimeStampable.created_at_field_name, models.DateTimeField(auto_now_add=True))
        cls.add_to_class(cls.TimeStampable.updated_at_field_name, models.DateTimeField(auto_now=True))
        super(TimeStampable, cls).modify_schema()


class SEO(Behavior):
    '''
    Base class for adding seo behavior to a model.

    Added Fields:
        Field 1:
            field: CharField(max_length = 255)
            description: Char field intended for use in html <title> tag.
            validation: Max Length 255 Characters
            default_name: seo_title
        Field 2:
            field: TextField()
            description: Text field intended for use in html <meta name="description"> tag.
            default_name: seo_description
        Field 3:
            field: TextField()
            description: Text field intended for use in html <meta name="keywords"> tag.
            validation: comma separated text strings
            default_name: seo_keywords

    '''
    class Meta:
        abstract = True

    class SEO:
        seo_title_field_name = 'seo_title'
        seo_description_field_name = 'seo_description'
        seo_keywords_field_name = 'seo_keywords'

    @classmethod
    def modify_schema(cls):
        cls.add_to_class(cls.SEO.seo_title_field_name, models.CharField(max_length = 255))
        cls.add_to_class(cls.SEO.seo_description_field_name, models.TextField())
        cls.add_to_class(cls.SEO.seo_keywords_field_name, models.TextField())
        super(SEO, cls).modify_schema()
