#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from functools import lru_cache
from .tags import Tags, casttagvalue, DXFTag, DXFStructureError

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
            if isinstance(code, tuple):
                return self._get_extended_type(code)
            else:
                return self.tags.getvalue(code)
        else:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key in self.CODE:
            self._setattrib(key, value)
        else:
            super(GenericWrapper, self).__setattr__(key, value)

    def _setattrib(self, key, value):
        code = self.CODE[key]
        if isinstance(code, tuple):
            self._set_extended_type(code, value)
        else:
            self._settag(code, value)

    def _settag(self, code, value):
        self.tags.new_or_update(code, casttagvalue(code, value))

    def update(self, attribs):
        for key, value in attribs.items():
            self._setattrib(key, value)

    def _set_extended_type(self, extcode, value):
        def set_point(code, axis):
            if len(value) != axis:
                raise ValueError('%d axis required' % axis)
            if self._count_axis(code) != axis:
                raise DXFStructureError('Invalid axis count for code: %d' % code)
            self._set_point(code, value)

        code, type_ = extcode
        if type_ == 'Point2D':
            set_point(code, axis=2)
        elif type_ == 'Point3D':
            set_point(code, axis=3)
        elif type_ == 'Point2D/3D':
            self._set_flexible_point(code, value)
        else:
            raise TypeError('Unknown extended type: %s' % type_)

    def _set_point(self, code, value):
        def settag(index, tag):
            if self.tags[index].code == tag.code:
                self.tags[index] = tag
            else:
                raise DXFStructureError('DXF coordinate error')
        index = self._point_index(code)
        for x, coord in enumerate(value):
            settag(index + x, DXFTag(code + x*10, float(coord)))

    def _set_flexible_point(self, code, value):
        def append_axis():
            index = self._point_index(code)
            self.tags.insert(index+2, DXFTag(code+20, 0.0))

        def remove_axis():
            index = self._point_index(code)
            self.tags.pop(index+2)

        newaxis = len(value)
        if newaxis not in (2, 3):
            raise ValueError("2D or 3D point required (tuple).")
        oldaxis = self._count_axis(code)
        if oldaxis > 1:
            if newaxis == 2 and oldaxis == 3:
                remove_axis()
            elif newaxis == 3 and oldaxis == 2:
                append_axis()
        else:
            raise DXFStructureError("Invalid axis count of point.")
        self._set_point(code, value)

    def _count_axis(self, code):
        return len(self._get_point(code))

    def _get_extended_type(self, extcode):
        code, type_ = extcode
        if type_ == 'Point2D':
            return self._get_fix_point(code, axis=2)
        elif type_ == 'Point3D':
            return self._get_fix_point(code, axis=3)
        elif type_ == 'Point2D/3D':
            return self._get_flexible_point(code)
        else:
            raise TypeError('Unknown extended type: %s' % type_)

    def _point_index(self, code):
        return self.tags.findfirst(code)

    def _get_point(self, code):
        index = self._point_index(code)
        return tuple(
            ( tag.value for x, tag in enumerate(self.tags[index:index+3])
              if tag.code == code + x*10 )
        )

    def _get_fix_point(self, code, axis):
        point = self._get_point(code)
        if len(point) != axis:
            raise DXFStructureError('Invalid axis count for code: %d' % code)
        return point

    def _get_flexible_point(self, code):
        point = self._get_point(code)
        if len(point) in (2, 3):
            return point
        else:
            raise DXFStructureError('Invalid axis count for code: %d' % code)
