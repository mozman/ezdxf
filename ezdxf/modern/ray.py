# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


_RAY_TPL = """0
RAY
5
0
330
0
100
AcDbEntity
8
0
100
AcDbRay
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
"""
ray_subclass = DefSubclass('AcDbRay', {
    'start': DXFAttr(10, xtype='Point3D'),
    'unit_vector': DXFAttr(11, xtype='Point3D'),
})


class Ray(ModernGraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_RAY_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, ray_subclass)


class XLine(Ray):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_RAY_TPL.replace('RAY', 'XLINE'))
