# Purpose: low level DXF data encoding/decoding module
# Created: 26.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import sys
import codecs

from .const import DXFEncodingError, DXFDecodingError


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

codecs.register_error('dxfreplace', dxfbackslashreplace)


PY3 = sys.version_info.major > 2

if not PY3:
    bytes = lambda u, e: u.encode(e)


def encode(unicode_string, encoding='cp1252', ignore_error=False):
    try:
        return bytes(unicode_string, encoding)
    except UnicodeEncodeError:  # can not use the given encoding
        if ignore_error:  # encode string with the default unicode encoding
            return bytes(unicode_string, 'utf8')
        else:
            raise DXFEncodingError("Can not encode string '{}' with given encoding '{}'".format(unicode_string, encoding))


def decode_utf_encoding(binary_string, ignore_errors=False):
    try:
        return binary_string.decode('utf-8', errors='ignore' if ignore_errors else 'strict')
    except UnicodeDecodeError:
        raise DXFDecodingError('Input Stream Decoding Error: unable to read data stream.')


def decode(binary_string, encoding='cp1245', ignore_errors=False):
    try:
        return binary_string.decode(encoding)
    except UnicodeDecodeError:  # if 'encoding' fails, try utf-8 encodings
        return decode_utf_encoding(binary_string, ignore_errors)


