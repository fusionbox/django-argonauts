import csv
from django.utils import unittest
from cStringIO import StringIO


class UnicodeCSVReaderTests(unittest.TestCase):

    def test_readrow_unicode(self):
        from fusionbox.unicode_csv import csv as fb_csv
        s = StringIO('"\xe2\x98\x83"')
        fb_reader = fb_csv.unicode_reader(s)
        self.assertEquals(fb_reader.next(), [u'\u2603'])

    def test_readrow_ascii(self):
        from fusionbox.unicode_csv import csv as fb_csv
        s = StringIO('"foo"')
        fb_result = fb_csv.unicode_reader(s).next()
        s.seek(0)
        csv_result = csv.reader(s).next()
        self.assertEquals(fb_result, csv_result)


class UnicodeCSVWriterTests(unittest.TestCase):

    def test_writerow_unicode(self):
        from fusionbox.unicode_csv import csv as fb_csv
        fb_result = StringIO()
        fb_writer = fb_csv.unicode_writer(fb_result)
        try:
            fb_writer.writerow([u'\u2603'])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), '\xe2\x98\x83\r\n')

    def test_writerow_ascii(self):
        from fusionbox.unicode_csv import csv as fb_csv
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = fb_csv.unicode_writer(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow(['foo'])
        try:
            fb_writer.writerow(['foo'])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())

    def test_writerow_bool(self):
        from fusionbox.unicode_csv import csv as fb_csv
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = fb_csv.unicode_writer(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow([True])
        try:
            fb_writer.writerow([True])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())

    def test_writerow_float(self):
        from fusionbox.unicode_csv import csv as fb_csv
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = fb_csv.unicode_writer(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow([1.1])
        try:
            fb_writer.writerow([1.1])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())

    def test_writerow_int(self):
        from fusionbox.unicode_csv import csv as fb_csv
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = fb_csv.unicode_writer(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow([1])
        try:
            fb_writer.writerow([1])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())
