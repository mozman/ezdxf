#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import Tags, casttagvalue, DXFTag, DXFStructureError

POINTCODES = frozenset( [10, 11, 12, 13, 14, 15, 16, 17, 18, 110, 111, 112] )

class GenericWrapper:
    TEMPLATE = ""
    CODE = {
        'handle': 5,
    }
    def __init__(self, tags):
        self.tags = tags

    @classmethod
    def new(cls, handle, attribs=None, dxffactory=None):
        if cls.TEMPLATE == "":
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(Tags.fromtext(cls.TEMPLATE))
        entity.handle = handle
        if attribs is not None:
            entity.update(attribs)
        return entity

    def __getattr__(self, key):
        if key in self.CODE:
            code = self.CODE[key]
            if code in POINTCODES:
                return self._getpoint(code)
            else:
                return self.tags.getvalue(code)
        else:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key in self.CODE:
            code = self.CODE[key]
            if code in POINTCODES:
                self._setpoint(code, value)
            else:
                self._settag(code, value)
        else:
            super(GenericWrapper, self).__setattr__(key, value)

    def _settag(self, code, value):
        self.tags.new_or_update(code, casttagvalue(code, value))

    def update(self, attribs):
        for key, value in attribs.items():
            self._settag(self.CODE[key], value)

    def _setpoint(self, code, value):
        def settag(index, tag):
            if self.tags[index].code == tag.code:
                self.tags[index] = tag
            else:
                self.tags.insert(index, tag)

        coords = list(value) + [0.] * (3 - len(value))
        index = self.tags.findfirst(code)
        for x, coord in enumerate(coords):
            settag(index + x, DXFTag(code + x*10, float(coord)))

    def _getpoint(self, code):
        index = self.tags.findfirst(code)
        coords = []
        for index in range(index, index+3):
            try:
                tag = self.tags[index]
            except IndexError:
                break
            if tag.code != code:
                break
            coords.append(tag.value)
            code += 10
        if len(coords) < 2:
            raise DXFStructureError('DXF coordinate error')
        return tuple(coords)



