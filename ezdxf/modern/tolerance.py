# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


_TOLERANCE_TPL = """0
TOLERANCE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbFcf
3
STANDARD
10
0.0
20
0.0
30
0.0
1

11
1.0
21
0.0
31
0.0
"""

tolerance_subclass = DefSubclass('AcDbFcf', {
    'dimstyle': DXFAttr(3),
    'insert': DXFAttr(10, xtype='Point3D'),  # Insertion point (in WCS)
    'content': DXFAttr(1),  # String representing the visual representation of the tolerance
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0, 0, 1)),  # Extrusion direction
    'x_axis_vector': DXFAttr(11, xtype='Point3D'),  # X-axis direction vector (in WCS)
})


class Tolerance(ModernGraphicEntity):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_TOLERANCE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, tolerance_subclass)
