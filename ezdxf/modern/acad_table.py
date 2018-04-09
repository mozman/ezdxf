# Created: 09.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity

_ACAD_TABLE_CLS = """0
CLASS
1
ACAD_TABLE
2
AcDbTable
3
ObjectDBX Classes
90
1025
91
0
280
0
281
1
"""

_ACAD_TABLE_TPL = """  0
ACAD_TABLE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbBlockReference
2
*T1
10
0.0
20
0.0
30
0.0
100
AcDbTable
280
0
342
7F
343
283
11
1.0
21
0.0
31
0.0
90
22
91
4
92
5
93
0
94
0
95
0
96
0
141
11.0
141
9.0
141
9.0
141
9.0
142
70.40972631711483
142
70.40972631711483
142
70.40972631711483
142
70.40972631711483
142
70.40972631711483
171
1
172
0
173
0
174
0
175
5
176
1
91
262144
178
0
145
0.0
92
0
"""

block_reference_subclass = DefSubclass('AcDbBlockReference', {
    'block_name': DXFAttr(2),  # Block name; an anonymous block begins with a *T value
    'insert': DXFAttr(10, xtype='Point3D'),  # Insertion point
})

table_subclass = DefSubclass('AcDbTable', {
    'version': DXFAttr(280),  # Table data version number: 0 = 2010
})


class ACADTable(ModernGraphicEntity):
    # Requires AC1024/R2010
    TEMPLATE = ExtendedTags.from_text(_ACAD_TABLE_TPL)
    CLASS = ExtendedTags.from_text(_ACAD_TABLE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, block_reference_subclass, table_subclass)

    @property
    def AcDbTable(self):
        return self.tags.subclasses[3]
