# Created: 20.03.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .graphics import none_subclass, entity_subclass, DXFAttr, DXFAttributes, DefSubclass, ExtendedTags
from .solid3d import Body, modeler_geometry_subclass

_SURFACE_TPL = """  0
SURFACE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbModelerGeometry
70
1
100
AcDbSurface
71
0
72
0
"""

surface_subclass = DefSubclass('AcDbSurface', {
    'u_count': DXFAttr(71),
    'v_count': DXFAttr(72),
})


class Surface(Body):
    TEMPLATE = ExtendedTags.from_text(_SURFACE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, modeler_geometry_subclass, surface_subclass)
