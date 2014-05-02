# Purpose: decode/encode DXF proprietary data
# Created: 01.05.2014
# Copyright (C) 2014, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .c23 import PY3


_decode_table = {
    0x20: ' ',
    0x40: '_',
    0x5F: '@',
}
for c in range(0x41, 0x5F):
    _decode_table[c] = chr(0x41 + (0x5E - c))  # 0x5E -> 'A', 0x5D->'B', ...


def decode(text_lines):
    def _decode(text):
        dectab = _decode_table  # fast local var
        s = []
        if PY3:
            text = bytes(text, 'ascii')
        else:
            text = map(ord, text)
        skip = False
        for c in text:
            if skip:
                skip = False
                continue
            if c in dectab:
                s += dectab[c]
                skip = (c == 0x5E)  # skip space after 'A'
            else:
                s += chr(c ^ 0x5F)
        return ''.join(s)
    return (_decode(line) for line in text_lines)

_encode_table = {
    ' ': ' ',  # 0x20
    '_': '@',  # 0x40
    '@': '_',  # 0x5F
}
for c in range(0x41, 0x5F):
    _encode_table[chr(c)] = chr(0x5E - (c - 0x41))  # 0x5E->'A', 'B'->0x5D, ...


def encode(text_lines):
    def _encode(text):
        s = []
        enctab = _encode_table  # fast local var
        for c in text:
            if c in enctab:
                s += enctab[c]
                if c == 'A':
                    s += ' '  # append a space for an 'A' -> cryptography
            else:
                s += chr(ord(c) ^ 0x5F)
        return ''.join(s)
    return (_encode(line) for line in text_lines)
