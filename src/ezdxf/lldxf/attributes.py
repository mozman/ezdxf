# Copyright (c) 2011-2020, Manfred Moitzi
# License: MIT License
from collections import namedtuple
from enum import Enum
from typing import (
    Optional, Dict, Tuple, TYPE_CHECKING, Iterable, Callable, Any,
)
from .const import DXFAttributeError, DXF12
import copy

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
    callback = 4  # callback attribute


# Unique object as marker
RETURN_DEFAULT = object()


class DXFAttr:
    """ Represents a DXF attribute for an DXF entity, accessible by the
    DXF namespace :attr:`DXFEntity.dxf` like ``entity.dxf.color = 7``.
    This definitions are immutable by design not by implementation.

    Extended Attribute Types
    ------------------------

    - XType.point2d:  2D points only
    - XType.point3d:  3D point only
    - XType.any_point:  mixed 2D/3D point
    - XType.callback: Calls get_value(entity) to get the value of DXF
      attribute 'name', and calls set_value(entity, value) to set value
      of DXF attribute 'name'.

    See example definition: ezdxf.entities.dxfgfx.acdb_entity.

    """

    def __init__(
            self,
            code: int,
            xtype: XType = None,
            default=None,
            optional=False,
            dxfversion: str = DXF12,
            getter: str = None,
            setter: str = None,
            alias: str = None,
            validator: Optional[Callable[[Any], bool]] = None,
            fixer: Optional[Callable[[Any], Any]] = None,
    ):

        # Attribute name set by DXFAttributes.__init__()
        self.name: str = ''

        # DXF group code
        self.code: int = code

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

        # Returns True if given value is valid - the validator should be as
        # fast as possible!
        self.validator: Optional[Callable[[Any], bool]] = validator

        # Returns a fixed value for invalid attributes, the fixer is called
        # only if the validator returns False.
        if fixer is RETURN_DEFAULT:
            fixer = self._return_default
        self.fixer: Optional[Callable[[Any], Any]] = fixer

    def _return_default(self, x: Any) -> Any:
        return self.default

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

    def is_valid_value(self, value: Any) -> bool:
        if self.validator:
            return self.validator(value)
        else:
            return True


class DXFAttributes:
    __slots__ = ('_attribs',)

    def __init__(self, *subclassdefs: DefSubclass):
        self._attribs: Dict[str, DXFAttr] = dict()
        for subclass in subclassdefs:
            for name, dxfattrib in subclass.attribs.items():
                dxfattrib.name = name
                self._attribs[name] = dxfattrib
                if dxfattrib.alias:
                    alias = copy.copy(dxfattrib)
                    alias.name = dxfattrib.alias
                    alias.alias = dxfattrib.name
                    self._attribs[dxfattrib.alias] = alias

    def __contains__(self, name: str) -> bool:
        return name in self._attribs

    def get(self, key: str) -> Optional[DXFAttr]:
        return self._attribs.get(key)

    def build_group_code_items(
            self, func=lambda x: True) -> Iterable[Tuple[int, str]]:
        for name, attrib in self._attribs.items():
            # code < 0 is internal tag
            if attrib.code > 0 and func(name):
                yield attrib.code, name
