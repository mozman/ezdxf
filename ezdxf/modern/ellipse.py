# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


_ELLIPSE_TPL = """0
ELLIPSE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbEllipse
10
0.0
20
0.0
30
0.0
11
1.0
21
0.0
31
0.0
40
1.0
41
0.0
42
6.283185307179586
"""

ellipse_subclass = DefSubclass('AcDbEllipse', {
    'center': DXFAttr(10, xtype='Point2D/3D'),
    'major_axis': DXFAttr(11, xtype='Point2D/3D'),  # relative to the center
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    'ratio': DXFAttr(40),
    'start_param': DXFAttr(41),  # this value is 0.0 for a full ellipse
    'end_param': DXFAttr(42),  # this value is 2*pi for a full ellipse
})


class Ellipse(ModernGraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_ELLIPSE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ellipse_subclass)
