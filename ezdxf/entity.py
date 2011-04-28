#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

from .tags import casttagvalue, DXFTag, DXFStructureError
from .tags import ExtendedTags

class DXFNamespace:
    """ Provides the dxf namespace for GenericWrapper.

    """
    __slots__ = ('wrapper', )
    def __init__(self, wrapper):
        self.wrapper = wrapper

    def get(self, key, default=ValueError):
        """
        GenericWrapper.dxf.get('DXF_ATTRIBUTE_NAME') - raises ValueError, if not exists
        GenericWrapper.dxf.get('DXF_ATTRIBUTE_NAME', defaultvalue)

        """
        return self.wrapper.get_dxf_attrib(key, default)

    def set(self, key, value):
        """ GenericWrapper.dxf.set('DXF_ATTRIBUTE_NAME', value) """
        self.wrapper.set_dxf_attrib(key, value)

    def __getattr__(self, key):
        """ GenericWrapper.dxf.DXF_ATTRIBUTE_NAME """
        return self.wrapper.get_dxf_attrib(key)

    def __setattr__(self, key, value):
        """ GenericWrapper.dxf.DXF_ATTRIBUTE_NAME = value """
        if key in self.__slots__:
            super(DXFNamespace, self).__setattr__(key, value)
        else:
            self.wrapper.set_dxf_attrib(key, value)

    def clone(self):
        """ GenericWrapper.dxf.clone(): Clone existing dxf attribs as dict. """
        return self.wrapper.clone_dxf_attribs()

    def update(self, attribs):
        """ GenericWrapper.dxf.update(dxfattribs): Update dxf attribs from dict. """
        return self.wrapper.update_dxf_attribs(attribs)

class GenericWrapper:
    TEMPLATE = ""
    DXFATTRIBS = {}

    def __init__(self, tags):
        self.tags = tags
        self.dxf = DXFNamespace(self)

    @classmethod
    def new(cls, handle, dxfattribs=None, dxffactory=None):
        if cls.TEMPLATE == "":
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(ExtendedTags.fromtext(cls.TEMPLATE))
        entity.dxf.handle = handle
        if dxfattribs is not None:
            entity.update_dxf_attribs(dxfattribs)
        return entity

    def dxftype(self):
        return self.tags[0].value

    def get_dxf_attrib(self, key, default=ValueError):
        if key in self.DXFATTRIBS:
            try:
                dxfattr = self.DXFATTRIBS[key]
                return self._get_dxf_attrib(dxfattr)
            except ValueError:
                if default is ValueError:
                    raise ValueError("DXFAttrib '%s' does not exist." % key)
                else:
                    return default
        else:
            raise AttributeError(key)

    def set_dxf_attrib(self, key, value):
        if key in self.DXFATTRIBS:
            self._set_dxf_attrib(key, value)
        else:
            raise AttributeError(key)

    def clone_dxf_attribs(self):
        dxfattribs = {}
        for key in self.DXFATTRIBS.keys():
            try:
                dxfattribs[key] = self.get_dxf_attrib(key)
            except ValueError:
                pass
        return dxfattribs

    def update_dxf_attribs(self, dxfattribs):
        for key, value in dxfattribs.items():
            self._set_dxf_attrib(key, value)

    def _get_dxf_attrib(self, dxfattr):
        # no subclass is subclass index 0
        if dxfattr.subclass > 0:
            return self._get_subclass_value(dxfattr)
        elif dxfattr.xtype is not None:
            return self._get_extended_type(dxfattr.code, dxfattr.xtype)
        else:
            return self.tags.getvalue(dxfattr.code)

    def _get_extended_type(self, code, xtype):
        tags = ExtendedType(self.tags)
        return tags.get_value(code, xtype)

    def _set_dxf_attrib(self, key, value):
        dxfattr = self.DXFATTRIBS[key]
        # no subclass is subclass index 0
        if dxfattr.subclass > 0:
            self._set_subclass_value(dxfattr, value)
        elif dxfattr.xtype is not None:
            self._set_extended_type(dxfattr.code, dxfattr.xtype, value)
        else:
            self._settag(self.tags, dxfattr.code, value)

    def _set_extended_type(self, code, xtype, value):
        tags = ExtendedType(self.tags)
        return tags.set_value(code, xtype, value)

    @staticmethod
    def _settag(tags, code, value):
        tags.setfirst(code, casttagvalue(code, value))

    def _get_subclass_value(self, dxfattr):
        # no subclass is subclass index 0
        subclasstags = self.tags.subclass[dxfattr.subclass-1]
        if dxfattr.xtype is not None:
            tags = ExtendedType(subclasstags)
            return tags.get_value(dxfattr.code, dxfattr.xtype)
        else:
            return subclasstags.getvalue(dxfattr.code)

    def _set_subclass_value(self, dxfattr, value):
        # no subclass is subclass index 0
        subclasstags = self.tags.subclass[dxfattr.subclass-1]
        if dxfattr.xtype is not None:
            tags = ExtendedType(subclasstags)
            tags.set_value(dxfattr.code, dxfattr.xtype, value)
        else:
            self._settag(subclasstags, dxfattr.code, value)

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
