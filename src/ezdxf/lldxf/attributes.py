# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
from collections import namedtuple
from enum import Enum
from typing import Any, List, Dict, ItemsView, KeysView, TYPE_CHECKING
from .const import DXFAttributeError, DXF12

if TYPE_CHECKING:
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
    """ Defines a DXF attribute, accessible by DXFEntity.dxf.name.

    Extended Attribute Types
    ------------------------

    - XType.point2d:  2D points only
    - XType.point3d:  3D point only
    - XType.any_point:  mixed 2D/3D point
    - XType.callback: Calls get_value(entity) to get the value of DXF
      attribute 'name', and calls set_value(entity, value) to set value
      of DXF attribute 'name'.

    For example definitions see: ezdxf.entities.dxfgfx.acdb_entity.

    """

    def __init__(
            self,
            code: int,
            subclass: int = 0,
            xtype: XType = None,
            default=None,
            optional=False,
            dxfversion: str = DXF12,
            getter: str = None,
            setter: str = None,
            alias: str = None,
    ):

        # Attribute name set by DXFAttributes._add_subclass_attribs()
        self.name: str = ''

        # DXF group code
        self.code: int = code

        # Subclass index [0, n-1], n is the count of subclasses
        self.subclass: int = subclass

        # Extended attribute type:
        self.xtype: XType = xtype

        # DXF default value
        self.default: TagValue = default

        # If optional is True, this attribute will be exported to DXF files
        # only if the given value differs from default value.
        self.optional: bool = optional

        # This attribute is valid for all DXF versions starting from the
        # specified DXF version, default is DXF12 = 'AC1009'
        self.dxfversion: str = dxfversion

        # DXF entity getter method name for callback attributes
        self.getter: str = getter

        # DXF entity setter method name for callback attributes
        self.setter: str = setter

        # Alternative name for this attribute
        self.alias: str = alias

    def __str__(self) -> str:
        return f'({self.name}, {self.code})'

    def __repr__(self) -> str:
        return 'DXFAttr' + self.__str__()

    def get_callback_value(self, entity: 'DXFEntity') -> 'TagValue':
        """
        Executes a callback function in 'entity' to get a DXF value.

        Callback function is defined by self.getter as string.

        Args:
            entity: DXF entity

        Raises:
            AttributeError: getter method does not exist
            TypeError: getter is None

        Returns:
            DXF attribute value

        """
        try:
            return getattr(entity, self.getter)()
        except AttributeError:
            raise DXFAttributeError(
                f'DXF attribute {self.name}: invalid getter {self.getter}.'
            )
        except TypeError:
            raise DXFAttributeError(
                f'DXF attribute {self.name} has no getter.'
            )

    def set_callback_value(self, entity: 'DXFEntity',
                           value: 'TagValue') -> None:
        """ Executes a callback function in 'entity' to set a DXF value.

        Callback function is defined by self.setter as string.

        Args:
            entity: DXF entity
            value: DXF attribute value

        Raises:
            AttributeError: setter method does not exist
            TypeError: setter is None

        """
        try:
            getattr(entity, self.setter)(value)
        except AttributeError:
            raise DXFAttributeError(
                f'DXF attribute {self.name}: invalid setter {self.setter}.'
            )
        except TypeError:
            raise DXFAttributeError(
                f'DXF attribute {self.name} has no setter.'
            )


class DXFAttributes:
    def __init__(self, *subclassdefs: DefSubclass):
        self._subclasses: List[DefSubclass] = []
        self._attribs: Dict[str, DXFAttr] = {}
        for subclass in subclassdefs:
            self.add_subclass(subclass)

    def add_subclass(self, subclass: DefSubclass) -> None:
        subclass_index = len(self._subclasses)
        self._subclasses.append(subclass)
        self._add_subclass_attribs(subclass, subclass_index)

    def _add_subclass_attribs(self, subclass: DefSubclass,
                              subclass_index: int) -> None:
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

    def build_group_code_items(self, func=lambda x: True):
        for name, attrib in self.items():
            if attrib.code > 0 and func(name):  # skip internal tags
                yield attrib.code, name
