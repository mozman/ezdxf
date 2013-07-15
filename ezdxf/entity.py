# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import cast_tag_value, DXFTag, DXFStructureError
from .classifiedtags import ClassifiedTags


class DXFNamespace(object):
    """ Provides the dxf namespace for GenericWrapper.

    """
    __slots__ = ('_setter', '_getter')

    def __init__(self, wrapper):
        self._getter = wrapper.get_dxf_attrib
        self._setter = wrapper.set_dxf_attrib

    def __getattr__(self, key):
        """GenericWrapper.dxf.DXF_ATTRIBUTE_NAME
        """
        return self._getter(key)

    def __setattr__(self, key, value):
        """GenericWrapper.dxf.DXF_ATTRIBUTE_NAME = value
        """
        if key in self.__slots__:
            super(DXFNamespace, self).__setattr__(key, value)
        else:
            self._setter(key, value)


# noinspection PyUnresolvedReferences
class GenericWrapper(object):
    TEMPLATE = ""
    DXFATTRIBS = {}

    def __init__(self, tags):
        self.tags = tags
        self.dxf = DXFNamespace(self)  # all DXF attributes are accessible by the dxf attribute, like entity.dxf.handle

    @classmethod
    def new(cls, handle, dxfattribs=None, dxffactory=None):
        if cls.TEMPLATE == "":
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(ClassifiedTags.from_text(cls.TEMPLATE))
        entity.dxf.handle = handle
        if dxfattribs is not None:
            entity.update_dxf_attribs(dxfattribs)
        entity.post_new_hook()
        return entity

    def post_new_hook(self):
        pass

    def dxftype(self):
        return self.tags.noclass[0].value

    def handle(self):
        return self.tags.get_handle()

    def has_dxf_attrib(self, key):
        return key in self.DXFATTRIBS

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
        subclass_tags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            tags = DXFExtendedPointType(subclass_tags)
            return tags.get_value(dxfattr.code, dxfattr.xtype)
        else:
            return subclass_tags.get_value(dxfattr.code)

    def _get_extended_type(self, code, xtype):
        tags = DXFExtendedPointType(self.tags)
        return tags.get_value(code, xtype)

    def _set_dxf_attrib(self, key, value):
        dxfattr = self.DXFATTRIBS[key]
        # no subclass is subclass index 0
        subclasstags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            tags = DXFExtendedPointType(subclasstags)
            tags.set_value(dxfattr.code, dxfattr.xtype, value)
        else:
            self._set_tag(subclasstags, dxfattr.code, value)

    def _set_extended_type(self, code, xtype, value):
        tags = DXFExtendedPointType(self.tags)
        return tags.set_value(code, xtype, value)

    @staticmethod
    def _set_tag(tags, code, value):
        tags.set_first(code, cast_tag_value(code, value))


class DXFExtendedPointType(object):
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
            (tag.value for x, tag in enumerate(self.tags[index:index + 3])
             if tag.code == code + x * 10)
        )

    def _point_index(self, code):
        return self.tags.tag_index(code)

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
        def set_tag(index, tag):
            if self.tags[index].code == tag.code:
                self.tags[index] = tag
            else:
                raise DXFStructureError('DXF coordinate error')
        index = self._point_index(code)
        for x, coord in enumerate(value):
            set_tag(index + x, DXFTag(code + x * 10, float(coord)))

    def _set_flexible_point(self, code, value):
        def append_axis():
            index = self._point_index(code)
            self.tags.insert(index + 2, DXFTag(code + 20, 0.0))

        def remove_axis():
            index = self._point_index(code)
            self.tags.pop(index + 2)

        new_axis = len(value)
        if new_axis not in (2, 3):
            raise ValueError("2D or 3D point required (tuple).")
        old_axis = self._count_axis(code)
        if old_axis > 1:
            if new_axis == 2 and old_axis == 3:
                remove_axis()
            elif new_axis == 3 and old_axis == 2:
                append_axis()
        else:
            raise DXFStructureError("Invalid axis count of point.")
        self._set_point(code, value)

    def _count_axis(self, code):
        return len(self._get_point(code))
