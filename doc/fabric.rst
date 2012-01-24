Fabric helpers
==============

Usage
-------------

A typical ``fabfile.py`` using :mod:`fusionbox.fabric_helpers` looks like::

    from fusionbox.fabric_helpers import *

    env.roledefs = {
            'dev': ['dev.fusionbox.com'],
            }

    env.project_name = 'foobar'
    env.short_name = 'fb'

    stage = roles('dev')(stage)

.. automodule:: fusionbox.fabric_helpers
  :members:
