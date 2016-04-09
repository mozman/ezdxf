# Purpose: entity module
# Created: 11.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from .lldxf.types import cast_tag_value, DXFTag
from .lldxf.const import DXFStructureError


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
        """Returns value of DXF attribute *attrib*. usage: value = DXFEntity.dxf.attrib
        """
        return self._getter(attrib)

    def __setattr__(self, attrib, value):
        """Set DXF attribute *attrib* to *value.  usage: DXFEntity.dxf.attrib = value
        """
        self._setter(attrib, value)

    def __delattr__(self, attrib):
        """Remove DXF attribute *attrib*.  usage: del DXFEntity.dxf.attrib
        """
        self._deleter(attrib)


# noinspection PyUnresolvedReferences
class DXFEntity(object):
    TEMPLATE = None
    DXFATTRIBS = {}

    def __init__(self, tags, drawing=None):
        self.tags = tags
        self.dxf = DXFNamespace(self)  # all DXF attributes are accessible by the dxf attribute, like entity.dxf.handle
        self.drawing = drawing

    @property
    def dxffactory(self):
        return self.drawing.dxffactory

    @property
    def entitydb(self):
        return self.drawing.entitydb

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

    def _new_entity(self, type_, dxfattribs):
        """ Create new entity with same layout settings as *self*.

        Used by INSERT & POLYLINE to create appended DXF entities, don't use it to create new standalone entities.
        """
        entity = self.dxffactory.create_db_entry(type_, dxfattribs)
        self.dxffactory.copy_layout(self, entity)
        return entity

    def dxftype(self):
        return self.tags.noclass[0].value

    def supports_dxf_attrib(self, key):
        """ Returns *True* if DXF attrib *key* is supported by this entity else False. Does not grant that attrib
        *key* really exists.
        """
        dxfattr = self.DXFATTRIBS.get(key, None)
        if dxfattr is None:
            return False
        if dxfattr.dxfversion is None or self.drawing is None:
            return True
        return self.drawing.dxfversion >= dxfattr.dxfversion

    def valid_dxf_attrib_names(self):
        """ Returns a list of supported DXF attribute names.
        """
        is_dxfversion = None if self.drawing is None else self.drawing.dxfversion
        return [key for key, attrib in self.DXFATTRIBS.items() if attrib.dxfversion is None or
                                                                  (attrib.dxfversion <= is_dxfversion)]

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
        try:  # No check if attribute is valid for DXF version of drawing, if it is there you get it
            return self._get_dxf_attrib(dxfattr)
        except ValueError:
            if default is ValueError:
                # no DXF default values if DXF version is incorrect
                if dxfattr.dxfversion is not None and \
                        self.drawing is not None and \
                        self.drawing.dxfversion < dxfattr.dxfversion:
                    msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                    raise ValueError(msg.format(key, self.drawing.dxfversion, dxfattr.dxfversion))
                result = dxfattr.default  # default value defined by DXF specs
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

    def _get_dxf_attrib(self, dxfattr):
        # no subclass is subclass index 0
        subclass_tags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            return self._get_extented_type(subclass_tags, dxfattr.code, dxfattr.xtype)
        else:
            return subclass_tags.get_value(dxfattr.code)

    def has_dxf_default_value(self, key):
        """ Returns *True* if the DXF attribute *key* has a DXF standard default value.
        """
        return self._get_dxfattr_definition(key).default is not None

    def set_dxf_attrib(self, key, value):
        dxfattr = self._get_dxfattr_definition(key)
        if dxfattr.dxfversion is not None and self.drawing is not None:
            if self.drawing.dxfversion < dxfattr.dxfversion:
                msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                raise AttributeError(msg.format(key, self.drawing.dxfversion, dxfattr.dxfversion))
        # no subclass is subclass index 0
        subclasstags = self.tags.subclasses[dxfattr.subclass]
        if dxfattr.xtype is not None:
            self._set_extended_type(subclasstags, dxfattr.code, dxfattr.xtype, value)
        else:
            subclasstags.set_first(dxfattr.code, cast_tag_value(dxfattr.code, value))

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

    @staticmethod
    def _get_extented_type(tags, code, xtype):
        def get_point():
            index = tags.tag_index(code)
            return tags[index].value

        if xtype == 'Point3D':
            value = get_point()
            if len(value) == 2:
                raise DXFStructureError("expected 3D point but found 2D point")
            return value
        elif xtype == 'Point2D':
            value = get_point()
            if len(value) == 3:
                raise DXFStructureError("expected 2D point but found 3D point")
            return value
        elif xtype == 'Point2D/3D':
            return get_point()
        else:
            raise TypeError('Unknown extended type: %s' % xtype)

    @staticmethod
    def _set_extended_type(tags, code, xtype, value):
        value = cast_tag_value(code, value)

        def set_point():
            if tags.has_tag(code):  # replace existing tag
                index = tags.tag_index(code)
                tags[index] = DXFTag(code, value)
            else:  # append new tag
                tags.append(DXFTag(code, value))

        if xtype == 'Point2D':
            if len(value) != 2:
                raise ValueError('2 axis required')
            set_point()
        elif xtype == 'Point3D':
            if len(value) != 3:
                raise ValueError('3 axis required')
            set_point()
        elif xtype == 'Point2D/3D':
            if not len(value) in (2, 3):
                raise ValueError('2 or 3 axis required')
            set_point()
        else:
            raise TypeError('Unknown extended type: %s' % xtype)

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

    def has_app_data(self, appid):
        return self.tags.has_app_data(appid)

    def get_app_data(self, appid):
        return self.tags.get_app_data_content(appid)

    def set_app_data(self, appid, app_data_tags):
        tags = self.tags
        if tags.has_app_data(appid):
            appdata = tags.get_app_data(appid)
            appdata[1:-1] = app_data_tags
        else:
            tags.new_app_data(appid, app_data_tags)

    def has_xdata(self, appid):
        return self.tags.has_xdata(appid)

    def get_xdata(self, appid):
        return self.tags.get_xdata(appid)[1:]  # without app id tag

    def set_xdata(self, appid, xdata_tags):
        tags = self.tags
        if tags.has_xdata(appid):
            xdata = tags.get_xdata(appid)
            xdata[1:] = xdata_tags
        else:
            tags.new_xdata(appid, xdata_tags)
