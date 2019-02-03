# Created: 16.07.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from typing import Tuple, Any, Iterable
from uuid import uuid1
import functools
import array
import html

escape = functools.partial(html.escape, quote=True)


def float2transparency(value: float) -> int:
    return int((1. - float(value)) * 255) | 0x02000000


def transparency2float(value):
    return 1. - float(int(value) & 0xFF) / 255.


def set_flag_state(flags: int, flag: int, state: bool = True) -> int:
    if state:
        flags = flags | flag
    else:
        flags = flags & ~flag
    return flags


def guid() -> str:
    return str(uuid1()).upper()


def take2(iterable: Iterable) -> Tuple[Any, Any]:
    store = None
    for item in iterable:
        if store is None:
            store = item
        else:
            yield store, item
            store = None


def encode_hex_code_string_to_bytes(data: str) -> bytes:
    byte_array = array.array('B', (int(data[index:index + 2], 16) for index in range(0, len(data), 2)))
    return byte_array.tobytes()


def byte_to_hexstr(byte: int) -> str:
    return "%0.2X" % byte


def suppress_zeros(s: str, leading: bool = False, trailing: bool = True):
    if (not leading) and (not trailing):
        return s

    if float(s) == 0.:
        return '0'

    if s[0] in '-+':
        sign = s[0]
        s = s[1:]
    else:
        sign = ""

    if leading:
        s = s.lstrip('0')
    if trailing:
        s = s.rstrip('0')
    if s[-1] in '.,':
        s = s[:-1]
    return sign+s


lifter = {
    '0': '\u2070',
    '1': '\u00B9',
    '2': '²',
    '3': '³',
    '4': '\u2074',
    '5': '\u2075',
    '6': '\u2076',
    '7': '\u2077',
    '8': '\u2078',
    '9': '\u2079',
}


def raise_decimals(s: str):
    def _raise():
        translate = False
        for char in s:
            if translate:
                if char not in '0123456789':
                    translate = False
                else:
                    char = lifter.get(char, char)
            if char == '.':
                translate = True
                continue
            yield char
    return ''.join(_raise())
