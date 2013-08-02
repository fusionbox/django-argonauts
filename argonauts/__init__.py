# -*- coding: utf-8 -*-

# (major, minor): (1, 0) -> 1.0
# (major, minor, phase): (1, 1, 'alpha') -> 1.0alpha
# (major, minor, phase, phaseversion): (1, 1, 'rc', 5) -> 1.1rc5

VERSION = (0, 9, 'alpha')

def get_version():
    from . import version
    return version.to_string(VERSION)
