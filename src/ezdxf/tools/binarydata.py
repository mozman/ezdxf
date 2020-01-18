# Created: 03.05.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from typing import Iterable
from array import array


def hex_strings_to_bytes(data: Iterable[str]) -> bytes:
    """ Returns multiple hex strings `data` as bytes. """
    byte_array = array('B')
    for hexstr in data:
        byte_array.extend(int(hexstr[index:index+2], 16) for index in range(0, len(hexstr), 2))
    return byte_array.tobytes()


def hexstr_to_bytes(data: str) -> bytes:
    """ Returns hex string `data` as bytes. """
    byte_array = array('B', (int(data[index:index + 2], 16) for index in range(0, len(data), 2)))
    return byte_array.tobytes()


def int_to_hexstr(data: int) -> str:
    """ Returns integer `data` as plain hex string. """
    return "%0.2X" % data


def bytes_to_hexstr(data: bytes) -> str:
    """ Returns `data` bytes as plain hex string. """
    return ''.join(int_to_hexstr(byte) for byte in data)


