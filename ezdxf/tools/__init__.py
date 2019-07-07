# Created: 16.07.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from typing import Tuple, Any, Iterable
from uuid import uuid1
import functools
import html
from .juliandate import juliandate, calendardate
from .rgb import int2rgb, rgb2int, aci2rgb
from .binarydata import hexstr_to_bytes, hex_strings_to_bytes, int_to_hexstr, bytes_to_hexstr

escape = functools.partial(html.escape, quote=True)


def float2transparency(value: float) -> int:
    return int((1. - float(value)) * 255) | 0x02000000


def transparency2float(value):
    # 255 -> 0.
    # 0 -> 1.
    return 1. - float(int(value) & 0xFF) / 255.


def set_flag_state(flags: int, flag: int, state: bool = True) -> int:
    """ Set/Clear `flag` in `flags`.

    Args:
        flags: data value
        flag: flag to set/clear
        state: ``True`` for setting, ``False`` for clearing

    """
    if state:
        flags = flags | flag
    else:
        flags = flags & ~flag
    return flags


def guid() -> str:
    """ Returns a General unique ID, based on :func:`uuid.uuid1`. """
    return str(uuid1()).upper()


def take2(iterable: Iterable) -> Tuple[Any, Any]:
    """ Iterate `iterable` as 2-tuples.

    :code:`[1, 2, 3, 4, ...] -> (1, 2), (3, 4), ...`

    """
    store = None
    for item in iterable:
        if store is None:
            store = item
        else:
            yield store, item
            store = None

def suppress_zeros(s: str, leading: bool = False, trailing: bool = True):
    """ Suppress leading and/or trailing ``0`` of string `s`.

    Args:
         s: data string
         leading: suppress leading ``0``
         trailing: suppress trailing ``0``

    """
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
    return sign + s
