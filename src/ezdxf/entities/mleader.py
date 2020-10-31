# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Union, Optional
import copy
import logging

from ezdxf.lldxf import const
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags
from ezdxf.math import Vector
from ezdxf import colors
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic, acdb_entity

from .factory import register_entity
from .objectcollection import ObjectCollection

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace, DXFTag

__all__ = ['MultiLeader', 'MLeaderStyle', 'MLeaderStyleCollection']

logger = logging.getLogger('ezdxf')

# DXF Examples:
# "D:\source\dxftest\CADKitSamples\house design for two family with common staircasedwg.dxf"
# "D:\source\dxftest\CADKitSamples\house design.dxf"
# How to render MLEADER: https://atlight.github.io/formats/dxf-leader.html


acdb_mleader = DefSubclass('AcDbMLeader', {
    'version': DXFAttr(270, default=2),
    'style_handle': DXFAttr(340),

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

    'leader_type': DXFAttr(170, default=1),
    'leader_line_color': DXFAttr(91, default=colors.BY_BLOCK_RAW_VALUE),
    'leader_linetype_handle': DXFAttr(341),
    'leader_lineweight': DXFAttr(171, default=const.LINEWEIGHT_BYBLOCK),
    'has_landing': DXFAttr(290, default=1),
    'has_dogleg': DXFAttr(291, default=1),
    'dogleg_length': DXFAttr(41),  # depend on $MEASUREMENT?

    # no handle is default arrow 'closed filled':
    'arrow_head_handle': DXFAttr(342),
    'arrow_head_size': DXFAttr(42),  # depend on $MEASUREMENT?

    'content_type': DXFAttr(172, default=2),
    # 0 = None
    # 1 = Block content
    # 2 = MTEXT content
    # 3 = TOLERANCE content

    # Text Content:
    'text_style_handle': DXFAttr(343),
    'text_left_attachment_type': DXFAttr(173, default=1),
    # Values 0-8 are used for the left/right attachment
    # point (attachment direction is horizontal), values 9-10 are used for the
    # top/bottom attachment points (attachment direction is vertical).
    # Attachment point is:
    # 0 = top of top text line,
    # 1 = middle of top text line,
    # 2 = middle of text,
    # 3 = middle of bottom text line,
    # 4 = bottom of bottom text line,
    # 5 = bottom text line,
    # 6 = bottom of top text line. Underline bottom line
    # 7 = bottom of top text line. Underline top line,
    # 8 = bottom of top text line. Underline all content,
    # 9 = center of text (y-coordinate only),
    # 10 = center of text (y-coordinate only), and overline top/underline
    # bottom content.
    'text_right_attachment_type': DXFAttr(95),  # like 173

    'text_angle_type': DXFAttr(174, default=1),
    # 0 = text angle is equal to last leader line segment angle
    # 1 = text is horizontal
    # 2 = text angle is equal to last leader line segment angle, but potentially
    #     rotated by 180 degrees so the right side is up for readability.

    'text_alignment_type': DXFAttr(175, default=2),
    'text_color': DXFAttr(92, default=colors.BY_BLOCK_RAW_VALUE),
    'has_frame_text': DXFAttr(292, default=0),

    # Block Content:
    'block_record_handle': DXFAttr(344),
    'block_color': DXFAttr(93, default=colors.BY_BLOCK_RAW_VALUE),  # raw color
    'block_scale_vector': DXFAttr(10, xtype=XType.point3d,
                                  default=Vector(1, 1, 1)),
    'block_rotation': DXFAttr(43),  # in radians!!!
    'block_connection_type': DXFAttr(176),
    # 0 = center extents
    # 1 = insertion point

    'is_annotative': DXFAttr(293, default=0),
    # REPEAT "arrow_heads":
    'arrow_head2_index': DXFAttr(94, dxfversion=const.DXF2007),
    'arrow_head2_handle': DXFAttr(345, dxfversion=const.DXF2007),
    # END "arrow heads"

    #  Block Attribute (ATTDEF)
    # REPEAT "block labels":
    'attrib_handle': DXFAttr(330, dxfversion=const.DXF2007),
    # attrib_index:  UI index (sequential index of the label in the collection)
    'attrib_index': DXFAttr(177, dxfversion=const.DXF2007),
    'attrib_width': DXFAttr(44, dxfversion=const.DXF2007),
    'attrib_text': DXFAttr(302, dxfversion=const.DXF2007),
    # END "block labels"

    # Text Content:
    'is_text_direction_negative': DXFAttr(294, default=0,
                                          dxfversion=const.DXF2007),
    'text_IPE_align': DXFAttr(178, default=0, dxfversion=const.DXF2007),
    'text_attachment_point': DXFAttr(179, default=1, dxfversion=const.DXF2007),
    # 1 = left
    # 2 = center
    # 3 = right

    'scale': DXFAttr(45, default=1, dxfversion=const.DXF2007),
    # 0 = horizontal
    # 1 = vertical

    'text_attachment_direction': DXFAttr(
        271, default=0, dxfversion=const.DXF2010),
    # This defines whether the leaders attach to the left/right of the content
    # block/text, or attach to the top/bottom:
    # 0 = horizontal
    # 1 = vertical

    'text_bottom_attachment_direction': DXFAttr(
        272, default=9, dxfversion=const.DXF2010),
    # like 173, but
    # 9 = center
    # 10= underline and center

    'text_top_attachment_direction': DXFAttr(
        273, default=9, dxfversion=const.DXF2010),
    # like 173, but
    # 9 = center
    # 10= overline and center

    'leader_extend_to_text': DXFAttr(
        295, default=0, dxfversion=const.DXF2013),

})

CONTEXT_STR = 'CONTEXT_DATA{'
LEADER_STR = 'LEADER{'
LEADER_LINE_STR = 'LEADER_LINE{'
START_CONTEXT_DATA = 300
END_CONTEXT_DATA = 301
START_LEADER = 302
END_LEADER = 303
START_LEADER_LINE = 304
END_LEADER_LINE = 305


@register_entity
class MultiLeader(DXFGraphic):
    DXFTYPE = 'MULTILEADER'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mleader)
    MIN_DXF_VERSION_FOR_EXPORT = const.DXF2000

    def __init__(self):
        super().__init__()
        # preserve original data until load/export is implemented
        self._tags = Tags()
        self.context = MultiLeaderContext()

    def copy(self):
        raise const.DXFTypeError(f'Cloning of {self.DXFTYPE} not supported.')

    def _copy_data(self, entity: 'MultiLeader') -> None:
        """ Copy leaders """
        entity.context = copy.deepcopy(self.context)

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        # _tags is just a temporarily solution
        self._tags = processor.subclasses[2]

        context = self.extract_context_data(processor.subclasses[2])
        if context:
            try:
                self.context = self.load_context(context)
            except const.DXFStructureError:
                logger.info(
                    f'Context structure error in entity MULTILEADER(#{dxf.handle})')

        tags = processor.load_dxfattribs_into_namespace(
            dxf, acdb_mleader, index=2)
        if len(tags):
            processor.log_unprocessed_tags(tags, subclass=acdb_mleader.name)
        return dxf

    @staticmethod
    def extract_context_data(tags) -> List['DXFTag']:
        start, end = None, None
        context_data = []
        for index, tag in enumerate(tags):
            if tag.code == START_CONTEXT_DATA:
                start = index
            elif tag.code == END_CONTEXT_DATA:
                end = index + 1

        if start and end:
            context_data = tags[start:end]
            # Remove context data!
            del tags[start: end]
        return context_data

    @staticmethod
    def load_context(data: List['DXFTag']) -> 'MultiLeaderContext':
        def build_structure(tag: 'DXFTag',
                            stop: int) -> List[Union['DXFTag', List]]:
            collector = [tag]
            while tag.code != stop:
                if tag.code == START_LEADER:
                    collector.append(build_structure(tag, END_LEADER))
                elif tag.code == START_LEADER_LINE:
                    collector.append(build_structure(tag, END_LEADER_LINE))
                collector.append(tag)
                tag = next(tags)
            return collector

        tags = iter(data)
        try:
            context = build_structure(next(tags), END_CONTEXT_DATA)
        except StopIteration:
            raise const.DXFStructureError
        else:
            return MultiLeaderContext.load(context)

    def preprocess_export(self, tagwriter: 'TagWriter') -> bool:
        if self.context.is_valid:
            return True
        else:
            logger.debug(
                f'Ignore {str(self)} at DXF export, invalid context data.')
            return False

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tags(self._tags)


class MultiLeaderContext:
    def __init__(self):
        self.leaders: List['Leader'] = []
        pass

    @classmethod
    def load(cls, context: List[Union['DXFTag', List]]) -> 'MultiLeaderContext':
        assert context[0] == (START_CONTEXT_DATA, CONTEXT_STR)
        ctx = cls()
        for tag in context:
            if isinstance(tag, list):  # Leader()
                ctx.leaders.append(Leader.load(tag))
                continue
            # parse context tags
            code, value = tag
            if code == 0:
                pass
        return ctx

    @property
    def is_valid(self) -> bool:
        return True

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(START_CONTEXT_DATA, CONTEXT_STR)
        for leader in self.leaders:
            leader.export_dxf(tagwriter)
        tagwriter.write_tag2(END_CONTEXT_DATA, '}')


class Leader:
    def __init__(self):
        self.lines: List['LeaderLine'] = []

    @classmethod
    def load(cls, context: List[Union['DXFTag', List]]):
        assert context[0] == (START_LEADER, LEADER_STR)
        leader = cls()
        for tag in context:
            if isinstance(tag, list):  # LeaderLine()
                leader.lines.append(LeaderLine.load(tag))
                continue
            # parse leader tags
            code, value = tag
            if code == 0:
                pass

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(START_LEADER, LEADER_STR)
        for line in self.lines:
            line.export_dxf(tagwriter)
        tagwriter.write_tag2(END_LEADER, '}')


class LeaderLine:
    def __init__(self):
        self.vertices: List[Vector] = []
        self.breaks: Optional[List[Union[int, Vector]]] = None
        # Breaks: 90, 11, 12, [11, 12, ...] [, 90, 11, 12 [11, 12, ...]]
        # group code 90 = break index
        # group code 11 = start vertex of break
        # group code 12 = end vertex of break
        # multiple breaks per index possible
        self.index: int = 0  # group code 91
        self.color: int = colors.BY_BLOCK_RAW_VALUE  # group code 92

    @classmethod
    def load(cls, tags: List['DXFTag']):
        assert tags[0] == (START_LEADER_LINE, LEADER_LINE_STR)
        line = LeaderLine()
        vertices = line.vertices
        breaks = []
        for code, value in tags:
            if code == 10:
                vertices.append(value)
            elif code in (90, 11, 12):
                breaks.append(value)
            elif code == 91:
                line.index = value
            elif code == 92:
                line.color = value
        if breaks:
            line.breaks = breaks
        return line

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(START_LEADER_LINE, LEADER_LINE_STR)
        for vertex in self.vertices:
            tagwriter.write_vertex(10, vertex)
        if self.breaks:
            code = 0
            for value in self.breaks:
                if isinstance(value, int):
                    # break index
                    tagwriter.write_tag2(90, value)
                else:
                    # 11 .. start vertex of break
                    # 12 .. end vertex of break
                    tagwriter.write_vertex(11 + code, value)
                    code = 1 - code
        tagwriter.write_tag2(91, self.index)
        tagwriter.write_tag2(92, self.color)
        tagwriter.write_tag2(END_LEADER_LINE, '}')


@register_entity
class MLeader(MultiLeader):
    DXFTYPE = 'MLEADER'


acdb_mleader_style = DefSubclass('AcDbMLeaderStyle', {
    'unknown1': DXFAttr(179, default=2),
    'content_type': DXFAttr(170, default=2),
    'draw_mleader_order_type': DXFAttr(171, default=1),
    'draw_leader_order_type': DXFAttr(172, default=0),
    'max_leader_segments_points': DXFAttr(90, default=2),
    'first_segment_angle_constraint': DXFAttr(40, default=0.0),
    'second_segment_angle_constraint': DXFAttr(41, default=0.0),
    'leader_type': DXFAttr(173, default=1),
    'leader_line_color': DXFAttr(91, default=-1056964608),
    # raw color: BY_BLOCK
    'leader_linetype_handle': DXFAttr(340),
    'leader_lineweight': DXFAttr(92, default=-2),
    'has_landing': DXFAttr(290, default=1),
    'landing_gap': DXFAttr(42, default=2.0),
    'has_dogleg': DXFAttr(291, default=1),
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
    'has_frame_text': DXFAttr(292, default=0),
    'text_align_always_left': DXFAttr(297, default=0),
    'align_space': DXFAttr(46, default=4),
    'has_block_scaling': DXFAttr(293),
    'block_record_handle': DXFAttr(343),
    'block_color': DXFAttr(94, default=-1056964608),  # raw color: BY_BLOCK
    'block_scale_x': DXFAttr(47, default=1),
    'block_scale_y': DXFAttr(49, default=1),
    'block_scale_z': DXFAttr(140, default=1),
    'has_block_rotation': DXFAttr(294, default=1),
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
    MIN_DXF_VERSION_FOR_EXPORT = const.DXF2000

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
        tagwriter.write_tag2(const.SUBCLASS_MARKER, acdb_mleader_style.name)
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
