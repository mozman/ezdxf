#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import casttagvalue, DXFTag, DXFStructureError
from .tags import ExtendedTags, DXFAttr

class GenericWrapper:
    TEMPLATE = ""
    DXFATTRIBS = {
        'handle': DXFAttr(5, None, None)
    }
    def __init__(self, tags):
        self.tags = tags

    @classmethod
    def new(cls, handle, dxfattribs=None, dxffactory=None):
        if cls.TEMPLATE == "":
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(ExtendedTags.fromtext(cls.TEMPLATE))
        entity.handle = handle
        if dxfattribs is not None:
            entity.update(dxfattribs)
        return entity

    def dxftype(self):
        return self.tags[0].value

    def getdxfattr(self, key, default=None):
        if key in self.DXFATTRIBS:
            try:
                return self.__getattr__(key)
            except ValueError:
                return default
        else:
            raise AttributeError(key)

    def setdxfattr(self, key, value):
        if key in self.DXFATTRIBS:
            self.__setattr__(key, value)
        else:
            raise AttributeError(key)

    def clonedxfattribs(self):
        dxfattribs = {}
        for key in self.DXFATTRIBS.keys():
            value = self.getdxfattr(key)
            if value is not None:
                dxfattribs[key] = value
        return dxfattribs

    def __getattr__(self, key):
        if key in self.DXFATTRIBS:
            code = self.DXFATTRIBS[key]
            return self._get_attrib(code)
        else:
            raise AttributeError(key)

    def _get_attrib(self, dxfattr):
        if dxfattr.subclass is not None:
            return self._get_subclass_value(dxfattr)
        elif dxfattr.xtype is not None:
            return self._get_extended_type(dxfattr.code, dxfattr.xtype)
        else:
            return self.tags.getvalue(dxfattr.code)

    def _get_subclass_value(self, dxfattr):
        subclasstags = self.tags.subclass[dxfattr.subclass]
        if dxfattr.xtype is not None:
            tags = ExtendedType(subclasstags)
            return tags.get_value(dxfattr.code, dxfattr.xtype)
        else:
            return subclasstags.getvalue(dxfattr.code)

    def _get_extended_type(self, code, xtype):
        tags = ExtendedType(self.tags)
        return tags.get_value(code, xtype)

    def __setattr__(self, key, value):
        if key in self.DXFATTRIBS:
            self._set_attrib(key, value)
        else:
            super(GenericWrapper, self).__setattr__(key, value)

    def _set_attrib(self, key, value):
        dxfattr = self.DXFATTRIBS[key]
        if dxfattr.subclass is not None:
            self._set_subclass_value(dxfattr, value)
        elif dxfattr.xtype is not None:
            self._set_extended_type(dxfattr.code, dxfattr.xtype, value)
        else:
            self._settag(self.tags, dxfattr.code, value)

    def _set_extended_type(self, code, xtype, value):
        tags = ExtendedType(self.tags)
        return tags.set_value(code, xtype, value)

    def _set_subclass_value(self, dxfattr, value):
        subclasstags = self.tags.subclass[dxfattr.subclass]
        if dxfattr.xtype is not None:
            tags = ExtendedType(subclasstags)
            tags.set_value(dxfattr.code, dxfattr.xtype, value)
        else:
            self._settag(subclasstags, dxfattr.code, value)

    @staticmethod
    def _settag(tags, code, value):
        tags.setfirst(code, casttagvalue(code, value))

    def update(self, dxfattribs):
        for key, value in dxfattribs.items():
            self._set_attrib(key, value)


class ExtendedType:
    def __init__(self, tags):
        self.tags = tags

    def get_value(self, code, xtype):
        if xtype == 'Point2D':
            return self._get_fix_point(code, axis=2)
        elif xtype == 'Point3D':
            return self._get_fix_point(code, axis=3)
        elif xtype == 'Point2D/3D':
            return self._get_flexible_point(code)
        else:
            raise TypeError('Unknown extended type: %s' % xtype)

    def _get_fix_point(self, code, axis):
        point = self._get_point(code)
        if len(point) != axis:
            raise DXFStructureError('Invalid axis count for code: %d' % code)
        return point

    def _get_point(self, code):
        index = self._point_index(code)
        return tuple(
            ( tag.value for x, tag in enumerate(self.tags[index:index+3])
              if tag.code == code + x*10 )
        )

    def _point_index(self, code):
        return self.tags.tagindex(code)

    def _get_flexible_point(self, code):
        point = self._get_point(code)
        if len(point) in (2, 3):
            return point
        else:
            raise DXFStructureError('Invalid axis count for code: %d' % code)

    def set_value(self, code, xtype, value):
        def set_point(code, axis):
            if len(value) != axis:
                raise ValueError('%d axis required' % axis)
            if self._count_axis(code) != axis:
                raise DXFStructureError('Invalid axis count for code: %d' % code)
            self._set_point(code, value)

        if xtype == 'Point2D':
            set_point(code, axis=2)
        elif xtype == 'Point3D':
            set_point(code, axis=3)
        elif xtype == 'Point2D/3D':
            self._set_flexible_point(code, value)
        else:
            raise TypeError('Unknown extended type: %s' % xtype)

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
