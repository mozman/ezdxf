# created: 19.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from array import array
from abc import abstractmethod
from collections import OrderedDict
from typing import Iterable, Tuple, Sequence, Mapping, Union

from .types import DXFTag, DXFVertex
from .const import DXFTypeError, DXFIndexError, DXFValueError

from .tags import Tags
from ezdxf.tools import take2
from ezdxf.tools.indexing import Index


def array_from_tags(tags: Tags, code: int, dtype='f') -> array:
    return array(dtype, (tag.value for tag in tags if tag.code == code))


class PackedTags:
    __slots__ = ()

    @abstractmethod
    def dxftags(self) -> Iterable[DXFTag]:
        """
        Yield packed tags as unpacked DXFTags().

        """
        pass

    @abstractmethod
    def clone(self) -> 'PackedTags':
        """
        Returns cloned tags (deep copy).

        """
        pass

    def dxfstr(self) -> str:
        """
        Returns the DXF strings constructed from dxftags().

        """
        return ''.join(tag.dxfstr() for tag in self.dxftags())


class TagList(PackedTags):
    code = -100  # compatible with DXFTag.code
    VALUE_CODE = 330
    __slots__ = ('value',)

    def __init__(self, data=None):
        self.value = list(data or [])  # compatible with DXFTag.value

    def dxftags(self) -> Iterable[DXFTag]:
        for value in self.value:
            yield DXFTag(self.VALUE_CODE, value)

    def clone(self) -> 'TagList':
        return self.__class__(data=self.value)

    def replace_tags(self, tags: Tags):
        return replace_tags(tags, codes=(self.VALUE_CODE,), packed_data=self)

    @classmethod
    def from_tags(cls, tags: Tags) -> 'TagList':
        return cls(data=(tag.value for tag in tags if tag.code == cls.VALUE_CODE))

    def clear(self) -> None:
        del self.value[:]


class TagArray(TagList):
    code = -101  # compatible with DXFTag.code
    VALUE_CODE = 60
    DTYPE = 'i'

    def __init__(self, data: Iterable = None):
        self.value = array(self.DTYPE, data or [])  # compatible with DXFTag.value

    def set_values(self, values: Iterable) -> None:
        self.value[:] = array(self.DTYPE, values)


class TagDict(PackedTags):
    __slots__ = ('value',)
    code = -102  # compatible with DXFTag.code
    KEY_CODE = 3
    VALUE_CODE = 350
    SEARCH_CODES = (3, 350, 360)  # some DICTIONARY have 360 handles

    def __init__(self, data: Union[Mapping, Iterable[Tuple]] = None):
        self.value = OrderedDict(data or {})  # compatible with DXFTag.value

    def dxftags(self) -> Iterable[DXFTag]:
        for key, value in self.value.items():
            yield DXFTag(self.KEY_CODE, key)
            yield DXFTag(self.VALUE_CODE, value)

    def clone(self) -> 'TagDict':
        return self.__class__(data=self.value)

    def replace_tags(self, tags: Tags):
        return replace_tags(tags, codes=self.SEARCH_CODES, packed_data=self)

    @classmethod
    def from_tags(cls, tags: Tags) -> 'TagDict':
        return cls(data=(t for t in take2(tag.value for tag in tags if tag.code in set(cls.SEARCH_CODES))))


class VertexArray(PackedTags):
    code = -10  # compatible with DXFTag.code
    VERTEX_CODE = 10
    VERTEX_SIZE = 3  # set to 2 for 2d points
    __slots__ = ('value',)

    def __init__(self, data: Iterable = None):
        self.value = array('d', data or [])  # compatible with DXFTag.value

    def __len__(self) -> int:
        return len(self.value) // self.VERTEX_SIZE

    def __getitem__(self, index: int):
        if isinstance(index, slice):
            return list(self._get_points(self._slicing(index)))
        else:
            return self._get_point(self._index(index))

    def __setitem__(self, index: int, point: Sequence[float]) -> None:
        if isinstance(index, slice):
            raise DXFTypeError('slicing not supported')
        else:
            self._set_point(self._index(index), point)

    def __delitem__(self, index: int) -> None:
        if isinstance(index, slice):
            self._del_points(self._slicing(index))
        else:
            self._del_point(self._index(index))

    def insert(self, pos: int, point: Sequence[float]):
        """
        Insert point in front of point at index pos.

        Args:
            pos: insert position
            point: point as tuple

        """
        size = self.VERTEX_SIZE
        if len(point) != size:
            raise DXFValueError('point requires exact {} components.'.format(size))

        pos = self._index(pos) * size
        _insert = self.value.insert
        for value in reversed(point):
            _insert(pos, value)

    def clone(self) -> 'VertexArray':
        return self.__class__(data=self.value)

    @classmethod
    def from_tags(cls, tags: Iterable[DXFTag]) -> 'VertexArray':
        """
        Setup point array from extended tags.

        Args:
            tags: Tags() object

        """
        vertices = array('d')
        for tag in tags:
            if tag.code == cls.VERTEX_CODE:
                vertices.extend(tag.value)
        return cls(data=vertices)

    def _index(self, item) -> int:
        return Index(self).index(item, error=DXFIndexError)

    def _slicing(self, index) -> Iterable[int]:
        return Index(self).slicing(index)

    def _get_point(self, index: int) -> Sequence[float]:
        size = self.VERTEX_SIZE
        index = index * size
        return tuple(self.value[index:index + size])

    def _get_points(self, indices) -> Iterable:
        for index in indices:
            yield self._get_point(index)

    def _set_point(self, index: int, point: Sequence[float]):
        size = self.VERTEX_SIZE
        if len(point) != size:
            raise DXFValueError('point requires exact {} components.'.format(size))
        if isinstance(point, (tuple, list)):
            point = array('d', point)
        index = index * size
        self.value[index:index + size] = point

    def _del_point(self, index: int) -> None:
        size = self.VERTEX_SIZE
        pos = index * size
        del self.value[pos:pos + size]

    def _del_points(self, indices: Iterable[int]) -> None:
        del_flags = set(indices)
        size = self.VERTEX_SIZE
        survivors = array('d', (v for i, v in enumerate(self.value) if (i // size) not in del_flags))
        self.value = survivors

    def dxftags(self) -> Iterable[DXFVertex]:
        for point in self:
            yield DXFVertex(self.VERTEX_CODE, point)

    def append(self, point: Sequence[float]) -> None:
        if len(point) != self.VERTEX_SIZE:
            raise DXFValueError('point requires exact {} components.'.format(self.VERTEX_SIZE))
        self.value.extend(point)

    def extend(self, points: Iterable[Sequence[float]]) -> None:
        for point in points:
            self.append(point)

    def clear(self) -> None:
        del self.value[:]


def replace_tags(tags: Tags, codes: Sequence[int], packed_data: PackedTags):
    """
    Replace single DXF tags by packed data object.

    Args:
        tags: Tags() object
        codes: codes to replace as tuple
        packed_data: packed data object

    """
    try:
        pos = tags.tag_index(codes[0])
    except ValueError:
        pos = len(tags)
    tags.remove_tags(codes=codes)
    tags.insert(pos, packed_data)
