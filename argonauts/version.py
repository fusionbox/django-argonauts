# -*- coding: utf-8 -*-

def to_string(v):
    version_string = '%d.%d' % v[0:2]
    try:
        version_string += '%s' % v[2]
        version_string += '%d' % v[3]
    except IndexError:
        pass
    return version_string
