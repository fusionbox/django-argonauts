Auth
====

Intro
------
Authentication backend to allow you to insert your own user model into the
built in django authentication backend.

Installation and Usage
----------------------

-  Add ``'fusionbox.auth.backends.CustomModelBackend'`` to your ``AUTHENTICATION_BACKENDS`` setting in ``settings.py``
-  Set ``CUSTOM_USER_MODEL`` in your ``settings.py`` file to a fully qualified path to your custom user model.
