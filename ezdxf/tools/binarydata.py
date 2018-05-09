# Created: 03.05.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .c23 import PY3
from array import array


def binary_encoded_data_to_bytes(data):
    byte_array = array('B')
    for text in data:
        byte_array.extend(int(text[index:index+2], 16) for index in range(0, len(text), 2))
    return array_to_bytes(byte_array)


def array_to_bytes(byte_array):
    if PY3:
        return byte_array.tobytes()
    else:
        return byte_array.tostring()
