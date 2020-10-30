# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXFTypeError
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags
from ezdxf.math import Vector
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic, acdb_entity

from .factory import register_entity
from .objectcollection import ObjectCollection

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace

__all__ = ['MLeader', 'MLeaderStyle', 'MLeaderStyleCollection']

# DXF Examples:
# "D:\source\dxftest\CADKitSamples\house design for two family with common staircasedwg.dxf"
# "D:\source\dxftest\CADKitSamples\house design.dxf"
# How to render MLEADER: https://atlight.github.io/formats/dxf-leader.html


acdb_mleader = DefSubclass('AcDbMLeader', {
    'style_handle': DXFAttr(340, default='0'),

    # Theory: Take properties for MLEADERSTYLE, except explicit overridden here:
    'property_override_flags': DXFAttr(90),
    # Bit coded flags:
    # 1 << 0 = leader_type
    # 1 << 1 = leader_line_color
    # 1 << 2 = leader_linetype_handle
    # 1 << 3 = leader_lineweight
    # 1 << 4 = landing_flag
    # 1 << 5 = landing_gap ???
    # 1 << 6 = dogleg_flag
    # 1 << 7 = dogleg_length
    # 1 << 8 = arrow_head_handle
    # 1 << 9 = arrow_head_size
    # 1 << 10 = content_type
    # 1 << 11 = text_style_handle
    # 1 << 12 = text_left_attachment_type (of MTEXT)
    # 1 << 13 = text_angle_type (of MTEXT)
    # 1 << 14 = text_alignment_type (of MTEXT)
    # 1 << 15 = text_color (of MTEXT)
    # 1 << 16 = ??? Text height (of MTEXT) ???
    # 1 << 17 = text_frame_flag
    # 1 << 18 = ??? Enable use of default MTEXT (from MLEADERSTYLE)
    # 1 << 19 = block_record_handle
    # 1 << 20 = block_color
    # 1 << 21 = block_scale_vector
    # 1 << 22 = block_rotation
    # 1 << 23 = block_connection_type
    # 1 << 24 = ??? Scale ???
    # 1 << 25 = text_right_attachment_type (of MTEXT)
    # 1 << 26 = ??? Text switch alignment type (of MTEXT) ???
    # 1 << 27 = text_attachment_direction (of MTEXT)
    # 1 << 28 = text_top_attachment_type (of MTEXT)
    # 1 << 29 = Text_bottom_attachment_type (of MTEXT)

    'leader_type': DXFAttr(170),
    'leader_line_color': DXFAttr(91),
    'leader_linetype_handle': DXFAttr(341),
    'leader_lineweight': DXFAttr(171),

    # Landing Flag: 0=disable; 1=enable
    'landing_flag': DXFAttr(290),

    # Dogleg Flag: 0=disable; 1=enable
    'dogleg_flag': DXFAttr(291),

    'dogleg_length': DXFAttr(41),

    # no handle is default arrow 'closed filled':
    'arrow_head_handle': DXFAttr(342),
    'arrow_head_size': DXFAttr(42),

    'content_type': DXFAttr(172),

    # Text Content:
    'text_style_handle': DXFAttr(343),
    'text_left_attachment_type': DXFAttr(173),
    'text_right_attachment_type': DXFAttr(95),
    'text_angle_type': DXFAttr(174),
    'text_alignment_type': DXFAttr(175),
    'text_color': DXFAttr(92),

    # Frame Text Flag: 0=disable; 1=enable
    'frame_text_flag': DXFAttr(292),

    # Block Content:
    'block_record_handle': DXFAttr(344),
    'block_color': DXFAttr(93),
    'block_scale_vector': DXFAttr(10, xtype=XType.point3d,
                                  default=Vector(1, 1, 1)),
    'block_rotation': DXFAttr(43),
    'block_connection_type': DXFAttr(176),

    # Annotation Scale Flag: 0=disable; 1=enable
    'annotation_scale_flag': DXFAttr(293),
    'arrow_head2_index': DXFAttr(94),
    'arrow_head2_handle': DXFAttr(345),

    # Block Attribute (ATTDEF)
    'attrib_handle': DXFAttr(340),
    'attrib_index': DXFAttr(177),
    'attrib_width': DXFAttr(44),
    'attrib_text': DXFAttr(302),

    # Text Content:
    'negative_text_direction_flag': DXFAttr(294),
    'text_align_in_IPE': DXFAttr(178),
    'text_attachment_point': DXFAttr(179),

    # 0=horizontal; 1=vertical
    'text_attachment_direction': DXFAttr(271),
    # 9=center; 10=underline and center
    'text_bottom_attachment_direction': DXFAttr(272),
    # 9=center; 10=overline and center
    'text_top_attachment_direction': DXFAttr(273),

})


@register_entity
class MLeader(DXFGraphic):
    DXFTYPE = 'MLEADER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mleader)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self):
        super().__init__()
        # preserve original data until load/export is implemented
        self._tags = Tags()

    def copy(self):
        raise DXFTypeError(f'Cloning of {self.DXFTYPE} not supported.')

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        self._tags = processor.subclasses[2]
        tags = processor.load_dxfattribs_into_namespace(
            dxf, acdb_mleader, index=2)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tags(self._tags)


@register_entity
class MultiLeader(MLeader):
    DXFTYPE = 'MULTILEADER'


acdb_mleader_style = DefSubclass('AcDbMLeaderStyle', {
    'unknown1': DXFAttr(179, default=2),
    'content_type': DXFAttr(170, default=2),
    'draw_mleader_order_type': DXFAttr(171, default=1),
    'draw_leader_order_type': DXFAttr(172, default=0),
    'max_leader_segments_points': DXFAttr(90, default=2),
    'first_segment_angle_constraint': DXFAttr(40, default=0.0),
    'second_segment_angle_constraint': DXFAttr(41, default=0.0),
    'leader_type': DXFAttr(173, default=1),
    'leader_line_color': DXFAttr(91, default=-1056964608),  # raw color: BY_BLOCK
    'leader_linetype_handle': DXFAttr(340),
    'leader_lineweight': DXFAttr(92, default=-2),
    'landing_flag': DXFAttr(290, default=1),
    'landing_gap': DXFAttr(42, default=2.0),
    # Dogleg Flag: 0=disable; 1=enable
    'dogleg_flag': DXFAttr(291, default=1),
    'dogleg_length': DXFAttr(43, default=8),
    'name': DXFAttr(3, default='Standard'),

    # no handle is default arrow 'closed filled':
    'arrow_head_handle': DXFAttr(341),
    'arrow_head_size': DXFAttr(44, default=4),
    'default_text_content': DXFAttr(300, default=''),
    'text_style_handle': DXFAttr(342),
    'text_left_attachment_type': DXFAttr(174, default=1),
    'text_angle_type': DXFAttr(175, default=1),
    'text_alignment_type': DXFAttr(176, default=0),
    'text_right_attachment_type': DXFAttr(178, default=1),
    'text_color': DXFAttr(93, default=-1056964608),  # raw color: BY_BLOCK
    'text_height': DXFAttr(45, default=4),

    # Frame Text Flag: 0=disable; 1=enable
    'frame_text_flag': DXFAttr(292, default=0),
    'text_align_always_left': DXFAttr(297, default=0),
    'align_space': DXFAttr(46, default=4),
    'block_scale_flag': DXFAttr(293),
    'block_record_handle': DXFAttr(343),
    'block_color': DXFAttr(94, default=-1056964608),  # raw color: BY_BLOCK
    'block_scale_x': DXFAttr(47, default=1),
    'block_scale_y': DXFAttr(49, default=1),
    'block_scale_z': DXFAttr(140, default=1),
    'block_rotation_flag': DXFAttr(294, default=1),
    'block_rotation': DXFAttr(141, default=0),
    'block_connection_type': DXFAttr(177, default=0),
    'scale': DXFAttr(142, default=1),
    'overwrite_property_value': DXFAttr(295, default=0),
    'is_annotative': DXFAttr(296, default=0),
    'break_gap_size': DXFAttr(143, default=3.75),

    # 0 = Horizontal; 1 = Vertical:
    'text_attachment_direction': DXFAttr(271, default=0),

    # 9 = Center; 10 = Underline and Center:
    'text_bottom__attachment_direction': DXFAttr(272, default=9),

    # 9 = Center; 10 = Overline and Center:
    'text_top_attachment_direction': DXFAttr(273, default=9),

    'unknown2': DXFAttr(298, optional=True),  # boolean flag ?
})


@register_entity
class MLeaderStyle(DXFObject):
    DXFTYPE = 'MLEADERSTYLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_mleader_style)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(
                dxf, acdb_mleader_style)
            if len(tags):
                processor.log_unprocessed_tags(
                    tags, subclass=acdb_mleader_style.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_mleader_style.name)
        self.dxf.export_dxf_attribs(
            tagwriter, acdb_mleader_style.attribs.keys())


class MLeaderStyleCollection(ObjectCollection):
    def __init__(self, doc: 'Drawing'):
        super().__init__(
            doc, dict_name='ACAD_MLEADERSTYLE', object_type='MLEADERSTYLE')
        self.create_required_entries()

    def create_required_entries(self) -> None:
        for name in ('Standard',):
            if name not in self.object_dict:
                mleader_style = self.new(name)
                # set standard text style
                text_style = self.doc.styles.get('Standard')
                mleader_style.dxf.text_style_handle = text_style.dxf.handle
