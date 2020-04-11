# Created: 08.04.2018
# Copyright (c) 2018-2019, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING
from collections import OrderedDict
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2004, DXFTypeError
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ezdxf.lldxf.tags import Tags
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic, acdb_entity

from .factory import register_entity
from .objectcollection import ObjectCollection

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace

__all__ = ['MLeader', 'MLeaderStyle', 'MLeaderStyleCollection']

# DXF Examples:
# D:\source\dxftest\CADKitSamples\house design for two family with common staircasedwg.dxf
# D:\source\dxftest\CADKitSamples\house design.dxf

acdb_mleader = DefSubclass('AcDbMLeader', {
    'leader_style_handle': DXFAttr(340, default='0'),  # handle of MLEADERSTYLE?
})


@register_entity
class MLeader(DXFGraphic):
    DXFTYPE = 'MLEADER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mleader)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2004

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        # todo: MLEADER implementation
        self.tags = Tags()

    def copy(self):
        raise DXFTypeError('Cloning of {} not supported.'.format(self.DXFTYPE))

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        processor.load_dxfattribs_into_namespace(dxf, acdb_mleader)
        self.tags = processor.subclasses[2]
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tags(self.tags)


@register_entity
class MultiLeader(MLeader):
    DXFTYPE = 'MULTILEADER'


acdb_mleader_style = DefSubclass('AcDbMLeaderStyle', {
    'unknown1': DXFAttr(179, default=2),
    'content_type': DXFAttr(170, default=2),
    'draw_mleader_order_type': DXFAttr(171, default=1),
    'draw_leader_order_type': DXFAttr(172, default=0),
    'max_leader_segments_points': DXFAttr(90, default=2),  # MaxLeader Segments Points
    'first_segment_angle_constraint': DXFAttr(40, default=0.0),  # First Segment Angle Constraint
    'second_segment_angle_constraint': DXFAttr(41, default=0.0),  # Second Segment Angle Constraint
    'leader_line_type': DXFAttr(173, default=1),
    'leader_line_color': DXFAttr(91, default=-1056964608),
    'leader_line_type_handle': DXFAttr(340),  # handle
    'leader_line_weight': DXFAttr(92, default=-2),
    'enable_landing': DXFAttr(290, default=1),
    'landing_gap': DXFAttr(42, default=2.0),
    'enable_dog_leg': DXFAttr(291, default=1),
    'dog_leg_length': DXFAttr(43, default=8),
    'name': DXFAttr(3, default='Standard'),
    'arrow_head_handle': DXFAttr(341),  # no handle is default arrow 'closed filled'
    'arrow_head_size': DXFAttr(44, default=4),
    'default_mtext_contents': DXFAttr(300, default=''),
    'text_style_handle': DXFAttr(342),  # handle to text style 'Standard'
    'text_left_attachment_type': DXFAttr(174, default=1),
    'text_angle_type': DXFAttr(175, default=1),
    'text_alignment_type': DXFAttr(176, default=0),
    'text_right_attachment_type': DXFAttr(178, default=1),
    'text_color': DXFAttr(93, default=-1056964608),
    'text_height': DXFAttr(45, default=4),
    'enable_frame_text': DXFAttr(292, default=0),
    'text_align_always_left': DXFAttr(297, default=0),
    'align_space': DXFAttr(46, default=4),
    'enable_block_content_scale': DXFAttr(293),
    'block_content_handle': DXFAttr(343),
    'block_content_color': DXFAttr(94, default=-1056964608),
    'block_content_scale_x': DXFAttr(47, default=1),
    'block_content_scale_y': DXFAttr(49, default=0),
    'block_content_scale_z': DXFAttr(140, default=1),
    'enable_block_content_rotation': DXFAttr(294, default=1),
    'block_content_rotation': DXFAttr(141, default=0),
    'block_content_connection_type': DXFAttr(177, default=0),
    'scale': DXFAttr(142, default=1),
    'overwrite_property_value': DXFAttr(295, default=0),
    'is_annotative': DXFAttr(296, default=0),
    'break_gap_size': DXFAttr(143, default=3.75),
    'mtext_attachment_direction': DXFAttr(271, default=0),  # 0 = Horizontal; 1 = Vertical
    'bottom_text_attachment_direction': DXFAttr(272, default=9),  # 9 = Center; 10 = Underline and Center
    'top_text_attachment_direction': DXFAttr(272, default=9),  # 9 = Center; 10 = Overline and Center
    'unknown2': DXFAttr(273, optional=True),  # also an attachment direction ?
    'unknown3': DXFAttr(298, optional=True),  # boolean flag ?
})


@register_entity
class MLeaderStyle(DXFObject):
    DXFTYPE = 'MLEADERSTYLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_mleader_style)
    MIN_DXF_VERSION_FOR_EXPORT = DXF2004

    def copy(self):
        raise DXFTypeError('Copying of {} not supported.'.format(self.DXFTYPE))

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_mleader_style)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_mleader_style.name)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_mleader_style.name)
        self.dxf.export_dxf_attribs(tagwriter, acdb_mleader_style.attribs.keys())


class MLeaderStyleCollection(ObjectCollection):
    def __init__(self, doc: 'Drawing'):
        super().__init__(doc, dict_name='ACAD_MLEADERSTYLE', object_type='MLEADERSTYLE')
        self.create_required_entries()

    def create_required_entries(self) -> None:
        for name in ('Standard',):
            if name not in self.object_dict:
                mleader_style = self.new(name)
                # set standard text style
                text_style = self.doc.styles.get('Standard')
                mleader_style.dxf.text_style_handle = text_style.dxf.handle
