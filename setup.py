from setuptools import setup

version = __import__('argonauts').get_version()

setup(name='django-argonauts',
      version=version,
      author="Fusionbox Inc",
      author_email="fusionbox@fusionbox.com",
      keywords="rest json views django helpers",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Topic :: Internet :: WWW/HTTP',
      ],

      packages=['argonauts'],

      test_suite='testproject.runtests',
)
