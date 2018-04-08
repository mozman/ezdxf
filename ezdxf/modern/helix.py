# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass
from .spline import Spline, spline_subclass

_HELIX_TPL = """0
HELIX
5
0
330
0
100
AcDbEntity
8
0
100
AcDbSpline
70
0
71
3
72
0
73
0
74
0
100
AcDbHelix
90
29
91
63
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
12
0.0
22
0.0
32
1.0
40
1.0
41
1.0
42
1.0
290
1
280
1
"""

helix_subclass = DefSubclass('AcDbHelix', {
    'major_release_number': DXFAttr(90),
    'maintenance_release_number': DXFAttr(91),
    'axis_base_point': DXFAttr(10, xtype='Point3D'),
    'start_point': DXFAttr(11, xtype='Point3D'),
    'axis_vector': DXFAttr(12, xtype='Point3D'),
    'radius': DXFAttr(40),
    'turns': DXFAttr(41),
    'turn_height': DXFAttr(42),
    'handedness': DXFAttr(290),  # Handedness: 0=left, 1=right
    'constrain': DXFAttr(280),  # Constrain type: 0= Constrain turn height; 1= Constrain turns; 2= Constrain height
})


class Helix(Spline):
    # Requires AC1021/R2007
    TEMPLATE = ExtendedTags.from_text(_HELIX_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, spline_subclass, helix_subclass)
