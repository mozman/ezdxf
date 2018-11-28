# created: 19.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from array import array
from abc import abstractmethod
from collections import OrderedDict

from .types import DXFTag, DXFVertex
from .const import DXFTypeError, DXFIndexError, DXFValueError

from ezdxf.tools import take2
from ezdxf.tools.indexing import Index


class PackedTags:
    __slots__ = ()

    @abstractmethod
    def dxftags(self):
        """
        Yield packed tags as unpacked DXFTags().

        """
        pass

    @abstractmethod
    def clone(self):
        """
        Returns cloned tags (deep copy).

        """
        pass

    def dxfstr(self):
        """
        Returns the DXF strings constructed from dxftags().

        """
        return ''.join(tag.dxfstr() for tag in self.dxftags())


class TagList(PackedTags):
    code = -100  # compatible with DXFTag.code
    VALUE_CODE = 330
    __slots__ = ('value', )

    def __init__(self, data=None):
        if data is None:
            data = []
        self.value = list(data)  # compatible with DXFTag.value

    def dxftags(self):
        for value in self.value:
            yield DXFTag(self.VALUE_CODE, value)

    def clone(self):
        return self.__class__(data=self.value)

    def replace_tags(self, tags):
        return replace_tags(tags, codes=(self.VALUE_CODE, ), packed_data=self)

    @classmethod
    def from_tags(cls, tags):
        return cls(data=(tag.value for tag in tags if tag.code == cls.VALUE_CODE))

    def clear(self):
        del self.value[:]


class TagArray(TagList):
    code = -101  # compatible with DXFTag.code
    VALUE_CODE = 60
    DTYPE = 'i'

    def __init__(self, data=None):
        if data is None:
            data = []
        self.value = array(self.DTYPE, data)  # compatible with DXFTag.value

    def set_values(self, values):
        self.value[:] = array(self.DTYPE, values)


class TagDict(PackedTags):
    __slots__ = ('value',)
    code = -102  # compatible with DXFTag.code
    KEY_CODE = 3
    VALUE_CODE = 350
    SEARCH_CODES = (3, 350, 360)  # some DICTIONARY have 360 handles

    def __init__(self, data=None):
        self.value = OrderedDict(data if data is not None else {})  # compatible with DXFTag.value

    def dxftags(self):
        for key, value in self.value.items():
            yield DXFTag(self.KEY_CODE, key)
            yield DXFTag(self.VALUE_CODE, value)

    def clone(self):
        return self.__class__(data=self.value)

    def replace_tags(self, tags):
        return replace_tags(tags, codes=self.SEARCH_CODES, packed_data=self)

    @classmethod
    def from_tags(cls, tags):
        return cls(data=((k, v) for k, v in take2(tag.value for tag in tags if tag.code in set(cls.SEARCH_CODES))))


class VertexArray(PackedTags):
    code = -10  # compatible with DXFTag.code
    VERTEX_CODE = 10
    VERTEX_SIZE = 3  # set to 2 for 2d points
    __slots__ = ('value', )

    def __init__(self, data=None):
        if data is None:
            data = []
        self.value = array('d', data)  # compatible with DXFTag.value

    def __len__(self):
        return len(self.value) // self.VERTEX_SIZE

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(self._get_points(self._slicing(index)))
        else:
            return self._get_point(self._index(index))

    def __setitem__(self, index, point):
        if isinstance(index, slice):
            raise DXFTypeError('slicing not supported')
        else:
            self._set_point(self._index(index), point)

    def __delitem__(self, index):
        if isinstance(index, slice):
            self._del_points(self._slicing(index))
        else:
            self._del_point(self._index(index))

    def insert(self, pos, point):
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

    def clone(self):
        return self.__class__(data=self.value)

    @classmethod
    def from_tags(cls, tags):
        """
        Setup point array from extended tags.

        Args:
            tags: ExtendedTags() object

        """
        vertices = array('d')
        for tag in tags:
            if tag.code == cls.VERTEX_CODE:
                vertices.extend(tag.value)
        return cls(data=vertices)

    def _index(self, item):
        return Index(self).index(item, error=DXFIndexError)

    def _slicing(self, index):
        return Index(self).slicing(index)

    def _get_point(self, index):
        size = self.VERTEX_SIZE
        index = index * size
        return tuple(self.value[index:index+size])

    def _get_points(self, indices):
        for index in indices:
            yield self._get_point(index)

    def _set_point(self, index, point):
        size = self.VERTEX_SIZE
        if len(point) != size:
            raise DXFValueError('point requires exact {} components.'.format(size))
        if isinstance(point, (tuple, list)):
            point = array('d', point)
        index = index * size
        self.value[index:index+size] = point

    def _del_point(self, index):
        size = self.VERTEX_SIZE
        pos = index * size
        del self.value[pos:pos+size]

    def _del_points(self, indices):
        del_flags = set(indices)
        size = self.VERTEX_SIZE
        survivors = array('d', (v for i, v in enumerate(self.value) if (i//size) not in del_flags))
        self.value = survivors

    def dxftags(self):
        for point in self:
            yield DXFVertex(self.VERTEX_CODE, point)

    def append(self, point):
        if len(point) != self.VERTEX_SIZE:
            raise DXFValueError('point requires exact {} components.'.format(self.VERTEX_SIZE))
        self.value.extend(point)

    def extend(self, points):
        for point in points:
            self.append(point)

    def clear(self):
        del self.value[:]


def replace_tags(tags, codes, packed_data):
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
