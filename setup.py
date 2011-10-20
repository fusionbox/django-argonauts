#!/usr/bin/env python
import os
import re
from setuptools import setup

__doc__="""
Useful stuff for django

"""

version = '0.0.1'

setup(name='django-fusionbox',
    version=version,
    description='Useful stuff for django',
    author='Fusionbox programmers',
    author_email='programmers@fusionbox.com',
    keywords='django boilerplate',
    long_description=__doc__,
    url='https://github.com/fusionbox/django-fusionbox',
    packages=['fusionbox', 'fusionbox.templatetags', 'fusionbox.management', 'fusionbox.management.commands'],
    platforms = "any",
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    install_requires = ['BeautifulSoup'],
    requires = ['BeautifulSoup'],
)
