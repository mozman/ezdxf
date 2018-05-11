# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from collections import namedtuple
from .const import DXFAttributeError, DXFValueError, DXFInternalEzdxfError, DXFStructureError
from .types import dxftag, DXFVertex

DefSubclass = namedtuple('DefSubclass', 'name attribs')


class DXFAttr(object):
    """
    Defines a DXF attribute, accessible by DXFEntity.dxf.name.

    Extended Attribute Types
    ------------------------

    xtype = 'Point2D'

    2D points only

    xtype = 'Point3D'

    3D point only

    xtype = 'Point2D/3D'

    mixed 2D/3D point

    xtype = 'Callback'

    Calls get_value(entity) to get the value of DXF attribute 'name', and calls set_value(entity, value) to set value of
    DXF attribute 'name'.

    For example definitions see TestDXFEntity.test_callback() in file test_dxfentity.py

    """
    def __init__(self, code=None, subclass=0, xtype=None, default=None, dxfversion=None,
                 getter=None, setter=None):
        self.name = ''  # set by DXFAttributes._add_subclass_attribs()
        self.code = code  # DXF group code
        self.subclass = subclass  # subclass index
        self.xtype = xtype  # Point2D, Point3D, Point2D/3D, Callback
        self.default = default  # DXF default value

        # If dxfversion is None - this attribute is valid for all supported DXF versions, set dxfversion to as specific
        # DXF version like 'AC1018' and this attribute can only be set by DXF version 'AC1018' or later.
        self.dxfversion = dxfversion
        self.getter = getter  # DXF entity getter method name for callback attributes
        self.setter = setter  # DXF entity setter method name for callback attributes

    def get_callback_value(self, entity):
        """
        Executes a callback function in 'entity' to get a DXF value.

        Callback function is defined by self.getter as string.

        Args:
            entity: DXF entity

        Returns: DXF attribute value
        """
        try:
            return getattr(entity, self.getter)()
        except AttributeError:
            raise DXFAttributeError('DXF attribute {}: invalid getter {}.'.format(self.name, self.getter))
        except TypeError:  # None
            DXFAttributeError('DXF attribute {} has no getter.'.format(self.name))

    def set_callback_value(self, entity, value):
        """
        Executes a callback function in 'entity' to set a DXF value.

        Callback function is defined by self.setter as string.

        Args:
            entity: DXF entity
            value: DXF attribute value

        """
        try:
            getattr(entity, self.setter)(value)
        except AttributeError:
            raise DXFAttributeError('DXF attribute {}: invalid setter {}.'.format(self.name, self.setter))
        except TypeError:  # None
            raise DXFAttributeError('DXF attribute {} has no setter.'.format(self.name))

    def get_attrib(self, entity, key, default=DXFValueError):
        """
        Return value of DXF attribute 'key'.

        Args:
            entity: DXF entity
            key: attribute name
            default: default value or DXFValueError for raising an exception if attribute does not exist

        Returns: value of DXF attribute

        """
        if self.xtype == 'Callback':
            return self.get_callback_value(entity)
        try:  # No check if attribute is valid for DXF version of drawing, if it is there you get it
            return self._get_dxf_attrib(entity.tags)
        except DXFValueError:
            if default is DXFValueError:
                # no DXF default values if DXF version is incorrect
                if self.dxfversion is not None and entity.drawing.dxfversion < self.dxfversion:
                    msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                    raise DXFValueError(msg.format(key, entity.drawing.dxfversion, self.dxfversion))
                result = self.default  # default value defined by DXF specs
                if result is not None:
                    return result
                else:
                    raise DXFValueError("DXFAttrib '%s' does not exist." % key)
            else:
                return default

    def _get_dxf_attrib(self, tags):
        subclass_tags = self._get_dxf_attrib_subclass_tags(tags, self.subclass)
        if self.xtype is not None:
            return self._get_extented_type(subclass_tags)
        else:
            return subclass_tags.get_first_value(self.code)

    def _get_extented_type(self, tags):
        value = tags.get_first_value(self.code)
        if len(value) == 3:
            if self.xtype == 'Point2D':
                raise DXFStructureError("expected 2D point but found 3D point")
        elif self.xtype == 'Point3D':  # len(value) == 2
            raise DXFStructureError("expected 3D point but found 2D point")
        return value

    def _get_dxf_attrib_subclass_tags(self, tags, subclass_key):
        try:  # fast access subclass by index as int
            # no subclass is subclass index 0
            return tags.subclasses[subclass_key]
        except IndexError:
            raise DXFInternalEzdxfError('Subclass index error in {entity} subclass={index}.'.format(
                entity=self.__str__(),
                index=subclass_key,
            ))
        except TypeError:  # slow access subclass by name as string
            # raises DXFKeyError if subclass does not exist
            return tags.get_subclass(subclass_key)

    def set_attrib(self, entity, key, value):
        """
        Set DXF attribute 'key' to value.

        Args:
            entity: DXF entity
            key: attribute name
            value: attribute value

        Returns: cache able value of attribute or None for not cache able

        """
        if self.dxfversion is not None:
            if entity.drawing.dxfversion < self.dxfversion:
                msg = "DXFAttrib '{0}' not supported by DXF version '{1}', requires at least DXF version '{2}'."
                raise DXFAttributeError(msg.format(key, entity.drawing.dxfversion, self.dxfversion))

        if self.xtype == 'Callback':
            self.set_callback_value(entity, value)
            return None  # callback not cache able

        subclass_tags = self._get_dxf_attrib_subclass_tags(entity.tags, self.subclass)
        if self.xtype is not None:
            return self._set_extended_type(subclass_tags, value)
        else:
            tag = dxftag(self.code, value)
            subclass_tags.set_first(tag)
            return tag.value  # cache able value

    def _set_extended_type(self, tags, value):
        value = tuple(value)
        vlen = len(value)
        if vlen == 3:
            if self.xtype == 'Point2D':
                raise DXFValueError('2 axis required')
        elif vlen == 2:
            if self.xtype == 'Point3D':
                raise DXFValueError('3 axis required')
        else:
            raise DXFValueError('2 or 3 axis required')
        vertex = DXFVertex(self.code, value)
        tags.set_first(vertex)
        return vertex.value  # cache able value

    def del_attrib(self, entity):
        """
        Remove tag of DXF attribute in 'entity'.

        Args:
            entity: DXF entity

        """
        subclass_tags = self._get_dxf_attrib_subclass_tags(entity.tags, self.subclass)
        subclass_tags.remove_tags(codes=(self.code,))


class DXFAttributes(object):
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
            dxfattrib.name = name
            dxfattrib.subclass = subclass_index
            self._attribs[name] = dxfattrib

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
