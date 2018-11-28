# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from ezdxf.legacy import text

from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntityExtension


_TEXT_TPL = """0
TEXT
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
TEXTCONTENT
50
0.0
51
0.0
7
STANDARD
41
1.0
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
AcDbText
73
0
"""
text_subclass = (
    DefSubclass('AcDbText', {
        'insert': DXFAttr(10, xtype='Point2D/3D'),
        'height': DXFAttr(40),
        'text': DXFAttr(1),
        'rotation': DXFAttr(50, default=0.0),  # in degrees (circle = 360deg)
        'oblique': DXFAttr(51, default=0.0),  # in degrees, vertical = 0deg
        'style': DXFAttr(7, default='STANDARD'),  # text style
        'width': DXFAttr(41, default=1.0),  # width FACTOR!
        'text_generation_flag': DXFAttr(71, default=0),  # 2 = backward (mirror-x), 4 = upside down (mirror-y)
        'halign': DXFAttr(72, default=0),  # horizontal justification
        'align_point': DXFAttr(11, xtype='Point2D/3D'),
        'thickness': DXFAttr(39, default=0.0),
        'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    }),
    DefSubclass('AcDbText', {'valign': DXFAttr(73, default=0)}))


class Text(text.Text, ModernGraphicEntityExtension):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_TEXT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, *text_subclass)
