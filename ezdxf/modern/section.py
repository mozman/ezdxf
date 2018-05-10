# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


_SECTION_TPL = """0
SECTION
5
0
330
0
100
AcDbEntity
8
0
100
AcDbSection
90
1
91
0
1
NAME
10
0.0
11
0.0
12
1.0
40
1.0
41
0.0
"""

section_subclass = DefSubclass('AcDbSection', {
    'state': DXFAttr(90),
    'flags': DXFAttr(91),
    'name': DXFAttr(1),
    'vertical_direction': DXFAttr(10, xtype='Point3D'),
    'top_height': DXFAttr(40),
    'bottom_height': DXFAttr(41),
    'indicator_transparency': DXFAttr(70),
    'indicator_color': DXFAttr(63),
    'indicator_true_color': DXFAttr(411),
    'n_vertices': DXFAttr(92),  # Number of vertices
    # 11: Vertex (repeats for number of vertices)
    'n_back_line_vertices': DXFAttr(93),  # Number of back line vertices
    # 12: Back line vertex (repeats for number of back line vertices)
    'geometry_settings_id': DXFAttr(360),  # Hard-pointer ID/handle to geometry settings object

})


class Section(ModernGraphicEntity):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_SECTION_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, section_subclass)

    @property
    def AcDbSection(self):
        return self.tags.subclasses[2]

    def get_vertices(self):
        return [vertex.value for vertex in self.AcDbSection.find_all(11)]

    def get_back_line_vertices(self):
        return [vertex.value for vertex in self.AcDbSection.find_all(12)]

