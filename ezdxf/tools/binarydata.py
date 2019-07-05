# Created: 03.05.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from typing import Iterable
from array import array


def hexstr_data_to_bytes(data: Iterable[str]) -> bytes:
    """ Convert multiple hex strings `data` into bytes. """
    byte_array = array('B')
    for hexstr in data:
        byte_array.extend(int(hexstr[index:index+2], 16) for index in range(0, len(hexstr), 2))
    return byte_array.tobytes()


def hexstr_to_bytes(data: str) -> bytes:
    """ Convert hex string `data` into bytes. """
    byte_array = array('B', (int(data[index:index + 2], 16) for index in range(0, len(data), 2)))
    return byte_array.tobytes()


def byte_to_hexstr(data: int) -> str:
    """ Convert integer `data` into a plain hex string. """
    return "%0.2X" % data


def bytes_to_hexstr(data: bytes) -> str:
    """ Convert bytes `data` into a plain hex string. """
    return ''.join(byte_to_hexstr(byte) for byte in data)


