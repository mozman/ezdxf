# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created 2019-02-04
# concept for new tag system

# Goals:
# ------
#
# 1. Create an new DXFTag system based on better understanding and knowledge of real world requirements of the DXF format
# 2. Cython optimization as secondary goal in mind, but avoid manual memory management (malloc() and free()), use array
# 3. Store DXF entities as wrapped entities in the EntityDB with LAZY SETUP, load time should be fast and most entities
#    are never touched - especially when only data querying

# Single data:
# ------------
# - int
# - float
# - string
# DXF string represent a single tag

# Cython types for single data:
# -----------------------------
# - DXFInt (code: short, value: long)
# - DXFFloat (code: :short, value: double)
# - DXFAny (code: short, value: Py_Object)
# hidden behind factory function dxftag()


# Multi data:
# -----------
# - Vertex (3 float array)
# - Binary data
# - Long Strings (MTEXT)
# - LWVertex (5 float array)
# DXF string represent multiple tags

# Cython types for multi data:
# -----------------------------
# - DXFVertex (code: short, x: double, y: double,  z: double)
# - DXFLWVertex (code: short, x: double, y: double, s: float, e: float, b: double)
# - see no advantages for binary data and long strings over Python versions

# Packed Data:
# ------------
# - PackedList - list() of vales (string, Vector, LWPolylineVertex) with same group code
# - PackedArray - array() of values (integer (I), float (d), handles (Q) with same group code
# - PackedVectors - array() of (x, y[, z]) with same group code
# - PackedDict - dict() key, value pairs
#   key is a string,  same group code for all keys
#   value is a handle(str), same group code for all keys
# - see no advantages by Cython optimizations

# array.array codes:
# float: d (double)
# bytes: B (unsigned char), binary data
# int: L (unsigned long) 4 bytes, for Vertex indices
# int: Q (unsigned long long) 8 bytes for handles!

# -------------------------------------------------
# This optimization are postponed after 1.0 release
# -------------------------------------------------

from typing import TYPE_CHECKING, Union, Any
from reprlib import repr
from abc import abstractmethod

from ezdxf.math.vector import Vector
from ezdxf.lldxf.types import POINT_CODES, cast_tag_value

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

TAG_STRING_FORMAT = '%3d\n%s\n'
NONE_CODE = -9999


class AbstractTagValue:
    @abstractmethod
    def clone(self) -> 'AbstractTagValue':
        pass

    @abstractmethod
    def dxfstr(self, code: int) -> str:
        pass

    @abstractmethod
    def value(self) -> Any:
        pass


TagValueType = Union[int, float, str, AbstractTagValue]


class DXFTag:
    """
    Represents all DXF tags.

    """
    __slots__ = ('code', '_value')

    def __init__(self, code: int, value: TagValueType):
        self.code = code  # type: int
        self._value = value

    def __str__(self) -> str:
        return str((self.code, repr(self.value)))

    def __repr__(self) -> str:
        return "DXFTag{}".format(str(self))

    @property
    def value(self) -> Any:
        return self._value.value if hasattr(self._value, 'value') else self._value

    @property
    def is_single_tag_value(self):
        return not issubclass(self._value.__class__, AbstractTagValue)

    def __eq__(self, other: 'DXFTag') -> bool:
        if self.code == other.code:
            return self._value == other._value
        return False

    def dxfstr(self) -> str:
        if self.is_single_tag_value:
            return TAG_STRING_FORMAT % (self.code, str(self._value))
        else:
            return self.value.dxfstr(self.code)

    def clone(self) -> 'DXFTag':
        if self.is_single_tag_value:
            value = self._value
        else:
            value = self._value.clone()
        return self.__class__(self.code, value)


# Special marker tag
NONE_TAG = DXFTag(NONE_CODE, NONE_CODE)


class VectorData(AbstractTagValue):
    __slots__ = ('_data', )

    def __init__(self, vector: 'Vertex'):
        self._data = Vector(vector)

    def clone(self):
        return self.__class__(self._data)

    def value(self):
        return self._data

    def dxfstr(self, code: int) -> str:
        raise NotImplemented()


class BinaryData(AbstractTagValue):
    __slots__ = ('_data', )

    def value(self):
        raise NotImplemented()

    def clone(self):
        raise NotImplemented()

    def dxfstr(self, code: int) -> str:
        raise NotImplemented()


class LongString(AbstractTagValue):
    __slots__ = ('_data', )

    def value(self):
        raise NotImplemented()

    def clone(self):
        raise NotImplemented()

    def dxfstr(self, code: int) -> str:
        raise NotImplemented()


class LWVertex(AbstractTagValue):
    __slots__ = ('_data', )

    def value(self):
        raise NotImplemented()

    def clone(self):
        raise NotImplemented()

    def dxfstr(self, code: int) -> str:
        raise NotImplemented()


def dxftag(code: int, data: Any, type_: str = None) -> DXFTag:
    """
    Factory function to creat DXF tags.

    Args:
        code: DXF group code
        data: tag value
        type_: type hints for faster processing

    Returns: DXFTag() object

    """
    code = int(code)
    if type_ == 'vector' or (code in POINT_CODES):
        value = VectorData(data)
    else:
        value = cast_tag_value(code, data)
    return DXFTag(code, value)
