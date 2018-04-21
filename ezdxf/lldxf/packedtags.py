# created: 19.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from array import array
from abc import abstractmethod
from .types import DXFTag, strtag2


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
    def __init__(self, code, value, dtype='f'):
        self.code = int(code)
        self.value = array(dtype, value)

    def dxftags(self):
        code = self.code
        for value in self.value:
            yield DXFTag(code, value)

    def clone(self):
        return TagArray(self.code, self.value, self.value.typecode)


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


class TagDict(PackedTags):
    pass
