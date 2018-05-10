# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..legacy import insert
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntityExtension


_INSERT_TPL = """0
INSERT
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
BLOCKNAME
10
0.0
20
0.0
30
0.0
41
1.0
42
1.0
43
1.0
50
0.0
"""

insert_subclass = DefSubclass('AcDbBlockReference', {
    'attribs_follow': DXFAttr(66, default=0),
    'name': DXFAttr(2),
    'insert': DXFAttr(10, xtype='Point2D/3D'),
    'xscale': DXFAttr(41, default=1.0),
    'yscale': DXFAttr(42, default=1.0),
    'zscale': DXFAttr(43, default=1.0),
    'rotation': DXFAttr(50, default=0.0),
    'column_count': DXFAttr(70, default=1),
    'row_count': DXFAttr(71, default=1),
    'column_spacing': DXFAttr(44, default=0.0),
    'row_spacing': DXFAttr(45, default=0.0),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})


class Insert(insert.Insert, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_INSERT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, insert_subclass)
