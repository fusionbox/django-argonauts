import os

from setuptools import setup
from setuptools.command.test import test as TestCommand

version = '1.0.0'


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # If we were to import outside of this function, pytest wouldn't be
        # installed yet.
        import pytest
        pytest.main(self.test_args)


setup(name='django-argonauts',
      version=version,
      author="Fusionbox, Inc.",
      author_email="programmers@fusionbox.com",
      url="https://github.com/fusionbox/django-argonauts",
      keywords="rest json views django helpers",
      description="A lightweight collection of JSON helpers for Django.",
      long_description=read_file('README.rst'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
      install_requires=['Django>=1.4'],
      packages=[
          'argonauts',
          'argonauts.templatetags',
      ],

      tests_require=['pytest-django', 'pytest'],
      cmdclass = {'test': PyTest},
)
