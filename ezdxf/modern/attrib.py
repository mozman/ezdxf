# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from ..legacy import attrib
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntityExtension


_ATTDEF_TPL = """0
ATTDEF
5
0
330
0
100
AcDbEntity
8
0
100
AcDbText
10
0.0
20
0.0
30
0.0
40
1.0
1
DEFAULTTEXT
50
0.0
51
0.0
41
1.0
7
STANDARD
71
0
72
0
11
0.0
21
0.0
31
0.0
100
AcDbAttributeDefinition
3
PROMPTTEXT
2
TAG
70
0
73
0
74
0
"""

attdef_subclass = (
    DefSubclass('AcDbText', {
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'thickness': DXFAttr(39, default=0.0),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),
        'width': DXFAttr(41, default=1.0),
        'oblique': DXFAttr(51, default=0.0),
        'style': DXFAttr(7, default='STANDARD'),
        'text_generation_flag': DXFAttr(71, default=0),
        'halign': DXFAttr(72, default=0),
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    }),
    DefSubclass('AcDbAttributeDefinition', {
        'prompt': DXFAttr(3),
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'valign': DXFAttr(74, default=0),
    })
)


class Attdef(attrib.Attdef, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_ATTDEF_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *attdef_subclass)


_ATTRIB_TPL = """0
ATTRIB
5
0
330
0
100
AcDbEntity
8
0
100
AcDbText
10
0.0
20
0.0
30
0.0
40
1.0
1
DEFAULTTEXT
50
0.0
51
0.0
41
1.0
7
STANDARD
72
0
11
0.0
21
0.0
31
0.0
100
AcDbAttribute
2
TAG
70
0
71
0
73
0
74
0
"""
attrib_subclass = (
    DefSubclass('AcDbText', {
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'thickness': DXFAttr(39, default=0.0),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),  # error in DXF description, because placed in 'AcDbAttribute'
        'width': DXFAttr(41, default=1.0),  # error in DXF description, because placed in 'AcDbAttribute'
        'oblique': DXFAttr(51, default=0.0),  # error in DXF description, because placed in 'AcDbAttribute'
        'style': DXFAttr(7, default='STANDARD'),  # error in DXF description, because placed in 'AcDbAttribute'
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),  # error in DXF description, because placed in 'AcDbAttribute'
        'halign': DXFAttr(72, default=0),
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
    }),
    DefSubclass('AcDbAttribute', {
        'tag': DXFAttr(2),
        'flags': DXFAttr(70),
        'field_length': DXFAttr(73, default=0),
        'text_generation_flag': DXFAttr(71, default=0),
        'valign': DXFAttr(74, default=0),
    })
)


class Attrib(attrib.Attrib, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_ATTRIB_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *attrib_subclass)

