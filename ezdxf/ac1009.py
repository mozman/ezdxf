#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: dxf engine for R12/AC1009
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .ac1009hdrvars import VARMAP

class AC1009Engine:
    HEADERVARS = dict(VARMAP)
    def __init__(self):
        self.drawing = None

    def new_header_var(self, key, value):
        factory = self.HEADERVARS[key]
        return factory(value)

    def table_entry_wrapper(self, tags, handle):
        return GenericTableEntry(tags, handle)

class GenericTableEntry:
    def __init__(self, tags, handle):
        self.tags = tags
        self.handle = handle

    @property
    def name(self):
        return self.tags[self.tags.findfirst(2)].value
