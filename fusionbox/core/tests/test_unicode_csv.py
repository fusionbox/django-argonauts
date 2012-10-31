import csv
from django.utils import unittest
from cStringIO import StringIO
from fusionbox.unicode_csv import UnicodeReader, UnicodeWriter


class UnicodeDictReaderTests(unittest.TestCase):

    def test_unicode_fieldnames(self):
        from fusionbox.unicode_csv import UnicodeDictReader
        s = StringIO('"\xe2\x98\x83"')
        fb_reader = UnicodeDictReader(s)
        self.assertEquals(fb_reader.fieldnames, [u'\u2603'])

    def test_readrow_unicode(self):
        from fusionbox.unicode_csv import UnicodeDictReader
        s = StringIO('"test"\r\n"\xe2\x98\x83"')
        fb_reader = UnicodeDictReader(s)
        self.assertEquals(fb_reader.next(), {'test': u'\u2603'})


class UnicodeDictWriterTests(unittest.TestCase):

    def test_write_headers(self):
        from fusionbox.unicode_csv import UnicodeDictWriter
        headers = [u'\u2603']
        result = StringIO()
        fb_writer = UnicodeDictWriter(result, headers)
        fb_writer.writeheader()
        self.assertEquals(result.getvalue(), '\xe2\x98\x83\r\n')

    def test_writerow(self):
        from fusionbox.unicode_csv import UnicodeDictWriter
        result = StringIO()
        row_to_write = {u'\u2603': u'\u2603'}
        headers = [u'\u2603']
        fb_writer = UnicodeDictWriter(result, headers)
        fb_writer.writeheader()
        fb_writer.writerow(row_to_write)
        self.assertEquals(result.getvalue(), '\xe2\x98\x83\r\n\xe2\x98\x83\r\n')


class UnicodeCSVReaderTests(unittest.TestCase):

    def test_readrow_unicode(self):
        s = StringIO('"\xe2\x98\x83"')
        fb_reader = UnicodeReader(s)
        self.assertEquals(fb_reader.next(), [u'\u2603'])

    def test_readrow_ascii(self):
        s = StringIO('"foo"')
        fb_result = UnicodeReader(s).next()
        s.seek(0)
        csv_result = csv.reader(s).next()
        self.assertEquals(fb_result, csv_result)


class UnicodeCSVWriterTests(unittest.TestCase):

    def test_writerow_unicode(self):
        fb_result = StringIO()
        fb_writer = UnicodeWriter(fb_result)
        try:
            fb_writer.writerow([u'\u2603'])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), '\xe2\x98\x83\r\n')

    def test_writerow_ascii(self):
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = UnicodeWriter(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow(['foo'])
        try:
            fb_writer.writerow(['foo'])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())

    def test_writerow_bool(self):
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = UnicodeWriter(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow([True])
        try:
            fb_writer.writerow([True])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())

    def test_writerow_float(self):
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = UnicodeWriter(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow([1.1])
        try:
            fb_writer.writerow([1.1])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())

    def test_writerow_int(self):
        fb_result = StringIO()
        csv_result = StringIO()
        fb_writer = UnicodeWriter(fb_result)
        csv_writer = csv.writer(csv_result)
        csv_writer.writerow([1])
        try:
            fb_writer.writerow([1])
        except Exception as e:
            self.fail('Failed with exception %s' % e)
        self.assertEquals(fb_result.getvalue(), csv_result.getvalue())
