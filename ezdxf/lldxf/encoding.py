# Purpose: low level DXF data encoding/decoding module
# Created: 26.03.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

import sys
from .const import DXFEncodingError, DXFDecodingError

PY3 = sys.version_info.major > 2

if PY3:
    pass
else:
    bytes = lambda u, e: u.encode(e)

DXF_DEFAULT_UNICODE_ENCODING = 'utf-8'
DXF_READ_ENCODINGS = ['utf-8', 'utf-16', 'utf-32']


def encode(unicode_string, encoding='cp1245', ignore_error=False):
    try:
        return bytes(unicode_string, encoding)
    except UnicodeEncodeError:  # can not use the given encoding
        if ignore_error:  # encode string with the default unicode encoding
            return bytes(unicode_string, DXF_DEFAULT_UNICODE_ENCODING)
        else:
            raise DXFEncodingError("Can not encode string '{}' with given encoding '{}'".format(unicode_string, encoding))


def decode_utf_encoding(binary_string, ignore_errors=False):
    for encoding in DXF_READ_ENCODINGS:
        try:
            return binary_string.decode(encoding)
        except UnicodeDecodeError:
            pass
        if ignore_errors:
            return binary_string.decode(DXF_DEFAULT_UNICODE_ENCODING, errors='ignore')
        else:
            raise DXFDecodingError('Input Stream Decoding Error: unable to read data stream. Set '
                                   'options.ignore_decode_errors=True to ignore decoding errors, but this maybe breaks '
                                   'text and entity names.')


def decode(binary_string, encoding='cp1245', ignore_errors=False):
    try:
        return binary_string.decode(encoding)
    except UnicodeDecodeError:  # if 'encoding' fails, try some utf encodings
        return decode_utf_encoding(binary_string, ignore_errors)
