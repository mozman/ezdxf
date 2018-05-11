# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
import array
from ..lldxf.types import DXFTag
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, none_subclass, ExtendedTags
from ..lldxf.packedtags import PackedTags, replace_tags
from ..lldxf import loader
from ..tools.c23 import PY3


def new_array(values=None):
    # Handles are 64bit values and Python2 does not support 64bit values in array, using list() instead of array() for
    # Python 2. (removed when official Python 2 support ends at 01.01.2020)
    a = array.array('Q') if PY3 else list()
    if values is not None:
        a.extend(values)
    return a


class PackedHandles(PackedTags):
    code = -330  # compatible with DXFTag.code
    __slots__ = ('value', )

    def __init__(self, handles=None):
        # compatible with DXFTag.value
        self.value = new_array(int(value, 16) for value in handles)

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return ['%X' % v for v in self.value[item]]
        else:
            return '%X' % self.value[item]

    def __setitem__(self, item, value):
        if isinstance(value, (tuple, list)):
            value = new_array(int(value, 16) for value in value)
        else:
            value = int(value, 16)
        self.value[item] = value

    def __delitem__(self, item):
        del self.value[item]

    def __iadd__(self, value):
        self.append(value)
        return self

    def __eq__(self, other):
        return self.value == new_array(int(handle, 16) for handle in other)

    def append(self, handle):
        self.value.append(int(handle, 16))

    def extend(self, handles):
        self.value.extend(int(handle, 16) for handle in handles)

    def dxftags(self):
        for handle in self.value:
            yield DXFTag(330, "%X" % handle)

    def clone(self):
        return self.__class__(handles=self.value)

    def clear(self):
        del self.value[:]


@loader.register('IDBUFFER', legacy=False)
def tag_processor(tags):
    subclass = tags.get_subclass('AcDbIdBuffer')
    id_buffer = PackedHandles(handles=(tag.value for tag in subclass[1:]))
    replace_tags(subclass, codes=(330, ), packed_data=id_buffer)
    return tags


_IDBUFFER_TPL = """0
IDBUFFER
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbIdBuffer
"""


class IDBuffer(DXFObject):
    __slots__ = ('_cached_handles', )
    TEMPLATE = tag_processor(ExtendedTags.from_text(_IDBUFFER_TPL))
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbIdBuffer', {}))

    @property
    def buffer_subclass(self):
        return self.tags.subclasses[1]  # 2nd subclass

    @property
    def handles(self):
        try:
            return self._cached_handles
        except AttributeError:
            self._cached_handles = self.buffer_subclass.get_first_tag(PackedHandles.code)
            return self._cached_handles

    @handles.setter
    def handles(self, items):
        self.handles[:] = list(items)


