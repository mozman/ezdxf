#!/usr/bin/env python
#coding:utf-8
# Author:  mozman --<mozman@gmx.at>
# Purpose: dxfattr
# Created: 2011-04-27

from collections import namedtuple

DXFAttr = namedtuple('DXFAttr', 'code xtype')
DXFAttr3 = namedtuple('DXFAttr3', 'code xtype subclass')
SubclassDef = namedtuple('SubclassDef', 'name attribs')

class DXFAttributes:
    def __init__(self, *subclassdefs):
        def add(subclass):
            for index, attrib in enumerate(subclass.attribs.items()):
                self._attribs[attrib[0]] = (attrib[1], index)
                
        self._defs = subclassdefs
        self._attribs = {}
        for subclass in self._defs:
            add(subclass)
            
    def __getitem__(self, name):
        attr, index = self._attribs[name]
        return DXFAttr3(attr.code, attr.xtype, index)
    
    def __contains__(self, name):
        return name in self._attribs
    
    def subclasses(self):
        return iter(self._defs)
    
    def subclass(self, pos):
        return self._defs[pos]
    
    def index(self, name, start=0):
        for pos, subclass in enumerate(self._defs):
            if pos >= start and subclass.name == name:
                return pos
        raise ValueError("subclass '%s' not found." % name)
        