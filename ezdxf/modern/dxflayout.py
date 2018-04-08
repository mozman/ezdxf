# Created: 22.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import DXFObject, none_subclass, ExtendedTags, DXFAttr, DXFAttributes, DefSubclass

plot_settings_subclass = DefSubclass('AcDbPlotSettings', {
    'page_setup_name': DXFAttr(1),
    'plot_configuration_file': DXFAttr(2),
    'paper_size': DXFAttr(4),
    'plot_view_name': DXFAttr(6),
    'left_margin': DXFAttr(40),  # in mm
    'bottom_margin': DXFAttr(41),  # in mm
    'right_margin': DXFAttr(42),  # in mm
    'top_margin': DXFAttr(43),  # in mm
    'paper_width': DXFAttr(44),  # in mm
    'paper_height': DXFAttr(45),  # in mm
    'plot_origin_x_offset': DXFAttr(46, default=0.),  # in mm
    'plot_origin_y_offset': DXFAttr(47, default=0.),  # in mm
    'plot_window_x1': DXFAttr(48, default=0.),
    'plot_window_y1': DXFAttr(49, default=0.),
    'plot_window_x2': DXFAttr(140, default=0.),
    'plot_window_y2': DXFAttr(141, default=0.),
    'scale_numerator': DXFAttr(142, default=1.),  # Numerator of custom print scale: real world (paper) units
    'scale_denominator': DXFAttr(143, default=1.),  # Denominator of custom print scale: drawing units
    'plot_layout_flags': DXFAttr(70),
    # 1 = Plot Viewport Borders
    # 2 = Show Plot Styles
    # 4 = Plot Centered
    # 8 = Plot Hidden
    # 16 = Use Standard Scale
    # 32 = Plot Plot Styles
    # 64 = Scale Lineweights
    # 128 = Print Lineweights
    # 512 = Draw Viewports First
    # 1024 = Model Type
    # 2048 = Update Paper
    # 4096 = Zoom To Paper On Update
    # 8192 = Initializing
    # 16384 = Prev PlotInit
    'plot_paper_units': DXFAttr(72),  # 0 = Plot in inches; 1 = Plot in millimeters; 2 = Plot in pixels
    'plot_rotation': DXFAttr(73),
    # 0 = No rotation
    # 1 = 90 degrees counterclockwise
    # 2 = Upside-down
    # 3 = 90 degrees clockwise
    'plot_type': DXFAttr(74),
    # 0 = Last screen display
    # 1 = Drawing extents
    # 2 = Drawing limits
    # 3 = View specified by code 6
    # 4 = Window specified by codes 48, 49, 140, and 141
    # 5 = Layout information
    'current_style_sheet': DXFAttr(7),
    'standard_scale_type': DXFAttr(75),
    # 0 = Scaled to Fit
    # 1 = 1/128"=1'
    # 2 = 1/64"=1'
    # 3 = 1/32"=1'
    # 4 = 1/16"=1'
    # 5 = 3/32"=1'
    # 6 = 1/8"=1'
    # 7 = 3/16"=1'
    # 8 = 1/4"=1'
    # 9 = 3/8"=1'
    # 10 = 1/2"=1'
    # 11 = 3/4"=1'
    # 12 = 1"=1'
    # 13 = 3"=1'
    # 14 = 6"=1'
    # 15 = 1'=1'
    # 16 = 1:1
    # 17 = 1:2
    # 18 = 1:4
    # 19 = 1:8
    # 20 = 1:10
    # 21 = 1:16
    # 22 = 1:20
    # 23 = 1:30
    # 24 = 1:40
    # 25 = 1:50
    # 26 = 1:100
    # 27 = 2:1
    # 28 = 4:1
    # 29 = 8:1
    # 30 = 10:1
    # 31 = 100:1
    # 32 = 1000:1
    'shade_plot_mode': DXFAttr(76),  # 0 = As Displayed; 1 = Wireframe; 2 = Hidden; 3 = Rendered
    'shade_plot_resolution_level': DXFAttr(77),
    # 0 = Draft
    # 1 = Preview
    # 2 = Normal
    # 3 = Presentation
    # 4 = Maximum
    # 5 = Custom
    'shade_plot_custom_dpi': DXFAttr(78),
    # Valid range: 100 to 32767, Only applied when the shade_plot_resolution level is set to 5 (Custom)
    'unit_factor': DXFAttr(147),
    # 147: factor for unit conversion (mm -> inches)
    # 147: DXF Reference error 'A floating point scale factor that represents the standard scale value specified in code 75'
    'paper_image_origin_x': DXFAttr(148),
    'paper_image_origin_y': DXFAttr(149),
    'shade_plot_handle': DXFAttr(333),
})


class DXFPlotSettings(DXFObject):
    DXFATTRIBS = DXFAttributes(none_subclass, plot_settings_subclass)


# removed reactors 5 .. 102 330 102 .. 330
_LAYOUT_TPL = """0
LAYOUT
5
0
330
1A
100
AcDbPlotSettings
1

2
Adobe PDF
4
A4
6

40
3.175
41
3.175
42
3.175
43
3.175
44
209.91
45
297.03
46
0.0
47
0.0
48
0.0
49
0.0
140
0.0
141
0.0
142
1.0
143
1.0
70
688
72
0
73
1
74
5
7

75
16
147
1.0
76
0
77
2
78
300
148
0.0
149
0.0
100
AcDbLayout
1
Layoutname
70
1
71
1
10
-3.175
20
-3.175
11
293.857
21
206.735
12
0.0
22
0.0
32
0.0
14
29.068
24
20.356
34
0.0
15
261.614
25
183.204
35
0.0
146
0.0
13
0.0
23
0.0
33
0.0
16
1.0
26
0.0
36
0.0
17
0.0
27
1.0
37
0.0
76
1
330
0
"""


class DXFLayout(DXFObject):
    TEMPLATE = ExtendedTags.from_text(_LAYOUT_TPL)
    DXFATTRIBS = DXFAttributes(
        none_subclass,
        plot_settings_subclass,
        DefSubclass('AcDbLayout', {
            'name': DXFAttr(1),  # layout name
            'layout_flags': DXFAttr(70),
            'taborder': DXFAttr(71),
            'limmin': DXFAttr(10, 'Point2D'),  # minimum limits
            'limmax': DXFAttr(11, 'Point2D'),  # maximum limits
            'insert_base': DXFAttr(12, 'Point3D'),  # Insertion base point for this layout
            'extmin': DXFAttr(14, 'Point3D'),  # Minimum extents for this layout
            'extmax': DXFAttr(15, 'Point3D'),  # Maximum extents for this layout
            'elevation': DXFAttr(146, default=0.),
            'ucs_origin': DXFAttr(13, 'Point3D'),
            'ucs_xaxis': DXFAttr(16, 'Point3D'),
            'ucs_yaxis': DXFAttr(17, 'Point3D'),
            'ucs_type': DXFAttr(76),
            # Orthographic type of UCS 0 = UCS is not orthographic;
            # 1 = Top; 2 = Bottom; 3 = Front; 4 = Back; 5 = Left; 6 = Right
            'block_record': DXFAttr(330),
            'viewport': DXFAttr(331),
            # ID/handle to the viewport that was last active in this
            # layout when the layout was current
            'ucs': DXFAttr(345),
            # ID/handle of AcDbUCSTableRecord if UCS is a named
            # UCS. If not present, then UCS is unnamed
            'base_ucs': DXFAttr(346),
            # ID/handle of AcDbUCSTableRecord of base UCS if UCS is
            # orthographic (76 code is non-zero). If not present and
            # 76 code is non-zero, then base UCS is taken to be WORLD
        }))
