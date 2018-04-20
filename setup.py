import os

from setuptools import setup
from setuptools.command.test import test as TestCommand

version = '1.2.1.dev0'


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(name='django-argonauts',
      version=version,
      author="Fusionbox, Inc.",
      author_email="programmers@fusionbox.com",
      url="https://github.com/fusionbox/django-argonauts",
      keywords="rest json views django helpers",
      description="A lightweight collection of JSON helpers for Django.",
      long_description=read_file('README.rst') + '\n\n' + read_file('CHANGELOG.rst'),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
      install_requires=['Django>=1.8'],
      packages=[
          'argonauts',
          'argonauts.templatetags',
      ],
)
