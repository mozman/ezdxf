# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from collections import namedtuple
from enum import Enum
from typing import Any, Tuple, Iterable, List, Dict, Union, ItemsView, KeysView, TYPE_CHECKING

from .const import DXFAttributeError, DXFValueError, DXFInternalEzdxfError, DXFStructureError, DXF12
from .types import dxftag, DXFVertex
from .tags import Tags
from .extendedtags import ExtendedTags

if TYPE_CHECKING:  # import forward declarations
    from ezdxf.eztypes import DXFEntity, TagValue

DefSubclass = namedtuple('DefSubclass', 'name attribs')
VIRTUAL_TAG = -666


class XType(Enum):
    """ Extended Attribute Types
    """
    point2d = 1  # 2D points only
    point3d = 2  # 3D points only
    any_point = 3  # 2D or 3D points
    callback = 4  #


class DXFAttr:
    """
    Defines a DXF attribute, accessible by DXFEntity.dxf.name.

    Extended Attribute Types
    ------------------------

    - XType.point2d:  2D points only
    - XType.point3d:  3D point only
    - XType.any_point:  mixed 2D/3D point
    - XType.callback: Calls get_value(entity) to get the value of DXF attribute 'name', and calls
      set_value(entity, value) to set value of DXF attribute 'name'.

    For example definitions see TestDXFEntity.test_callback() in file test_dxfentity.py

    """

    def __init__(self,
                 code: int,
                 subclass: int = 0,
                 xtype: XType = None,
                 default=None,
                 optional=False,
                 dxfversion: str = DXF12,
                 getter: str = None,  # name of getter method
                 setter: str = None,  # name of setter method
                 alias: str = None,  # alias name
                 ):
        self.name = ''  # type: str  # set by DXFAttributes._add_subclass_attribs()
        self.code = code  # DXF group code
        self.subclass = subclass  # subclass index
        self.xtype = xtype  # Point2D, Point3D, Point2D/3D, Callback
        self.default = default  # type: TagValue # DXF default value
        self.optional = optional  # this value is only written if set

        # If dxfversion is None - this attribute is valid for all supported DXF versions, set dxfversion to a specific
        # DXF version like 'AC1018' and this attribute can only be set by DXF version 'AC1018' or later.
        self.dxfversion = dxfversion
        self.getter = getter  # DXF entity getter method name for callback attributes
        self.setter = setter  # DXF entity setter method name for callback attributes
        self.alias = alias

    def __str__(self):
        return "({}, {})".format(self.name, self.code)

    def __repr__(self):
        return "DXFAttr" + self.__str__()

    def get_callback_value(self, entity: 'DXFEntity') -> 'TagValue':
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

    def set_callback_value(self, entity: 'DXFEntity', value: 'TagValue') -> None:
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


class DXFAttributes:
    def __init__(self, *subclassdefs: DefSubclass):
        self._subclasses = []  # type: List[DefSubclass]
        self._attribs = {}  # type: Dict[str, DXFAttr]
        for subclass in subclassdefs:
            self.add_subclass(subclass)

    def add_subclass(self, subclass: DefSubclass) -> None:
        subclass_index = len(self._subclasses)
        self._subclasses.append(subclass)
        self._add_subclass_attribs(subclass, subclass_index)

    def _add_subclass_attribs(self, subclass: DefSubclass, subclass_index: int) -> None:
        for name, dxfattrib in subclass.attribs.items():
            dxfattrib.name = name
            dxfattrib.subclass = subclass_index
            self._attribs[name] = dxfattrib

    def __getitem__(self, name: str) -> DXFAttr:
        return self._attribs[name]

    def __contains__(self, name: str) -> bool:
        return name in self._attribs

    def get(self, key: str, default: Any = None) -> Any:
        return self._attribs.get(key, default)

    def keys(self) -> KeysView[str]:
        return self._attribs.keys()

    def items(self) -> ItemsView[str, DXFAttr]:
        return self._attribs.items()

    def subclasses(self) -> Iterable[DefSubclass]:
        return iter(self._subclasses)

    def build_group_code_items(self, func=lambda x: True):
        for name, attrib in self.items():
            if attrib.code > 0 and func(name):  # skip internal tags
                yield attrib.code, name
