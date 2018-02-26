# Created: 16.07.2015
# Copyright (C) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals


def float2transparency(value):
    return int((1. - float(value)) * 255) | 0x02000000


def transparency2float(value):
    return 1. - float(int(value) & 0xFF) / 255.


def set_flag_state(flags, flag, state=True):
    if state:
        flags = flags | flag
    else:
        flags = flags & ~flag
    return flags
