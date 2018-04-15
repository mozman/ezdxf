# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.types import DXFTag
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, none_subclass, ExtendedTags


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
    TEMPLATE = ExtendedTags.from_text(_IDBUFFER_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, DefSubclass('AcDbIdBuffer', {}))
    BUFFER_START_INDEX = 1

    @property
    def buffer_subclass(self):
        return self.tags.subclasses[1]  # 2nd subclass

    def get_ids(self):
        return [tag.value for tag in self.buffer_subclass[self.BUFFER_START_INDEX:]]

    def set_ids(self, handles):
        self.buffer_subclass[self.BUFFER_START_INDEX:] = [DXFTag(330, handle) for handle in handles]

    def __len__(self):
        return len(self.buffer_subclass)-self.BUFFER_START_INDEX

    def __iter__(self):
        return iter(self.get_ids())

    def __getitem__(self, item):
        return self.get_ids()[item]

    def __setitem__(self, item, value):
        handles = self.get_ids()
        handles[item] = value
        self.set_ids(handles)

    def __delitem__(self, key):
        handles = self.get_ids()
        del handles[key]
        self.set_ids(handles)

    def append(self, handle):
        self.buffer_subclass.append(DXFTag(330, handle))

    def __iadd__(self, handle):
        self.append(handle)
        return self
