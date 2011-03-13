#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose:
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from collections import OrderedDict

from .dxfvalue import DXFValue
from .tags import TagGroups

class HeaderSection:
    name = 'header'
    def __init__(self, tags, drawing):
        self.hdrvars = OrderedDict()
        self._drawing = drawing
        self._build(tags)

    @property
    def dxfengine(self):
        return self._drawing.dxfengine

    def _build(self, tags):
        assert tags[0] == (0, 'SECTION')
        assert tags[1] == (2, 'HEADER')
        assert tags[-1] == (0, 'ENDSEC')
        groups = TagGroups(tags[2:-1], splitcode=9)
        for group in groups:
            name = group[0].value
            if len(group) > 2:
                value = tuple(group[1:])
            else:
                value = group[1]
            self.hdrvars[name] =DXFValue(value)

    def write(self, stream):
        def _write(name, value):
            stream.write("  9\n%s\n" % name)
            stream.write(str(value))

        stream.write("  0\nSECTION\n  2\nHEADER\n")
        for name, value in self.hdrvars.items():
            _write(name, value)
        stream.write("  0\nENDSEC\n")

    def __getitem__(self, key):
        var = self.hdrvars[key]
        if var.ispoint:
            return var.getpoint()
        else:
            return var.value

    def get(self, key, default=None):
        if key in self.hdrvars:
            return self.__getitem__(key)
        else:
            return default

    def __setitem__(self, key, value):
        tags = self.dxfengine.new_header_var(key, value)
        self.hdrvars[key] = DXFValue(tags)
