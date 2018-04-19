# created: 19.04.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from array import array
from .types import DXFTag, strtag2


class TagArray(object):
    def __init__(self, code, values, dtype='f'):
        self.code = int(code)
        self.values = array(dtype, values)

    def dxftags(self):
        code = self.code
        for value in self.values:
            yield DXFTag(code, value)

    def dxfstr(self):
        def to_string():
            for tag in self.dxftags():
                yield strtag2(tag)
        return ''.join(to_string())


class MultiTagArray(object):
    pass


class TagDict(object):
    pass
