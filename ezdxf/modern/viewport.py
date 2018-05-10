# Created: 11.10.2015
# Copyright (C) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf.types import DXFTag
from ..lldxf.const import DXFAttributeError, DXFValueError

_VIEWPORT_TPL = """0
VIEWPORT
5
0
330
0
100
AcDbEntity
67
1
8
VIEWPORTS
100
AcDbViewport
10
0.0
20
0.0
30
0.0
40
1.0
41
1.0
68
2
69
2
12
0.0
22
0.0
13
0.0
23
0.0
14
0.1
24
0.1
15
0.1
25
0.1
16
0.0
26
0.0
36
0.0
17
0.0
27
0.0
37
0.0
42
50.0
43
0.0
44
0.0
45
1.0
50
0.0
51
0.0
72
100
90
32864
1

281
0
71
0
74
0
110
0.0
120
0.0
130
0.0
111
1.0
121
0.0
131
0.0
112
0.0
122
1.0
132
0.0
79
0
146
0.0
"""

# Every paper space layout contains as default VIEWPORT entity with the id=1.
# VIEWPORT id has to be unique to the paper space, it is placed not to the whole
# DXF drawing.

viewport_subclass = DefSubclass('AcDbViewport', {
    'center': DXFAttr(10, xtype='Point2D/3D'),
    'width': DXFAttr(40),
    'height': DXFAttr(41),
    'status': DXFAttr(68),
    'id': DXFAttr(69),
    'view_center_point': DXFAttr(12, xtype='Point2D'),
    'snap_base_point': DXFAttr(13, xtype='Point2D'),
    'snap_spacing': DXFAttr(14, xtype='Point2D'),
    'grid_spacing': DXFAttr(15, xtype='Point2D'),
    'view_direction_vector': DXFAttr(16, xtype='Point3D'),
    'view_target_point': DXFAttr(17, xtype='Point3D'),
    'perspective_lens_length': DXFAttr(42, default=50),
    'front_clip_plane_z_value': DXFAttr(43, default=0),
    'back_clip_plane_z_value': DXFAttr(44, default=0),
    'view_height': DXFAttr(45, default=1),
    'snap_angle': DXFAttr(50, default=0),
    'view_twist_angle': DXFAttr(51, default=0),
    'circle_zoom': DXFAttr(72, default=100),
    'flags': DXFAttr(90, default=0),
    # Viewport status bit-coded flags:
    # 1 (0x1) = Enables perspective mode
    # 2 (0x2) = Enables front clipping
    # 4 (0x4) = Enables back clipping
    # 8 (0x8) = Enables UCS follow
    # 16 (0x10) = Enables front clip not at eye
    # 32 (0x20) = Enables UCS icon visibility
    # 64 (0x40) = Enables UCS icon at origin
    # 128 (0x80) = Enables fast zoom
    # 256 (0x100) = Enables snap mode
    # 512 (0x200) = Enables grid mode
    # 1024 (0x400) = Enables isometric snap style
    # 2048 (0x800) = Enables hide plot mode
    # 4096 (0x1000) = kIsoPairTop. If set and kIsoPairRight is not set, then isopair top is enabled. If both kIsoPairTop
    #                 and kIsoPairRight are set, then isopair left is enabled
    # 8192 (0x2000) = kIsoPairRight. If set and kIsoPairTop is not set, then isopair right is enabled
    # 16384 (0x4000) = Enables viewport zoom locking
    # 32768 (0x8000) = Currently always enabled
    # 65536 (0x10000) = Enables non-rectangular clipping
    # 131072 (0x20000) = Turns the viewport off
    # 262144 (0x40000) = Enables the display of the grid beyond the drawing limits
    # 524288 (0x80000) = Enable adaptive grid display
    # 1048576 (0x100000) = Enables subdivision of the grid below the set grid spacing when the grid display is adaptive
    # 2097152 (0x200000) = Enables grid follows workplane switching
    'clipping_boundary_handle': DXFAttr(340, default=0),
    'plot_style_name': DXFAttr(1),
    'render_mode': DXFAttr(281, default=0),
    'ucs_per_viewport': DXFAttr(71, default=0),
    'ucs_icon': DXFAttr(74, default=0),
    'ucs_origin': DXFAttr(110, xtype='Point3D'),
    'ucs_x_axis': DXFAttr(111, xtype='Point3D'),
    'ucs_y_axis': DXFAttr(112, xtype='Point3D'),
    'ucs_handle': DXFAttr(345),  # ID/handle of AcDbUCSTableRecord if UCS is a named UCS. If not present, then UCS is unnamed
    'ucs_base_handle': DXFAttr(346),  # ID/handle of AcDbUCSTableRecord of base UCS if UCS is orthographic (79 code is non-zero). If not present and 79 code is non-zero, then base UCS is taken to be WORLD
    'ucs_ortho_type': DXFAttr(79),  # 0 = not orthographic; 1= Top; 2= Bottom; 3= Front; 4= Back; 5= Left; 6= Right
    'elevation': DXFAttr(146),
    'shade_plot_mode': DXFAttr(170, dxfversion='AC1018'),  # 0= As Displayed; 1= Wireframe; 2= Hidden; 3= Rendered
    'grid_frequency': DXFAttr(61, dxfversion='AC1021'),  # Frequency of major grid lines compared to minor grid lines
    'background_handle': DXFAttr(332, dxfversion='AC1021'),
    'shade_plot_handle': DXFAttr(333, dxfversion='AC1021'),
    'visual_style_handle': DXFAttr(348, dxfversion='AC1021'),
    'default_lighting_flag': DXFAttr(292, dxfversion='AC1021'),
    'default_lighting_type': DXFAttr(282, dxfversion='AC1021'),
    'view_brightness': DXFAttr(141, dxfversion='AC1021'),
    'view_contrast': DXFAttr(142, dxfversion='AC1021'),
    'ambient_light_color_1': DXFAttr(63, dxfversion='AC1021'),  # as AutoCAD Color Index
    'ambient_light_color_2': DXFAttr(421, dxfversion='AC1021'),  # as True Color
    'ambient_light_color_3': DXFAttr(431, dxfversion='AC1021'),  # as True Color
    'sun_handle': DXFAttr(361, dxfversion='AC1021'),
    'ref_vp_object_1': DXFAttr(335, dxfversion='AC1021'),  # unknown meaning, don't ask mozman
    'ref_vp_object_2': DXFAttr(343, dxfversion='AC1021'),  # unknown meaning, don't ask mozman
    'ref_vp_object_3': DXFAttr(344, dxfversion='AC1021'),  # unknown meaning, don't ask mozman
    'ref_vp_object_4': DXFAttr(91, dxfversion='AC1021'),  # unknown meaning, don't ask mozman
})


class Viewport(ModernGraphicEntity):
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VIEWPORT_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, viewport_subclass)
    viewport_id = 2  # notes to id:
    # The id of the first viewport has to be 1, which is the definition of
    # paper space. For the following viewports it seems only important, that
    # the id is greater than 1.

    @property
    def AcDbViewport(self):
        return self.tags.sublasses[2]

    def get_next_viewport_id(self):
        current_id = Viewport.viewport_id
        Viewport.viewport_id += 1
        return current_id

    def get_frozen_layer_handles(self):
        return (tag.value for tag in self.AcDbViewport if tag.code == 331)

    def get_frozen_layer_entities(self):
        if self.drawing is None:
            raise DXFAttributeError("'drawing' attribute is None, can not build DXF entities.")
        wrapper = self.dxffactory.wrap_handle
        return (wrapper(handle) for handle in self.get_frozen_layer_handles())

    def set_frozen_layers(self, layer_handles):
        self.AcDbViewport.remove_tags([331])  # remove existing frozen layer tags
        frozen_layer_tags = [DXFTag(331, handle) for handle in layer_handles]
        try:  # insert frozen layer tags in front of the flags-tag
            # try to create order like in the DXF standard, because order is sometimes important
            insert_pos = self.AcDbViewport.tag_index(90)
            self.AcDbViewport[insert_pos:insert_pos] = frozen_layer_tags
        except DXFValueError:  # flags-tag not found, just append frozen layer tags
            self.AcDbViewport.extend(frozen_layer_tags)

