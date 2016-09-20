Changelog
=========

1.2.0 (unreleased)
------------------

- Add support for requests without a Content-Type header to JsonTestClient
- Remove support for old versions of Django (<= 1.7)


1.1.4 (2015-07-29)
------------------

- Tests mocked http requests don't always have charset


1.1.3 (2015-05-27)
------------------

- Fixed package (include the CHANGELOG in ``MANIFEST.in``)


1.1.2 (2015-05-27)
------------------

- Added ``JsonTestCase`` and ``JsonTestMixin``


1.1.1 (2015-04-20)
------------------

- Fixed package


1.1.0 (2015-04-20)
------------------

Cleanup:

- Dropped support for Django 1.3
- Added support for Python 3
- Updated documentation
- Switched testing to py.test
- Switched to zest.releaser


1.0.1 (2013-10-06)
------------------

- Fixed tests


1.0.0 (2013-07-05)
------------------

Initial release:

- Extracted from django-fusionbox
- Safe JSON Serializer
- Safe JSON template filter
- JSON Views
