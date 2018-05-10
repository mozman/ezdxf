# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity

# example: D:\source\dxftest\CADKitSamples\AEC Plan Elev Sample.dxf

_LEADER_TPL = """0
LEADER
5
0
330
0
100
AcDbEntity
8
0
100
AcDbLeader
3
DIMSTYLE
73
3
40
1.0
41
1.0
76
3
10
0.0
20
0.0
30
0.0
340
0
210
0.0
220
0.0
230
1.0
213
0.0
223
0.0
233
0.0
"""

leader_subclass = DefSubclass('AcDbLeader', {
    'dimstyle': DXFAttr(3),  # Dimension style name
    'has_arrowhead': DXFAttr(71),  # Arrowhead flag: 0/1 = no/yes
    'path_type': DXFAttr(72),  # Leader path type: 0 = Straight line segments; 1 = Spline
    'annotation_type': DXFAttr(73, default=3),  # Leader creation flag:
    # 0= Created with text annotation
    # 1 = Created with tolerance annotation;
    # 2 = Created with block reference annotation
    # 3 = Created without any annotation
    'hookline_direction': DXFAttr(74),  # Hookline direction flag:
    # 0 = Hookline (or end of tangent for a splined leader) is the opposite direction from the horizontal vector
    # 1 = Hookline (or end of tangent for a splined leader) is the same direction as horizontal vector (see code 75)
    'has_hookline': DXFAttr(75),  # Hookline flag: 0/1 = no/yes
    'text_height': DXFAttr(40),  # Text annotation height
    'text_width': DXFAttr(41),  # Text annotation width
    'n_vertices': DXFAttr(76),  # Number of vertices in leader (ignored for OPEN)
    # 10, 20, 30 - Vertex coordinates (one entry for each vertex)
    'block_color': DXFAttr(76),  # Color to use if leader's DIMCLRD = BYBLOCK
    'annotation': DXFAttr(340),  # Hard reference to associated annotation (mtext, tolerance, or insert entity)
    'normal_vector': DXFAttr(210, xtype='Point3D'),  # Normal vector
    'horizontal_direction': DXFAttr(211, xtype='Point3D'),  # 'horizontal' direction for leader
    'leader_offset_block_ref': DXFAttr(212, xtype='Point3D'),  # Offset of last leader vertex from block reference insertion point
    'leader_offset_annotation_placement': DXFAttr(213, xtype='Point3D'),  # Offset of last leader vertex from annotation placement point
    # Xdata belonging to the application ID "ACAD" follows a leader entity if any dimension overrides have been applied
    # to this entity. See Dimension Style Overrides.
})


class Leader(ModernGraphicEntity):
    # Requires AC1015/R2000
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_LEADER_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, leader_subclass)

    @property
    def AcDbLeader(self):
        return self.tags.subclasses[2]

    def get_vertices(self):
        return (tag.value for tag in self.AcDbLeader if tag.code == 10)
