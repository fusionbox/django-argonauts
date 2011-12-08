Panels
======

Intro
------
`Django Debug Toolbar <http://pypi.python.org/pypi/django-debug-toolbar/>`_ allows hooking in extra panels.

User Panel
----------
The user panel is derived from `https://github.com/playfire/django-debug-toolbar-user-panel <https://github.com/playfire/django-debug-toolbar-user-panel/>`_.  The user panel allows for quick swapping between users.  This version has been modified to disable the panel unless the user logs in initially with a superuser.

Installation
^^^^^^^^^^^^

-  Add ``'fusionbox.panels.user_panel'`` to your ``INSTALLED_APPS``::

        INSTALLED_APPS = (
            ...
            'fusionbox.panels.user_panel',
            ...
        )
-  Add ``fusionbox.panels.user_panel.panels.UserPanel`` to the ``DEBUG_TOOLBAR_PANELS`` setting::
        DEBUG_TOOLBAR_PANELS = (
            ...
            'fusionbox.panels.user_panel.panels.UserPanel',
            ...
        )
-  Include ``fusionbox.panels.user_panel.urls`` somewhere in your url conf::
        urlpatterns = patterns('',
            ...
            url(r'', include('fusionbox.panels.user_panel.urls')),
            ...
        )
