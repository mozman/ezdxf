# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .tags import cast_tag_value, DXFTag, DXFStructureError


class DXFNamespace(object):
    """ Provides the dxf namespace for GenericWrapper.
    """
    __slots__ = ('_setter', '_getter', '_deleter')

    def __init__(self, wrapper):
        # DXFNamespace.__setattr__ can not set _getter and _setter
        super(DXFNamespace, self).__setattr__('_getter', wrapper.get_dxf_attrib)
        super(DXFNamespace, self).__setattr__('_setter', wrapper.set_dxf_attrib)
        super(DXFNamespace, self).__setattr__('_deleter', wrapper.del_dxf_attrib)

    def __getattr__(self, attrib):
        """Returns value of DXF attribute *attrib*. usage: value = GenericWrapper.dxf.attrib
        """
        return self._getter(attrib)

    def __setattr__(self, attrib, value):
        """Set DXF attribute *attrib* to *value.  usage: GenericWrapper.dxf.attrib = value
        """
        self._setter(attrib, value)

    def __delattr__(self, attrib):
        """Remove DXF attribute *attrib*.  usage: del GenericWrapper.dxf.attrib
        """
        self._deleter(attrib)


# noinspection PyUnresolvedReferences
class GenericWrapper(object):
    TEMPLATE = None
    DXFATTRIBS = {}

    def __init__(self, tags, drawing=None):
        self.tags = tags
        self.dxf = DXFNamespace(self)  # all DXF attributes are accessible by the dxf attribute, like entity.dxf.handle
        self.drawing = drawing

    @classmethod
    def new(cls, handle, dxfattribs=None, drawing=None):
        if cls.TEMPLATE is None:
            raise NotImplementedError("new() for type %s not implemented." % cls.__name__)
        entity = cls(cls.TEMPLATE.clone(), drawing)
        entity.dxf.handle = handle
        if dxfattribs is not None:
            entity.update_dxf_attribs(dxfattribs)
        entity.post_new_hook()
        return entity

    def post_new_hook(self):
        """ Called after entity creation.
        """
        pass

    def dxftype(self):
        return self.tags.noclass[0].value

    def supports_dxf_attrib(self, key):
        """ Returns *True* if DXF attrib *key* is supported by this entity else False. Does not grant that attrib
        *key* really exists.
        """
        return key in self.DXFATTRIBS

    def valid_dxf_attrib_names(self):
        """ Returns a list of supported DXF attribute names.
        """
        return list(self.DXFATTRIBS.keys())

    def dxf_attrib_exists(self, key):
        """ Returns *True* if DXF attrib *key* really exists else False. Raises *AttributeError* if *key* isn't supported.
        """
        # attributes with default values don't raise an exception!
        return self.get_dxf_attrib(key, default=None) is not None

    def _get_dxfattr_definition(self, key):
        try:
            return self.DXFATTRIBS[key]
        except KeyError:
            raise AttributeError(key)

    def get_dxf_attrib(self, key, default=ValueError):
        dxfattr = self._get_dxfattr_definition(key)
        try:
            return self._get_dxf_attrib(dxfattr)
        except ValueError:
            if default is ValueError:
                result = self.get_dxf_default_value(key)
                if result is not None:
                    return result
                else:
                    raise ValueError("DXFAttrib '%s' does not exist." % key)
            else:
                return default

    def get_dxf_default_value(self, key):
        """ Returns the default value as defined in the DXF standard.
        """
        return self._get_dxfattr_definition(key).default

    def has_dxf_default_value(self, key):
        """ Returns *True* if the DXF attribute *key* has a DXF standard default value.
        """
        return self._get_dxfattr_definition(key).default is not None

    def set_dxf_attrib(self, key, value):
        dxfattr = self._get_dxfattr_definition(key)
        # no subclass is subclass index 0
        subclasstags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            tags = DXFExtendedPointType(subclasstags)
            tags.set_value(dxfattr.code, dxfattr.xtype, value)
        else:
            self._set_tag(subclasstags, dxfattr.code, value)

    def del_dxf_attrib(self, key):
        dxfattr = self._get_dxfattr_definition(key)
        self._del_dxf_attrib(dxfattr)

    def clone_dxf_attribs(self):
        """ Clones defined and existing DXF attributes as dict.
        """
        dxfattribs = {}
        for key in self.DXFATTRIBS.keys():
            value = self.get_dxf_attrib(key, default=None)
            if value is not None:
                dxfattribs[key] = value
        return dxfattribs

    def update_dxf_attribs(self, dxfattribs):
        for key, value in dxfattribs.items():
            self.set_dxf_attrib(key, value)

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

    def _set_extended_type(self, code, xtype, value):
        tags = DXFExtendedPointType(self.tags)
        return tags.set_value(code, xtype, value)

    @staticmethod
    def _set_tag(tags, code, value):
        tags.set_first(code, cast_tag_value(code, value))

    def _del_dxf_attrib(self, dxfattr):
        def point_codes(base_code):
            return base_code, base_code + 10, base_code + 20

        subclass_tags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            subclass_tags.remove_tags(codes=point_codes(dxfattr.code))
        else:
            subclass_tags.remove_tags(codes=(dxfattr.code,))

    def destroy(self):
        pass


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

    def has_point(self, code):
        return self.tags.has_tag(code)

    def create_point(self, code, axis):
        for i in range(axis):
            self.tags.append(DXFTag(code + i * 10, 0.0))

    def set_value(self, code, xtype, value):
        def set_point(code, axis):
            if len(value) != axis:
                raise ValueError('%d axis required' % axis)
            if not self.has_point(code):
                self.create_point(code, axis)
            else:
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

        if not self.has_point(code):
            self.create_point(code, new_axis)
        else:
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
