import os

from setuptools import setup

version = __import__('argonauts').get_version()

install_requires = ['Django>=1.3']
tests_require = []

try:
    django_version = __import__('django').VERSION
    if django_version < (1, 4):
        tests_require.append('django-override-settings')
except ImportError:
    pass

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
      install_requires=install_requires,
      tests_require=tests_require,
      packages=[
          'argonauts',
          'argonauts.templatetags',
      ],

      test_suite='testproject.runtests',
)
