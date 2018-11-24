# Created: 24.11.2018
# Copyright (c) 2018, Manfred Moitzi
# License: MIT-License
from __future__ import unicode_literals
from .dxfobjects import DXFAttr, DefSubclass, DXFAttributes, ExtendedTags
from .dxfobjects import none_subclass, DXFObject

_VISUALSTYLE_CLS = """0
CLASS
1
VISUALSTYLE
2
AcDbVisualStyle
3
ObjectDBX Classes
90
4095
91
26
280
0
281
0
"""

_VISUALSTYLE_TPL = """  0
VISUALSTYLE
5
0
102
{ACAD_REACTORS
330
0
102
}
330
0
100
AcDbVisualStyle
2
2dWireframe
70
4
"""

visualstyle_subclass = DefSubclass('AcDbVisualStyle', {
    'description': DXFAttr(2),
    'style_type': DXFAttr(70),
    'face_lighting_model': DXFAttr(71),
    # 0 =Invisible
    # 1 = Visible
    # 2 = Phong
    # 3 = Gooch
    'face_lighting_quality': DXFAttr(72),
    # 0 = No lighting
    # 1 = Per face lighting
    # 2 = Per vertex lighting
    'face_color_mode': DXFAttr(73),
    # 0 = No color
    # 1 = Object color
    # 2 = Background color
    # 3 = Custom color
    # 4 = Mono color
    # 5 = Tinted
    # 6 = Desaturated
    'face_modifiers': DXFAttr(90),
    # 0 = No modifiers
    # 1 = Opacity
    # 2 = Specular
    'face_opacity_level': DXFAttr(40),
    'face_specular_level': DXFAttr(41),
    'color1': DXFAttr(62),
    'color2': DXFAttr(63),
    'face_face_style_mono_color': DXFAttr(421),
    'edge_style_model': DXFAttr(74),
    # 0 = No edges
    # 1 = Isolines
    # 2 = Facet edges
    'edge_style': DXFAttr(91),
    'edge_intersection_color': DXFAttr(64),
    'edge_obscured_color': DXFAttr(65),
    'edge_obscured_linetype': DXFAttr(75),
    'edge_intersection_linetype': DXFAttr(175),
    'edge_crease_angle': DXFAttr(42),
    'edge_modifiers': DXFAttr(92),
    'edge_color': DXFAttr(66),
    'edge_opacity_level': DXFAttr(43),
    'edge_width': DXFAttr(76),
    'edge_overhang': DXFAttr(77),
    'edge_jitter': DXFAttr(78),
    'edge_silhouette_color': DXFAttr(67),
    'edge_silhouette_width': DXFAttr(79),
    'edge_halo_gap': DXFAttr(170),
    'edge_isoline_count': DXFAttr(171),
    'edge_hide_precision': DXFAttr(290),  # flag
    'edge_style_apply': DXFAttr(174),  # flag
    'style_display_settings': DXFAttr(93),
    'brightness': DXFAttr(44),
    'shadow_type': DXFAttr(173),
})


class VisualStyle(DXFObject):
    # Requires AC1021/R2007
    __slots__ = ()
    TEMPLATE = ExtendedTags.from_text(_VISUALSTYLE_TPL)
    CLASS = ExtendedTags.from_text(_VISUALSTYLE_CLS)
    DXFATTRIBS = DXFAttributes(none_subclass, visualstyle_subclass)


