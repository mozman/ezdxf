# Purpose: low level DXF data encoding/decoding module
# Created: 26.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
import sys
from .const import DXFEncodingError


def dxfbackslashreplace(exc):
    if isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError)):
        s = u""
        for c in exc.object[exc.start:exc.end]:
            if ord(c) <= 0xff:
                s += u"\\x%02x" % ord(c)
            elif ord(c) <= 0xffff:
                s += u"\\U+%04x" % ord(c)
            else:
                s += u"\\U+%08x" % ord(c)
        return (s, exc.end)
    else:
        raise TypeError("can't handle %s" % exc.__name__)


PY3 = sys.version_info.major > 2
if not PY3:
    bytes = lambda u, e: u.encode(e)


def encode(unicode_string, encoding='cp1252', ignore_error=False):
    try:
        return bytes(unicode_string, encoding)
    except UnicodeEncodeError:  # can not use the given encoding
        if ignore_error:  # encode string with the default unicode encoding
            return bytes(unicode_string, 'utf-8')
        else:
            raise DXFEncodingError("Can not encode string '{}' with given encoding '{}'".format(unicode_string, encoding))


