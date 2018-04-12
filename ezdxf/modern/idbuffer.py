# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.types import DXFTag
from .dxfobjects import DXFObject, DefSubclass, DXFAttributes, DXFAttr, none_subclass, ExtendedTags


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

    @property
    def buffer_subclass(self):
        return self.tags.subclasses[1]  # 2nd subclass

    def __len__(self):
        return len(self.buffer_subclass)-1

    def get_ids(self):
        return [tag.value for tag in self.buffer_subclass[1:]]

    def set_ids(self, handles):
        self.buffer_subclass[1:] = [DXFTag(330, handle) for handle in handles]
