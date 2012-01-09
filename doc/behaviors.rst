Behaviors
=========

Usage Notes
-----------

Because behaviors are ultimately implemented using a special metaclass, any model inheritance involving behaviors must come before any other parent class which inherits from Django's built in metaclass.

    class MyBaseModel(models.Model):
        pass

    # Incorrect Usage
    class MyChildModel(MyBaseModel, Timestampable):
        pass

    # Correct Usage
    class MyChildModel(Timestampable, MyBaseModel):
        pass

Built in Behaviors
------------------

.. automodule:: fusionbox.behaviors
    :members: Behavior, Timestampable, SEO

.. autoclass:: fusionbox.behaviors.MetaBehavior
    :members: __new__

