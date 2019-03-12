# Copyright (c) 2019, Manfred Moitzi
# License: MIT-License
# Created: 2019-03-12
from typing import TYPE_CHECKING
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2007
from ezdxf.lldxf.attributes import DXFAttributes, DefSubclass, DXFAttr
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace

__all__ = ['VisualStyle']

acdb_visualstyle = DefSubclass('AcDbVisualStyle', {
    'description': DXFAttr(2),
    'style_type': DXFAttr(70),
    # 0 = Flat
    # 1 = FlatWithEdges
    # 2 = Gouraud
    # 3 = GouraudWithEdges
    # 4 = 2dWireframe
    # 5 = Wireframe
    # 6 = Hidden
    # 7 = Basic
    # 8 = Realistic
    # 9 = Conceptual
    # 10 = Modeling
    # 11 =Dim
    # 12 = Brighten
    # 13 = Thicken
    # 14 = Linepattern
    # 15 = Facepattern
    # 16 = ColorChange
    # 20 = JitterOff
    # 21 = OverhangOff
    # 22 = EdgeColorOff
    # 23 = Shades of Gray
    # 24 = Sketchy
    # 25 = X-Ray
    # 26 = Shaded with edges
    # 27 = Shaded
    'face_lighting_model': DXFAttr(71),
    # 0 = Invisible
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
    'face_style_mono_color': DXFAttr(421),
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
    'internal_flag': DXFAttr(291),
})


@register_entity
class VisualStyle(DXFObject):
    """ DXF VISUALSTYLE entity """
    DXFTYPE = 'VISUALSTYLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_visualstyle)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2007

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.load_dxfattribs_into_namespace(dxf, acdb_visualstyle)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_visualstyle.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'description', 'style_type', 'face_lighting_model', 'face_lighting_quality', 'face_color_mode',
            'face_modifiers', 'face_opacity_level', 'face_specular_level', 'color1', 'color2', 'face_style_mono_color',
            'edge_style_model', 'edge_style', 'edge_intersection_color', 'edge_obscured_color',
            'edge_obscured_linetype', 'edge_intersection_linetype', 'edge_crease_angle', 'edge_modifiers',
            'edge_color', 'edge_opacity_level', 'edge_width', 'edge_overhang', 'edge_jitter', 'edge_silhouette_color',
            'edge_silhouette_width', 'edge_halo_gap', 'edge_isoline_count', 'edge_hide_precision', 'edge_style_apply',
            'style_display_settings', 'brightness', 'shadow_type', 'internal_flag'
        ])
