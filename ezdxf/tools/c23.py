# Purpose: Python 2/3 compatibility layer
# Created: 12.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import sys
import functools

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
else:  # Python 2.7
    import cgi
    escape = functools.partial(cgi.escape, quote=True)
    ustr = unicode
    unicode2bytes = lambda s: s.encode('utf-8')


def isstring(s):
    return isinstance(s, basestring)
