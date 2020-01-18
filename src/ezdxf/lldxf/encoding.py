# Purpose: low level DXF data encoding/decoding module
# Created: 26.03.2016
# Copyright (c) 2016-2018, Manfred Moitzi
# License: MIT License
from .const import DXFEncodingError


def dxf_backslash_replace(exc: Exception):
    if isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError)):
        s = ""
        for c in exc.object[exc.start:exc.end]:
            if ord(c) <= 0xff:
                s += "\\x%02x" % ord(c)
            elif ord(c) <= 0xffff:
                s += "\\U+%04x" % ord(c)
            else:
                s += "\\U+%08x" % ord(c)
        return s, exc.end
    else:
        raise TypeError("can't handle %s" % exc.__name__)


def encode(unicode: str, encoding: str = 'cp1252', ignore_error: bool = False):
    try:
        return bytes(unicode, encoding)
    except UnicodeEncodeError:  # can not use the given encoding
        if ignore_error:  # encode string with the default unicode encoding
            return bytes(unicode, 'utf-8')
        else:
            raise DXFEncodingError("Can not encode string '{}' with given encoding '{}'".format(unicode, encoding))
