# Purpose: Python 2/3 compatibility layer
# Created: 12.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import sys
import functools
import array

PY3 = sys.version_info.major > 2
if sys.version_info[:2] > (3, 2):
    from collections.abc import Sequence
else:
    from collections import Sequence


if PY3:
    import html
    escape = functools.partial(html.escape, quote=True)
    basestring = str
    ustr = str
    unicode2bytes = lambda s: bytes(s, encoding='utf-8')
    import reprlib
else:  # Python 2.7
    import cgi
    import repr as reprlib
    escape = functools.partial(cgi.escape, quote=True)
    ustr = unicode
    unicode2bytes = lambda s: s.encode('utf-8')


def byte_to_hexstr(byte):
    if PY3:
        return "%X" % byte
    else:
        return "%X" % ord(byte)


def encode_hex_code_string_to_bytes(data):
    byte_array = array.array('B', (int(data[index:index+2], 16) for index in range(0, len(data), 2)))
    if PY3:
        return byte_array.tobytes()
    else:
        return byte_array.tostring()


def isstring(s):
    return isinstance(s, basestring)
