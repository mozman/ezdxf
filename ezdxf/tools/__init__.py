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


def text_width(text: str, width_table: dict) -> float:
    default = width_table['default']
    return sum(width_table.get(char, default) for char in text)
