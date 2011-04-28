#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: dxfattr
# Created: 2011-04-27

from collections import namedtuple

DXFAttr = namedtuple('DXFAttr', 'code xtype')
DXFAttr3 = namedtuple('DXFAttr3', 'code xtype subclass')
DefSubclass = namedtuple('SubclassDef', 'name attribs')

class DXFAttributes:
    def __init__(self, *subclassdefs):
        def add(subclass, index):
            for name, dxfattrib in subclass.attribs.items():
                self._attribs[name] = DXFAttr3(dxfattrib.code, dxfattrib.xtype, index)

        self._defs = subclassdefs
        self._attribs = {}
        for index, subclass in enumerate(self._defs):
            add(subclass, index)

    def __getitem__(self, name):
        return self._attribs[name]

    def __contains__(self, name):
        return name in self._attribs

    def keys(self):
        return self._attribs.keys()

    def subclasses(self):
        return iter(self._defs)

    def subclass(self, pos):
        return self._defs[pos]

    def index(self, name, start=0):
        for pos, subclass in enumerate(self._defs):
            if pos >= start and subclass.name == name:
                return pos
        raise ValueError("subclass '%s' not found." % name)
