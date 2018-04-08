# Created: 08.04.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from .dxfobjects import DXFObject
from .object_manager import ObjectManager

# DXF Examples:
# D:\source\dxftest\CADKitSamples\house design for two family with comman staircasedwg.dxf
# D:\source\dxftest\CADKitSamples\house design.dxf

_MLEADER_CLS = """0
CLASS
1
MLEADER
2
AcDbMLeader
3
ACDB_MLEADER_CLASS
90
1025
91
0
280
0
281
1
"""

_MLEADER_TPL = """0
MLEADER
5
0
330
0
100
AcDbEntity
8
0
100
AcDbMLeader
340
0
"""

mleader_subclass = DefSubclass('AcDbMLeader', {
    'leader_style_id': DXFAttr(340),  # handle of MLEADERSTYLE?
})


class MLeader(ModernGraphicEntity):
    # Requires AC1021/R2007
    TEMPLATE = ExtendedTags.from_text(_MLEADER_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, mleader_subclass)
    CLASS = ExtendedTags.from_text(_MLEADER_CLS)


_MLEADER_STYLE_CLS = """0
CLASS
1
MLEADERSTYLE
2
AcDbMLeaderStyle
3
ACDB_MLEADERSTYLE_CLASS
90
4095
91
0
280
0
281
0
"""

_MLEADER_STYLE_TPL = """  0
MLEADERSTYLE
5
0
102
{ACAD_REACTORS
102
}
330
0
100
AcDbMLeaderStyle
179
2
170
2
171
1
172
0
90
2
40
0.0
41
0.0
173
1
91
-1056964608
340
14
92
-2
290
1
42
2.0
291
1
43
8.0
3
Standard
341
0
44
4.0
300

342
11
174
1
178
1
175
1
176
0
93
-1056964608
45
4.0
292
0
297
0
46
4.0
343
0
94
-1056964608
47
1.0
49
1.0
140
1.0
293
1
141
0.0
294
1
177
0
142
1.0
295
0
296
0
143
3.75
271
0
272
9
273
9
"""

mleader_style_subclass = DefSubclass('AcDbMLeaderStyle', {
    'content_type': DXFAttr(170),
    'draw_mleader_order_type': DXFAttr(171),
    'draw_leader_order_type': DXFAttr(172),
    'max_leader_segments_points': DXFAttr(90),  # MaxLeader Segments Points
    'first_segment_angle_constraint': DXFAttr(40),  # First Segment Angle Constraint
    'second_segment_angle_constraint': DXFAttr(41),  # Second Segment Angle Constraint
    'leader_line_type': DXFAttr(173),
    'leader_line_color': DXFAttr(91),
    'leader_line_type_id': DXFAttr(340),  # handle
    'leader_line_weight': DXFAttr(92),
    'enable_landing': DXFAttr(290),
    'landing_gap': DXFAttr(42),
    'enable_dog_leg': DXFAttr(291),
    'dog_leg_length': DXFAttr(43),
    'name': DXFAttr(3),
    'arrow_head_id': DXFAttr(341),
    'arrow_head_size': DXFAttr(44),
    'default_mtext_contents': DXFAttr(300),
    'mtext_style_id': DXFAttr(342),
    'text_left_attachment_type': DXFAttr(174),
    'text_angle_type': DXFAttr(175),
    'text_right_attachment_type': DXFAttr(178),
    'text_color': DXFAttr(93),
    'text_height': DXFAttr(45),
    'enable_frame_text': DXFAttr(292),
    'text_align_always_left': DXFAttr(297),
    'align_space': DXFAttr(46),
    'enable_block_content_scale': DXFAttr(293),
    'block_content_id': DXFAttr(343),
    'block_content_color': DXFAttr(94),
    'block_content_scale_x': DXFAttr(47),
    'block_content_scale_y': DXFAttr(49),
    'block_content_scale_z': DXFAttr(140),
    'enable_block_content_rotation': DXFAttr(294),
    'block_content_rotation': DXFAttr(141),
    'block_content_connection_type': DXFAttr(177),
    'scale': DXFAttr(142),
    'overwrite_property_value': DXFAttr(295),
    'is_annotative': DXFAttr(296),
    'break_gap_size': DXFAttr(143),
    'mtext_attachment_direction': DXFAttr(271),  # 0 = Horizontal; 1 = Vertical
    'bottom_text_attachment_direction': DXFAttr(272),  # 9 = Center; 10 = Underline and Center
    'top_text_attachment_direction': DXFAttr(272),  # 9 = Center; 10 = Overline and Center
})


class MLeaderStyle(DXFObject):
    # Requires AC1021/R2007
    TEMPLATE = ExtendedTags.from_text(_MLEADER_STYLE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, mleader_style_subclass)
    CLASS = ExtendedTags.from_text(_MLEADER_STYLE_CLS)


class MLeaderStyleManager(ObjectManager):
    def __init__(self, drawing):
        super(MLeaderStyleManager, self).__init__(drawing, dict_name='ACAD_MLEADERSTYLE', object_type='MLEADERSTYLE')
        self.create_required_entries()

    def create_required_entries(self):
        for name in ('Standard', ):
            if name not in self.object_dict:
                self.new(name)
