# Copyright (c) 2016-2020, Manfred Moitzi
# License: MIT License
import re
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
        raise TypeError(f"Can't handle {exc.__class__.__name__}")


def encode(unicode: str, encoding: str = 'cp1252', ignore_error: bool = False):
    try:
        return bytes(unicode, encoding)
    except UnicodeEncodeError:  # can not use the given encoding
        if ignore_error:  # encode string with the default unicode encoding
            return bytes(unicode, 'utf-8')
        else:
            raise DXFEncodingError(
                f"Can not encode string '{unicode}' with given "
                f"encoding '{encoding}'")


BACKSLASH_UNICODE = re.compile(r'(\\U\+[A-F0-9]{4})')


def _decode(s: str) -> str:
    if s.startswith(r'\U+'):
        return chr(int(s[3:], 16))
    else:
        return s


def has_dxf_backslash_encoding(s: str) -> bool:
    return bool(re.search(BACKSLASH_UNICODE, s))


def decode_dxf_backslash_encoding(s: str):
    return ''.join(_decode(part) for part in re.split(BACKSLASH_UNICODE, s))
