# Created: 03.05.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from typing import Iterable
from array import array


def binary_encoded_data_to_bytes(data: Iterable[str]) -> bytes:
    byte_array = array('B')
    for hexstr in data:
        byte_array.extend(int(hexstr[index:index+2], 16) for index in range(0, len(hexstr), 2))
    return byte_array.tobytes()
