"""
Unicode Readers and Writers for use with the stdlib's csv module.

See <http://docs.python.org/library/csv.html> for details.
"""
import csv
import codecs
import cStringIO


class UnicodeRecoder:
    """
    Iterator that reads an encoded stream and reencodes the input to the
    specified encoding
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode(self.encoding)


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
        f = UnicodeRecoder(f, encoding)
        self.encoding = encoding
        self.reader = csv.reader(f, dialect=dialect, **kwargs)
        self.line_num = 0

    def next(self):
        row = self.reader.next()
        self.line_num = self.reader.line_num
        return [unicode(s, self.encoding) for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwargs):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
        self.stream = f
        self.encoding = encoding
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode(self.encoding) for s in row])
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class UnicodeDictWriter(csv.DictWriter):
    def __init__(self, f, fieldnames, restkey="", extrasaction="raise",
                 dialect="excel", encoding="utf-8", *args, **kwargs):
        csv.DictWriter.__init__(self, f, fieldnames, restkey, extrasaction,
                                dialect, *args, **kwargs)
        self.writer = UnicodeWriter(f, dialect, encoding=encoding, *args, **kwargs)


class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect="excel", encoding="utf-8", *args, **kwargs):
        csv.DictReader.__init__(self, f, fieldnames, restkey, restval,
                                dialect, *args, **kwargs)
        self.reader = UnicodeReader(f, dialect, encoding=encoding, *args, **kwargs)
