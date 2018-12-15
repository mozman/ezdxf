# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from typing import TYPE_CHECKING
from .dxfobjects import DefSubclass, DXFAttr, DXFAttributes, none_subclass, ExtendedTags
from .idbuffer import IDBuffer, PackedHandles, replace_tags

from ezdxf.lldxf import loader

if TYPE_CHECKING:
    from ezdxf.eztypes import Tags

_FIELDLIST_CLS = """0
CLASS
1
FIELDLIST
2
AcDbFieldList
3
ObjectDBX Classes
90
1152
91
0
280
0
281
0
"""

_FIELDLIST_TPL = """0
FIELDLIST
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
AcDbIdSet
90
12
100
AcDbFieldList
"""


@loader.register('FIELDLIST', legacy=False)
def tag_processor(tags: ExtendedTags) -> ExtendedTags:
    subclass = tags.get_subclass('AcDbFieldList')
    flist = PackedHandles(handles=(tag.value for tag in subclass[1:]))
    replace_tags(subclass, codes=(330, ), packed_data=flist)
    return tags


class FieldList(IDBuffer):
    __slots__ = ()
    TEMPLATE = tag_processor(ExtendedTags.from_text(_FIELDLIST_TPL))
    CLASS = ExtendedTags.from_text(_FIELDLIST_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbIdSet',
                    {
                        'flags': DXFAttr(90),  # not documented by Autodesk
                    }),
        DefSubclass('AcDbFieldList', {}),
    )

    @property
    def buffer_subclass(self) -> 'Tags':
        return self.tags.subclasses[2]  # 3rd subclass
