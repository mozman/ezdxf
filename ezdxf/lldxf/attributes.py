# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from collections import namedtuple
from .const import DXFAttributeError
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

    def get_value(self, entity):
        try:
            return getattr(entity, self.getter)()
        except AttributeError:
            raise DXFAttributeError('DXF attribute {}: invalid getter {}.'.format(self.name, self.getter))
        except TypeError:  # None
            DXFAttributeError('DXF attribute {} has no getter.'.format(self.name))

    def set_value(self, entity, value):
        try:
            getattr(entity, self.setter)(value)
        except AttributeError:
            raise DXFAttributeError('DXF attribute {}: invalid setter {}.'.format(self.name, self.setter))
        except TypeError:  # None
            raise DXFAttributeError('DXF attribute {} has no setter.'.format(self.name))


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
