# -*- coding: utf-8 -*-

def to_string(v):
    version_string = '%d.%d.%d' % v[0:3]
    try:
        version_string += '%s' % v[3]
        version_string += '%d' % v[4]
    except IndexError:
        pass
    return version_string
