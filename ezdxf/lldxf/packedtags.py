# created: 19.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from array import array
from abc import abstractmethod
from collections import OrderedDict
from .types import DXFTag, strtag2
from ..tools import take2


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
        return ''.join(strtag2(tag) for tag in self.dxftags())


class TagArray(PackedTags):
    code = -100  # compatible with DXFTag.code
    VALUE_CODE = 60
    DTYPE = 'i'
    __slots__ = ('value', )

    def __init__(self, data=None):
        if data is None:
            data = []
        self.value = array(self.DTYPE, data)  # compatible with DXFTag.value

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


class TagDict(PackedTags):
    code = -101  # compatible with DXFTag.code
    KEY_CODE = 3
    VALUE_CODE = 350
    SEARCH_CODES = (350, 360, 3)  # some DICTIONARY have 360 handles
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
        return cls(data=((k, v) for k, v in take2(tag.value for tag in tags if tag.code in cls.SEARCH_CODES)))


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
