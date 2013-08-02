from setuptools import setup

version = __import__('argonauts').get_version()

setup(name='django-argonauts',
      version=version,
      author="Fusionbox, Inc.",
      author_email="programmers@fusionbox.com",
      keywords="rest json views django helpers",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ],
      install_requires=['Django>=1.4'],
      packages=[
          'argonauts',
          'argonauts.templatetags',
      ],

      test_suite='testproject.runtests',
)
