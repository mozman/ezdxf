# Purpose: dxf tag type def
# Created: 30.04.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"


from .c23 import unicode2bytes
import zlib


class CompressedString(object):
    def __init__(self, s):
        self._data = zlib.compress(unicode2bytes(s))

    def __str__(self):
        return 'compressed data'

    def __len__(self):
        return len(self._data)

    def write(self, stream):
        stream.write(self.decompress())

    def decompress(self):
        data = zlib.decompress(self._data)
        return data.decode(encoding='utf-8')