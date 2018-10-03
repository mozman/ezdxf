# Created: 16.07.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from uuid import uuid1

from .c23 import ustr


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


def guid():
    return ustr(uuid1()).upper()


def take2(iterable):
    store = None
    for item in iterable:
        if store is None:
            store = item
        else:
            yield store, item
            store = None
