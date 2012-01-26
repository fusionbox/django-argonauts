from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase

import copy
import datetime

class EmptyObject(object):
    pass


class MetaBehavior(ModelBase):
    """
    Base Metaclass for Behaviors
    """
    def __new__(cls, name, bases, attrs):
        """
        This allows declarative field definition in behaviors, just like in a
        regular model definition, while still allowing field names to be
        customized. Given a behavior::

            class FooBehavior(Behavior):
                some_column = IntegerField()

        A child class declaring::

            class MyModel(FooBehavior):
                class FooBehavior:
                    some_column = 'another_name'

        will be able to change the name of ``some_column`` to ``another_name``.

        To do this, we rip out all instances of :class:`model.Field`, and wait for
        :func:`Behavior.modify_schema` to add them back in once all config classes are
        merged.
        """
        found_django_meta_without_behavior = False
        for base in bases:
            if not issubclass(object, base):
                continue
            mro = base.mro()
            if found_django_meta_without_behavior and Behavior in mro:
                raise ImproperlyConfigured(u'Any model inheriting from a behavior cannot have a model which inherits from models.Model ahead of it in the parent classes')
            mro_modules = [klass.__module__ for klass in mro]
            if not 'fusionbox.behaviors' in mro_modules and models.Model in mro:
                found_django_meta_without_behavior = True

        declared_fields = {}

        if getattr(attrs.get('Meta', EmptyObject()), 'abstract', False):
            for property_name in attrs:
                if isinstance(attrs[property_name], models.Field):
                    declared_fields[property_name] = attrs[property_name]
            for field in declared_fields:
                del attrs[field]

        attrs['declared_fields'] = declared_fields

        new_class = super(MetaBehavior, cls).__new__(cls, name, bases, attrs)
        new_class.merge_parent_settings()
        if not new_class._meta.abstract:
            new_class.modify_schema()
        else:
            # make sure abstract classes have an inner settings class
            if not hasattr(new_class, new_class.__name__):
                setattr(new_class, new_class.__name__, EmptyObject())

        return new_class

class Behavior(models.Model):
    """
    Base class for all Behaviors

    Behaviors are implemented through model inheritance, and support
    multi-inheritance as well.  Each behavior adds a set of default fields
    and/or methods to the model.  Field names can be customized like example B.

    EXAMPLE A::

        class MyModel(FooBehavior):
            pass

    ``MyModel`` will have whatever fields ``FooBehavior`` adds with default
    field names.

    EXAMPLE B::

        class MyModel(FooBehavior):
            class FooBehavior:
                bar = 'qux'
                baz = 'quux'

    ``MyModel`` will have the fields from ``FooBehavior`` added, but the field
    names will be "qux" and "quux" respectively.

    EXAMPLE C::

        class MyModel(FooBehavior, BarBehavior):
            pass

    ``MyModel`` will have the fields from both ``FooBehavior`` and
    ``BarBehavior``, each with default field names.  To customizing field names
    can be done just like it was in example B.

    """
    class Meta:
        abstract = True
    __metaclass__ = MetaBehavior


    @classmethod
    def modify_schema(cls):
        """
        Hook for behaviors to modify their model class just after it's created
        """

        # Everything in declared_fields was pulled out by our metaclass, time
        # to add them back in
        for parent in cls.mro():
            try:
                declared_fields = parent.declared_fields
            except AttributeError:  # Model itself doesn't have declared_fields
                continue

            for name, field in declared_fields.iteritems():
                if not hasattr(cls, parent.__name__):
                    setattr(cls, parent.__name__, EmptyObject())
                try:
                    new_name = getattr(getattr(cls, parent.__name__), name)
                except AttributeError:
                    new_name = name
                    # put the column name in the behavior's config, so it's always there
                    setattr(getattr(parent, parent.__name__), name, name)
                if not hasattr(cls, new_name):
                    cls.add_to_class(new_name, copy.copy(field))


    @classmethod
    def merge_parent_settings(cls):
        """
        Every behavior's settings are stored in an inner class whose name
        matches its behavior's name. This method implements inheritance for
        those inner classes.
        """
        behaviors = [behavior.__name__ for behavior in cls.base_behaviors()]
        for parent in cls.mro():
            for behavior in behaviors:
                parent_settings = dict(getattr(parent, behavior, EmptyObject()).__dict__)
                child_settings = getattr(cls, behavior, EmptyObject()).__dict__
                parent_settings.update(child_settings)
                getattr(cls, behavior).__dict__ = parent_settings

    @classmethod
    def base_behaviors(cls):
        behaviors = []
        for parent in cls.mro():
            if hasattr(parent, parent.__name__):
                behaviors.append(parent)
        return behaviors


class Timestampable(Behavior):
    """
    Base class for adding timestamping behavior to a model.

    Added Fields:
        Field 1:
            field: DateTimeField(default=datetime.datetime.now)
            description: Timestamps set at the creation of the instance
            default_name: created_at
        Field 2:
            field: DateTimeField(auto_now=True)
            description: Timestamps set each time the save method is called on the instance
            default_name: updated_at

    """
    class Meta:
        abstract = True

    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)


class PublishableManager(models.Manager):
    """
    Manager for publishable behavior

    """
    def get_query_set(self):
        queryset = super(PublishableManager, self).get_query_set()
        return queryset.filter(is_published=True, publish_at__lte=datetime.datetime.now())

class Publishable(Behavior):
    """
    Base class for adding publishable behavior to a model.

    Added Fields:
        Field 1:
            field: DateTimeField(default=datetime.datetime.now, help_text='Selecting a future date will automatically publish to the live site on that date.')
            description: The date that the model instance will be made available to the PublishableManager's query set
            default_name: publish_at
        Field 2:
            field: DateTimeField(default=datetime.datetime.now, help_text='Selecting a future date will automatically publish to the live site on that date.')
            description: setting to False will automatically draft the instance, making it unavailable to the PublishableManager's query set
            default_name: is_published

    Added Managers:
        PublishableManager:
            description: overwritten get_query_set() function to only fetch published instances.
            name: published
            usage: 
                class Blog(Publishable):
                ...

                all_blogs = Blog.objects.all()
                published_blogs = Blog.published.all()

    """
    class Meta:
        abstract = True

    publish_at = models.DateTimeField(default=datetime.datetime.now, help_text='Selecting a future date will automatically publish to the live site on that date.')
    is_published = models.BooleanField(default=True, help_text='Unchecking this will take the entry off the live site regardless of publishing date')

    objects = models.Manager()
    published = PublishableManager()


class SEO(Behavior):
    """
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

    """
    class Meta:
        abstract = True

    seo_title = models.CharField(max_length = 255)
    seo_description = models.TextField()
    seo_keywords = models.TextField()

    def formatted_seo_data(self, title='', description = '', keywords = ''):
        """
        A string containing the model's SEO data marked up and ready for output
        in HTML.
        """
        from django.utils.safestring import mark_safe
        from django.utils.html import escape

        escaped_data = tuple(map(escape,
            (getattr(self, self.SEO.seo_title, title),
             getattr(self, self.SEO.seo_description, description),
             getattr(self, self.SEO.seo_keywords, keywords))))
        return mark_safe('<title>%s</title>\n<meta name="description" value="%s"/>\n<meta name="keywords" value="%s"/>' % escaped_data)
