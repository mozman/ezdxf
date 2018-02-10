# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <me@mozman.at>"

from collections import namedtuple

_DXFAttr = namedtuple('DXFAttr', 'code xtype default dxfversion')
DXFAttr3 = namedtuple('DXFAttr3', 'code xtype subclass default dxfversion')
DefSubclass = namedtuple('DefSubclass', 'name attribs')


# *dxfversion* == None - valid for all supported DXF versions managed by the dxffactory:
# dxffactory AC1009 - manages just DXF version AC1009, but dxffactory AC1015 manages the DXF version AC1015 and all
# later DXF versions! Set *dxfversion* to 'AC1018' and this attribute can only be set in drawings with DXF version
# AC1018 or later.
def DXFAttr(code, xtype=None, default=None, dxfversion=None):
    return _DXFAttr(code, xtype, default, dxfversion)


class DXFAttributes:
    def __init__(self, *subclassdefs):
        self._subclasses = []
        self._attribs = {}
        for subclass in subclassdefs:
            self.add_subclass(subclass)
            
    def add_subclass(self, subclass):
        subclass_index = len(self._subclasses)
        self._subclasses.append(subclass)
        self._add_subclass_attribs(subclass, subclass_index)
        
    def _add_subclass_attribs(self, subclass, subclass_index):
        for name, dxfattrib in subclass.attribs.items():
            self._attribs[name] = DXFAttr3(dxfattrib.code, dxfattrib.xtype, subclass_index, dxfattrib.default,
                                           dxfattrib.dxfversion)

    def __getitem__(self, name):
        return self._attribs[name]

    def __contains__(self, name):
        return name in self._attribs

    def get(self, key, default=None):
        return self._attribs.get(key, default)

    def keys(self):
        return self._attribs.keys()

    def items(self):
        return self._attribs.items()

    def subclasses(self):
        return iter(self._subclasses)
