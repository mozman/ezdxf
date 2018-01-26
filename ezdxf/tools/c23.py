# Purpose: Python 2/3 compatibility layer
# Created: 12.05.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import sys
import functools

PY3 = sys.version_info.major > 2
if sys.version_info[:2] > (3, 2):
    from collections.abc import Sequence
    from functools import lru_cache
else:
    from collections import Sequence


def _no_cache(maxsize=0):  # no caching for Python 2.7
    def _no_cache(func):
        def __no_cache(*args, **kwargs):
            return func(*args, **kwargs)
        return __no_cache
    return _no_cache


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
    lru_cache = _no_cache


def isstring(s):
    return isinstance(s, basestring)
