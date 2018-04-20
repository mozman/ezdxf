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

    def dxfstr(self):
        """
        Returns the DXF strings constructed from dxftags().

        """
        return ''.join(strtag2(tag) for tag in self.dxftags())


class TagArray(PackedTags):
    def __init__(self, code, values, dtype='f'):
        self.code = int(code)
        self.values = array(dtype, values)

    def dxftags(self):
        code = self.code
        for value in self.values:
            yield DXFTag(code, value)


class TagDict(PackedTags):
    pass
