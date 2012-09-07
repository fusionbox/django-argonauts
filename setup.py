#!/usr/bin/env python
import os
import re
from setuptools import setup, find_packages

__doc__="""
Useful stuff for django

"""

version = '0.0.2'

setup(name='django-fusionbox',
    version=version,
    description='Useful stuff for django',
    author='Fusionbox programmers',
    author_email='programmers@fusionbox.com',
    keywords='django boilerplate',
    long_description=__doc__,
    url='https://github.com/fusionbox/django-fusionbox',
    packages=find_packages(),
    package_data={
        'fusionbox': ['static/js/*'],
        'fusionbox.panels.user_panel': ['templates/*',],
        'fusionbox.newsletter': ['templates/newsletter/*',]
        },
    namespace_packages=['fusionbox'],
    platforms = "any",
    license='BSD',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    install_requires = ['BeautifulSoup', 'PyYAML', 'markdown'],
    requires = ['BeautifulSoup', 'PyYAML', 'markdown'],
)

