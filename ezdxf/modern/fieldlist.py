# Created: 12.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from ..lldxf.types import DXFTag
from .dxfobjects import DefSubclass, DXFAttr, DXFAttributes, none_subclass, ExtendedTags
from .idbuffer import IDBuffer

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


class FieldList(IDBuffer):
    TEMPLATE = ExtendedTags.from_text(_FIELDLIST_TPL)
    CLASS = ExtendedTags.from_text(_FIELDLIST_CLS)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        DefSubclass('AcDbIdSet',
                    {
                        'flags': DXFAttr(90),  # not documented by Autodesk
                    }),
        DefSubclass('AcDbFieldList', {}),
    )
    BUFFER_START_INDEX = 2
