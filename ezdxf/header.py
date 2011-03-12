#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose:
# Created: 12.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from collections import OrderedDict
from .dxfvalue import DXFValue

class HeaderSection:
    name = 'header'
    def __init__(self, tags, drawing):
        self.hdrvars = self.build_dict(tags)
        self.drawing = drawing

    @property
    def dxfengine(self):
        return self.drawing.dxfengine

    def build_dict(self, tags):
        def itervars():
            def getpoint(x):
                y = tags[index + 1]
                z = tags[index + 2]
                return (x, y, z) if z.code == 30 else (x, y)

            def gettag():
                tag = tags[index]
                return getpoint(tag) if tag.code == 10 else tag

            def tagcount(tag):
                return len(value) if isinstance(tag[0], tuple) else 1

            index = 2
            tag = tags[index]
            while tag != (0, 'ENDSEC'):
                name = tag.value
                index += 1
                value = gettag()
                index += tagcount(value)
                yield (name, value)
                tag = tags[index]

        d = OrderedDict()
        for name, value in itervars():
            d[name] = DXFValue(value)
        return d

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
