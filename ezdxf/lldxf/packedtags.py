# created: 19.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from array import array
from abc import abstractmethod
from collections import OrderedDict
from .types import DXFTag, DXFVertex
from ..tools import take2
from ..tools.indexing import Index
from .const import DXFTypeError, DXFIndexError, DXFValueError


class PackedTags(object):
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


class TagArray(TagList):
    code = -101  # compatible with DXFTag.code
    VALUE_CODE = 60
    DTYPE = 'i'
    __slots__ = ('value', )

    def __init__(self, data=None):
        if data is None:
            data = []
        self.value = array(self.DTYPE, data)  # compatible with DXFTag.value

    def set_values(self, values):
        self.value[:] = array(self.DTYPE, values)


class TagDict(PackedTags):
    code = -102  # compatible with DXFTag.code
    KEY_CODE = 3
    VALUE_CODE = 350
    SEARCH_CODES = (3, 350, 360)  # some DICTIONARY have 360 handles
    __slots__ = ('value', )

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


class VertexTags(PackedTags):
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
            return list(self._slicing(index))
        else:
            return self._get_point(Index(self).index(index, error=DXFIndexError))

    def __setitem__(self, index, point):
        if isinstance(index, slice):
            raise DXFTypeError('slicing not supported')
        else:
            self._set_point(Index(self).index(index, error=DXFIndexError), point)

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

    def _slicing(self, s):
        for index in Index(self).slicing(s):
            yield self._get_point(index)

    def _get_point(self, index):
        size = self.VERTEX_SIZE
        index = index * size
        return tuple(self.value[index:index+size])

    def _set_point(self, index, point):
        size = self.VERTEX_SIZE
        if len(point) != size:
            raise DXFValueError('point requires exact {} components.'.format(size))
        if isinstance(point, (tuple, list)):
            point = array('d', point)
        index = index * size
        self.value[index:index+size] = point

    def dxftags(self):
        for point in self:
            yield DXFVertex(self.VERTEX_CODE, point)

    def append(self, point):
        # PackedPoints does not maintain the point count attribute!
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
