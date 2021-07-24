# Copyright (c) 2018-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Union, Optional, Iterable
import copy
import logging
from collections import namedtuple

from ezdxf.lldxf import const
from ezdxf.lldxf.attributes import (
    DXFAttr,
    DXFAttributes,
    DefSubclass,
    XType,
    group_code_mapping,
)
from ezdxf.lldxf.tags import Tags
from ezdxf.math import Vec3, NULLVEC, X_AXIS, Y_AXIS, Z_AXIS, Matrix44
from ezdxf import colors
from ezdxf.proxygraphic import ProxyGraphic

from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic, acdb_entity

from .factory import register_entity
from .objectcollection import ObjectCollection

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, Drawing, DXFNamespace, DXFTag

__all__ = ["MultiLeader", "MLeader", "MLeaderStyle", "MLeaderStyleCollection"]

logger = logging.getLogger("ezdxf")

# DXF Examples:
# "D:\source\dxftest\CADKitSamples\house design for two family with common staircasedwg.dxf"
# "D:\source\dxftest\CADKitSamples\house design.dxf"

# How to render MLEADER: https://atlight.github.io/formats/dxf-leader.html
# DXF reference:
# http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72D20B8C-0F5E-4993-BEB7-0FCF94F32BE0

acdb_mleader = DefSubclass(
    "AcDbMLeader",
    {
        "version": DXFAttr(270, default=2),
        "style_handle": DXFAttr(340),
        # Theory: Take properties from MLEADERSTYLE,
        # except explicit overridden here:
        "property_override_flags": DXFAttr(90),
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
        "leader_type": DXFAttr(170, default=1),
        "leader_line_color": DXFAttr(91, default=colors.BY_BLOCK_RAW_VALUE),
        "leader_linetype_handle": DXFAttr(341),
        "leader_lineweight": DXFAttr(171, default=const.LINEWEIGHT_BYBLOCK),
        "has_landing": DXFAttr(290, default=1),
        "has_dogleg": DXFAttr(291, default=1),
        "dogleg_length": DXFAttr(41, default=8),  # depend on $MEASUREMENT?
        # no handle is default arrow 'closed filled':
        "arrow_head_handle": DXFAttr(342),
        "arrow_head_size": DXFAttr(42, default=4),  # depend on $MEASUREMENT?
        "content_type": DXFAttr(172, default=2),
        # 0 = None
        # 1 = Block content
        # 2 = MTEXT content
        # 3 = TOLERANCE content
        # Text Content:
        "text_style_handle": DXFAttr(343),
        "text_left_attachment_type": DXFAttr(173, default=1),
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
        "text_right_attachment_type": DXFAttr(95),  # like 173
        "text_angle_type": DXFAttr(174, default=1),
        # 0 = text angle is equal to last leader line segment angle
        # 1 = text is horizontal
        # 2 = text angle is equal to last leader line segment angle, but potentially
        #     rotated by 180 degrees so the right side is up for readability.
        "text_alignment_type": DXFAttr(175, default=2),
        "text_color": DXFAttr(92, default=colors.BY_BLOCK_RAW_VALUE),
        "has_frame_text": DXFAttr(292, default=0),
        # Block Content:
        "block_record_handle": DXFAttr(344),
        "block_color": DXFAttr(
            93, default=colors.BY_BLOCK_RAW_VALUE
        ),  # raw color
        "block_scale_vector": DXFAttr(
            10, xtype=XType.point3d, default=Vec3(1, 1, 1)
        ),
        "block_rotation": DXFAttr(43, default=0),  # in radians!!!
        "block_connection_type": DXFAttr(176, default=0),
        # 0 = center extents
        # 1 = insertion point
        "is_annotative": DXFAttr(293, default=0),
        # REPEAT "arrow_heads": DXF R2007+
        # arrow_head_index: 94, ???
        # arrow_head_handle: 345
        # END "arrow heads"
        # REPEAT "block attribs" (ATTDEF): DXF R2007+
        # attrib_handle: 330
        # attrib_index: 177, sequential index of the label in the collection
        # attrib_width: 44
        # attrib_text: 302, collision with group code (302, "LEADER{") in context data
        # END "block attribs"
        # Text Content:
        "is_text_direction_negative": DXFAttr(
            294, default=0, dxfversion=const.DXF2007
        ),
        "text_IPE_align": DXFAttr(178, default=0, dxfversion=const.DXF2007),
        "text_attachment_point": DXFAttr(
            179, default=1, dxfversion=const.DXF2007
        ),
        # 1 = left
        # 2 = center
        # 3 = right
        "scale": DXFAttr(45, default=1, dxfversion=const.DXF2007),
        "text_attachment_direction": DXFAttr(
            271, default=0, dxfversion=const.DXF2010
        ),
        # This defines whether the leaders attach to the left/right of the content
        # block/text, or attach to the top/bottom:
        # 0 = horizontal
        # 1 = vertical
        "text_bottom_attachment_direction": DXFAttr(
            272, default=9, dxfversion=const.DXF2010
        ),
        # like 173, but
        # 9 = center
        # 10= underline and center
        "text_top_attachment_direction": DXFAttr(
            273, default=9, dxfversion=const.DXF2010
        ),
        # like 173, but
        # 9 = center
        # 10= overline and center
        "leader_extend_to_text": DXFAttr(
            295, default=0, dxfversion=const.DXF2013
        ),
    },
)
acdb_mleader_group_codes = group_code_mapping(acdb_mleader)
CONTEXT_STR = "CONTEXT_DATA{"
LEADER_STR = "LEADER{"
LEADER_LINE_STR = "LEADER_LINE{"
START_CONTEXT_DATA = 300
END_CONTEXT_DATA = 301
START_LEADER = 302
END_LEADER = 303
START_LEADER_LINE = 304
END_LEADER_LINE = 305


def compile_context_tags(
    data: List["DXFTag"], stop_code: int
) -> List[Union["DXFTag", List]]:
    def build_structure(
        tag: "DXFTag", stop: int
    ) -> List[Union["DXFTag", List]]:
        collector = [tag]
        tag = next(tags)
        while tag.code != stop:
            if tag.code == START_LEADER:
                collector.append(build_structure(tag, END_LEADER))
            # Group code 304 is used also for MTEXT content, therefore always
            # test for group code AND and value string:
            elif tag.code == START_LEADER_LINE and tag.value == LEADER_LINE_STR:
                collector.append(build_structure(tag, END_LEADER_LINE))
            else:
                collector.append(tag)
            tag = next(tags)
        return collector

    tags = iter(data)
    return build_structure(next(tags), stop_code)


ArrowHeadData = namedtuple("ArrowHeadData", "index, handle")
AttribData = namedtuple("AttribData", "handle, index, width, text")


@register_entity
class MultiLeader(DXFGraphic):
    DXFTYPE = "MULTILEADER"
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mleader)
    MIN_DXF_VERSION_FOR_EXPORT = const.DXF2000

    def __init__(self):
        super().__init__()
        self.context = MultiLeaderContext()
        self.arrow_heads: List[ArrowHeadData] = []
        self.block_attribs: List[AttribData] = []

    def _copy_data(self, entity: "MultiLeader") -> None:
        """Copy leaders"""
        entity.context = copy.deepcopy(self.context)
        entity.arrow_heads = copy.deepcopy(self.arrow_heads)
        entity.block_attribs = copy.deepcopy(self.block_attribs)

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf
        tags = processor.subclass_by_index(2)
        if tags:
            context = self.extract_context_data(tags)
            if context:
                try:
                    self.context = self.load_context(context)
                except const.DXFStructureError:
                    logger.info(
                        f"Context structure error in entity MULTILEADER(#{dxf.handle})"
                    )
        else:
            raise const.DXFStructureError(
                f"missing 'AcDbMLeader' subclass in MULTILEADER(#{dxf.handle})"
            )

        self.arrow_heads = self.extract_arrow_heads(tags)
        self.block_attribs = self.extract_block_attribs(tags)

        processor.fast_load_dxfattribs(
            dxf, acdb_mleader_group_codes, subclass=tags, recover=True
        )
        return dxf

    @staticmethod
    def extract_context_data(tags: Tags) -> List["DXFTag"]:
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
            del tags[start:end]
        return context_data

    @staticmethod
    def load_context(data: List["DXFTag"]) -> "MultiLeaderContext":
        try:
            context = compile_context_tags(data, END_CONTEXT_DATA)
        except StopIteration:
            raise const.DXFStructureError
        else:
            return MultiLeaderContext.load(context)

    @staticmethod
    def extract_arrow_heads(data: Tags) -> List[ArrowHeadData]:
        def store_head():
            heads.append(
                ArrowHeadData(
                    collector.get(94, 0),  # arrow head index
                    collector.get(345, "0"),  # arrow head handle
                )
            )
            collector.clear()

        heads = []
        try:
            start = data.tag_index(94)
        except const.DXFValueError:
            return heads

        end = start
        collector = dict()
        for code, value in data.collect_consecutive_tags({94, 345}, start):
            end += 1
            collector[code] = value
            if code == 345:
                store_head()

        # Remove processed tags:
        del data[start:end]
        return heads

    @staticmethod
    def extract_block_attribs(data: Tags) -> List[AttribData]:
        def store_attrib():
            attribs.append(
                AttribData(
                    collector.get(330, "0"),  # ATTDEF handle
                    collector.get(177, 0),  # ATTDEF index
                    collector.get(44, 1.0),  # ATTDEF width
                    collector.get(302, ""),  # ATTDEF text (content)
                )
            )
            collector.clear()

        attribs = []
        try:
            start = data.tag_index(330)
        except const.DXFValueError:
            return attribs

        end = start
        collector = dict()
        for code, value in data.collect_consecutive_tags(
            {330, 177, 44, 302}, start
        ):
            end += 1
            if code == 330 and len(collector):
                store_attrib()
            collector[code] = value
        if len(collector):
            store_attrib()

        # Remove processed tags:
        del data[start:end]
        return attribs

    def preprocess_export(self, tagwriter: "TagWriter") -> bool:
        if self.context.is_valid:
            return True
        else:
            logger.debug(
                f"Ignore {str(self)} at DXF export, invalid context data."
            )
            return False

    def export_entity(self, tagwriter: "TagWriter") -> None:
        def write_handle_if_exist(code: int, name: str):
            handle = dxf.get(name)
            if handle is not None:
                write_tag2(code, handle)

        super().export_entity(tagwriter)
        dxf = self.dxf
        version = tagwriter.dxfversion
        write_tag2 = tagwriter.write_tag2

        write_tag2(100, acdb_mleader.name)
        write_tag2(270, dxf.version)
        self.context.export_dxf(tagwriter)

        # Export common MLEADER tags:
        # Don't use dxf.export_dxf_attribs() - all attributes should be written
        # even if equal to the default value:
        write_tag2(340, dxf.style_handle)
        write_tag2(90, dxf.property_override_flags)
        write_tag2(170, dxf.leader_type)
        write_tag2(91, dxf.leader_line_color)
        write_tag2(341, dxf.leader_linetype_handle)
        write_tag2(171, dxf.leader_lineweight)
        write_tag2(290, dxf.has_landing)
        write_tag2(291, dxf.has_dogleg)
        write_tag2(41, dxf.dogleg_length)
        # arrow_head_handle is None for default arrow 'closed filled':
        write_handle_if_exist(342, "arrow_head_handle")
        write_tag2(42, dxf.arrow_head_size)
        write_tag2(172, dxf.content_type)
        write_tag2(343, dxf.text_style_handle)  # mandatory!
        write_tag2(173, dxf.text_left_attachment_type)
        write_tag2(95, dxf.text_right_attachment_type)
        write_tag2(174, dxf.text_angle_type)
        write_tag2(175, dxf.text_alignment_type)
        write_tag2(92, dxf.text_color)
        write_tag2(292, dxf.has_frame_text)

        write_handle_if_exist(344, "block_record_handle")
        write_tag2(93, dxf.block_color)
        tagwriter.write_vertex(10, dxf.block_scale_vector)
        write_tag2(43, dxf.block_rotation)
        write_tag2(176, dxf.block_connection_type)
        write_tag2(293, dxf.is_annotative)
        if version >= const.DXF2007:
            self.export_arrow_heads(tagwriter)
            self.export_block_attribs(tagwriter)
            write_tag2(294, dxf.is_text_direction_negative)
            write_tag2(178, dxf.text_IPE_align)
            write_tag2(179, dxf.text_attachment_point)
            write_tag2(45, dxf.scale)

        if version >= const.DXF2010:
            write_tag2(271, dxf.text_attachment_direction)
            write_tag2(272, dxf.text_bottom_attachment_direction)
            write_tag2(273, dxf.text_top_attachment_direction)

        if version >= const.DXF2013:
            write_tag2(295, dxf.leader_extend_to_text)

    def export_arrow_heads(self, tagwriter: "TagWriter") -> None:
        for index, handle in self.arrow_heads:
            tagwriter.write_tag2(94, index)
            tagwriter.write_tag2(345, handle)

    def export_block_attribs(self, tagwriter: "TagWriter") -> None:
        for attrib in self.block_attribs:
            tagwriter.write_tag2(330, attrib.handle)
            tagwriter.write_tag2(177, attrib.index)
            tagwriter.write_tag2(44, attrib.width)
            tagwriter.write_tag2(302, attrib.text)

    def __virtual_entities__(self) -> Iterable["DXFGraphic"]:
        # As long as MLeader.virtual_entities() is not implemented,
        # use existing proxy graphic:
        if self.proxy_graphic:
            return ProxyGraphic(self.proxy_graphic, self.doc).virtual_entities()
        else:
            return []


class MultiLeaderContext:
    ATTRIBS = {
        40: "scale",
        10: "base_point",
        41: "text_height",
        140: "arrowhead_size",
        145: "landing_gap_size",
        174: "left_attachment",
        175: "right_attachment",
        176: "text_align_type",
        177: "attachment_type",
        110: "plane_origin",
        111: "plane_x_axis",
        112: "plane_y_axis",
        297: "plane_normal_reversed",
        272: "top_attachment",
        273: "bottom_attachment",
    }

    def __init__(self):
        self.leaders: List["Leader"] = []
        self.scale: float = 1.0  # overall scale
        self.base_point: Vec3 = NULLVEC
        self.text_height = 4.0
        self.arrowhead_size = 4.0
        self.landing_gap_size = 2.0
        self.left_attachment = 1
        self.right_attachment = 1
        self.text_align_type = 0  # 0=left, 1=center, 2=right
        self.attachment_type = 0  # 0=content extents, 1=insertion point
        self.mtext: Optional[MTextData] = None
        self.block: Optional[BlockData] = None
        self.plane_origin: Vec3 = NULLVEC
        self.plane_x_axis: Vec3 = X_AXIS
        self.plane_y_axis: Vec3 = Y_AXIS
        self.plane_normal_reversed: int = 0
        self.top_attachment = 9
        self.bottom_attachment = 9

    @classmethod
    def load(cls, context: List[Union["DXFTag", List]]) -> "MultiLeaderContext":
        assert context[0] == (START_CONTEXT_DATA, CONTEXT_STR)
        ctx = cls()
        content = None
        for tag in context:
            if isinstance(tag, list):  # Leader()
                ctx.leaders.append(Leader.load(tag))
                continue
            # parse context tags
            code, value = tag
            if content:
                if content.parse(code, value):
                    continue
                else:
                    content = None

            if code == 290 and value == 1:
                content = MTextData()
                ctx.mtext = content
            elif code == 296 and value == 1:
                content = BlockData()
                ctx.block = content
            else:
                name = MultiLeaderContext.ATTRIBS.get(code)
                if name:
                    ctx.__setattr__(name, value)
        return ctx

    @property
    def is_valid(self) -> bool:
        return True

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        write_tag2 = tagwriter.write_tag2
        write_vertex = tagwriter.write_vertex
        write_tag2(START_CONTEXT_DATA, CONTEXT_STR)
        # All MultiLeaderContext tags:
        write_tag2(40, self.scale)
        write_vertex(10, self.base_point)
        write_tag2(41, self.text_height)
        write_tag2(140, self.arrowhead_size)
        write_tag2(145, self.landing_gap_size)
        write_tag2(174, self.left_attachment)
        write_tag2(175, self.right_attachment)
        write_tag2(176, self.text_align_type)
        write_tag2(177, self.attachment_type)

        if self.mtext:
            write_tag2(290, 1)  # has mtext content
            self.mtext.export_dxf(tagwriter)
        else:
            write_tag2(290, 0)

        if self.block:
            write_tag2(296, 1)  # has block content
            self.block.export_dxf(tagwriter)
        else:
            write_tag2(296, 0)

        write_vertex(110, self.plane_origin)
        write_vertex(111, self.plane_x_axis)
        write_vertex(112, self.plane_y_axis)
        write_tag2(297, self.plane_normal_reversed)

        # Export Leader and LiederLine objects:
        for leader in self.leaders:
            leader.export_dxf(tagwriter)

        # Additional MultiLeaderContext tags:
        if tagwriter.dxfversion >= const.DXF2010:
            write_tag2(272, self.top_attachment)
            write_tag2(273, self.bottom_attachment)
        write_tag2(END_CONTEXT_DATA, "}")


class MTextData:
    ATTRIBS = {
        304: "default_content",
        11: "normal_direction",
        340: "style_handle",
        12: "location",
        13: "direction",
        42: "rotation",
        43: "boundary_width",
        44: "boundary_height",
        45: "line_space_factor",
        170: "line_space_style",
        90: "color",
        171: "alignment",
        172: "flow_direction",
        91: "bg_color",
        141: "bg_scale_factor",
        92: "bg_transparency",
        291: "has_bg_color",
        292: "has_bg_fill",
        173: "column_type",
        293: "use_auto_height",
        142: "column_width",
        143: "column_gutter_width",
        294: "column_flow_reversed",
        144: "column_sizes",  # multiple values
        295: "use_word_break",
    }

    def __init__(self):
        self.default_content: str = ""
        self.normal_direction: Vec3 = Z_AXIS
        self.style_handle = None  # handle of TextStyle() table entry
        self.location: Vec3 = NULLVEC
        self.direction: Vec3 = X_AXIS  # text direction
        self.rotation: float = 0.0  # in radians!
        self.boundary_width: float = 0.0
        self.boundary_height: float = 0.0
        self.line_space_factor: float = 1.0
        self.line_space_style: int = 1  # 1=at least, 2=exactly
        self.color: int = colors.BY_BLOCK_RAW_VALUE
        self.alignment: int = 1  # 1=left, 2=center, 3=right
        self.flow_direction: int = 1  # 1=horiz, 3=vert, 6=by style
        self.bg_color: int = -939524096  # use window background color? (CMC)
        self.bg_scale_factor: float = 1.5
        self.bg_transparency: int = 0
        self.has_bg_color: int = 0
        self.has_bg_fill: int = 0
        self.column_type: int = 0  # unknown values
        self.use_auto_height: int = 0
        self.column_width: float = 0.0
        self.column_gutter_width: float = 0.0
        self.column_flow_reversed: int = 0
        self.column_sizes: List[float] = []  # heights?
        self.use_word_break: int = 1

    def parse(self, code: int, value) -> bool:
        # return True if data belongs to mtext else False (end of mtext section)
        if code == 144:
            self.column_sizes.append(value)
            return True
        attrib = MTextData.ATTRIBS.get(code)
        if attrib:
            self.__setattr__(attrib, value)
        return bool(attrib)

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        write_tag2 = tagwriter.write_tag2
        write_vertex = tagwriter.write_vertex
        write_tag2(304, self.default_content)
        write_vertex(11, self.normal_direction)
        if self.style_handle:
            write_tag2(340, self.style_handle)
        else:
            # Do not write None, but "0" is also not valid!
            # DXF structure error should be detected before export.
            write_tag2(340, "0")
        write_vertex(12, self.location)
        write_vertex(13, self.direction)
        write_tag2(42, self.rotation)
        write_tag2(43, self.boundary_width)
        write_tag2(44, self.boundary_height)
        write_tag2(45, self.line_space_factor)
        write_tag2(170, self.line_space_style)
        write_tag2(90, self.color)
        write_tag2(171, self.alignment)
        write_tag2(172, self.flow_direction)
        write_tag2(91, self.bg_color)
        write_tag2(141, self.bg_scale_factor)
        write_tag2(92, self.bg_transparency)
        write_tag2(291, self.has_bg_color)
        write_tag2(292, self.has_bg_fill)
        write_tag2(173, self.column_type)
        write_tag2(293, self.use_auto_height)
        write_tag2(142, self.column_width)
        write_tag2(143, self.column_gutter_width)
        write_tag2(294, self.column_flow_reversed)
        for size in self.column_sizes:
            write_tag2(144, size)
        write_tag2(295, self.use_word_break)


class BlockData:
    ATTRIBS = {
        341: "block_record_handle",
        14: "normal_direction",
        15: "location",
        16: "scale",
        46: "rotation",
        93: "color",
    }

    def __init__(self):
        self.block_record_handle = None
        self.normal_direction: Vec3 = Z_AXIS
        self.location: Vec3 = NULLVEC
        self.scale: Vec3 = Vec3(1, 1, 1)
        self.rotation: float = 0  # in radians!
        self.color: int = colors.BY_BLOCK_RAW_VALUE
        # The transformation matrix is stored in transposed order
        # of ezdxf.math.Matrix44()!
        self._matrix: List[float] = []  # group code 47 x 16

    @property
    def matrix44(self) -> Matrix44:
        m = Matrix44(self._matrix)
        m.transpose()
        return m

    @matrix44.setter
    def matrix44(self, m: Matrix44) -> None:
        m = m.copy()
        m.transpose()
        self._matrix = list(m)

    def parse(self, code: int, value) -> bool:
        attrib = BlockData.ATTRIBS.get(code)
        if attrib:
            self.__setattr__(attrib, value)
        elif code == 47:
            self._matrix.append(value)
        else:
            return False
        # return True if data belongs to block else False (end of block section)
        return True

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        write_tag2 = tagwriter.write_tag2
        write_vertex = tagwriter.write_vertex
        if self.block_record_handle:
            write_tag2(341, self.block_record_handle)
        else:
            # Do not write None, but "0" is also not valid!
            # DXF structure error should be detected before export.
            write_tag2(341, "0")
        write_vertex(14, self.normal_direction)
        write_vertex(15, self.location)
        write_vertex(16, self.scale)
        write_tag2(46, self.rotation)
        write_tag2(93, self.color)
        for value in self._matrix:
            write_tag2(47, value)


class Leader:
    def __init__(self):
        self.lines: List["LeaderLine"] = []
        self.has_last_leader_line: int = 0  # group code 290
        self.has_dogleg_vector: int = 0  # group code 291
        self.last_leader_point: Vec3 = NULLVEC  # group code (10, 20, 30)
        self.dogleg_vector: Vec3 = X_AXIS  # group code (11, 21, 31)
        self.dogleg_length: float = 1.0  # group code 40
        self.index: int = 0  # group code 90
        self.attachment_direction: int = 0  # group code 271, R21010+
        self.breaks = []  # group code 12, 13 - multiple breaks possible!

    @classmethod
    def load(cls, context: List[Union["DXFTag", List]]):
        assert context[0] == (START_LEADER, LEADER_STR)
        leader = cls()
        for tag in context:
            if isinstance(tag, list):  # LeaderLine()
                leader.lines.append(LeaderLine.load(tag))
                continue

            code, value = tag
            if code == 290:
                leader.has_last_leader_line = value
            elif code == 291:
                leader.has_dogleg_vector = value
            elif code == 10:
                leader.last_leader_point = value
            elif code == 11:
                leader.dogleg_vector = value
            elif code == 40:
                leader.dogleg_length = value
            elif code == 90:
                leader.index = value
            elif code == 271:
                leader.attachment_direction = value
            elif code in (12, 13):
                leader.breaks.append(value)

        return leader

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        write_tag2 = tagwriter.write_tag2
        write_vertex = tagwriter.write_vertex

        write_tag2(START_LEADER, LEADER_STR)
        write_tag2(290, self.has_last_leader_line)
        write_tag2(291, self.has_dogleg_vector)
        if self.has_last_leader_line:
            write_vertex(10, self.last_leader_point)
        if self.has_dogleg_vector:
            write_vertex(11, self.dogleg_vector)

        code = 0
        for vertex in self.breaks:
            # write alternate group code 12 and 13
            write_vertex(12 + code, vertex)
            code = 1 - code
        write_tag2(90, self.index)
        write_tag2(40, self.dogleg_length)

        # Export leader lines:
        for line in self.lines:
            line.export_dxf(tagwriter)

        if tagwriter.dxfversion >= const.DXF2010:
            write_tag2(271, self.attachment_direction)
        write_tag2(END_LEADER, "}")


class LeaderLine:
    def __init__(self):
        self.vertices: List[Vec3] = []
        self.breaks: Optional[List[Union[int, Vec3]]] = None
        # Breaks: 90, 11, 12, [11, 12, ...] [, 90, 11, 12 [11, 12, ...]]
        # group code 90 = break index
        # group code 11 = start vertex of break
        # group code 12 = end vertex of break
        # multiple breaks per index possible
        self.index: int = 0  # group code 91
        self.color: int = colors.BY_BLOCK_RAW_VALUE  # group code 92
        # R2010+: override properties see ODA DWG pg. 214-215

    @classmethod
    def load(cls, tags: List["DXFTag"]):
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

    def export_dxf(self, tagwriter: "TagWriter") -> None:
        write_tag2 = tagwriter.write_tag2
        write_vertex = tagwriter.write_vertex

        write_tag2(START_LEADER_LINE, LEADER_LINE_STR)
        for vertex in self.vertices:
            write_vertex(10, vertex)
        if self.breaks:
            code = 0
            for value in self.breaks:
                if isinstance(value, int):
                    # break index
                    write_tag2(90, value)
                else:
                    # 11 .. start vertex of break
                    # 12 .. end vertex of break
                    write_vertex(11 + code, value)
                    code = 1 - code
        write_tag2(91, self.index)
        write_tag2(92, self.color)
        write_tag2(END_LEADER_LINE, "}")


@register_entity
class MLeader(MultiLeader):
    DXFTYPE = "MLEADER"


acdb_mleader_style = DefSubclass(
    "AcDbMLeaderStyle",
    {
        "unknown1": DXFAttr(179, default=2),
        "content_type": DXFAttr(170, default=2),
        "draw_mleader_order_type": DXFAttr(171, default=1),
        "draw_leader_order_type": DXFAttr(172, default=0),
        "max_leader_segments_points": DXFAttr(90, default=2),
        "first_segment_angle_constraint": DXFAttr(40, default=0.0),
        "second_segment_angle_constraint": DXFAttr(41, default=0.0),
        "leader_type": DXFAttr(173, default=1),
        "leader_line_color": DXFAttr(91, default=-1056964608),
        # raw color: BY_BLOCK
        # raw color: BY_BLOCK
        "leader_linetype_handle": DXFAttr(340),
        "leader_lineweight": DXFAttr(92, default=-2),
        "has_landing": DXFAttr(290, default=1),
        "landing_gap": DXFAttr(42, default=2.0),
        "has_dogleg": DXFAttr(291, default=1),
        "dogleg_length": DXFAttr(43, default=8),
        "name": DXFAttr(3, default="Standard"),
        # no handle is default arrow 'closed filled':
        "arrow_head_handle": DXFAttr(341),
        "arrow_head_size": DXFAttr(44, default=4),
        "default_text_content": DXFAttr(300, default=""),
        "text_style_handle": DXFAttr(342),
        "text_left_attachment_type": DXFAttr(174, default=1),
        "text_angle_type": DXFAttr(175, default=1),
        "text_alignment_type": DXFAttr(176, default=0),
        "text_right_attachment_type": DXFAttr(178, default=1),
        "text_color": DXFAttr(93, default=-1056964608),  # raw color: BY_BLOCK
        "text_height": DXFAttr(45, default=4),
        "has_frame_text": DXFAttr(292, default=0),
        "text_align_always_left": DXFAttr(297, default=0),
        "align_space": DXFAttr(46, default=4),
        "has_block_scaling": DXFAttr(293),
        "block_record_handle": DXFAttr(343),
        "block_color": DXFAttr(94, default=-1056964608),  # raw color: BY_BLOCK
        "block_scale_x": DXFAttr(47, default=1),
        "block_scale_y": DXFAttr(49, default=1),
        "block_scale_z": DXFAttr(140, default=1),
        "has_block_rotation": DXFAttr(294, default=1),
        "block_rotation": DXFAttr(141, default=0),
        "block_connection_type": DXFAttr(177, default=0),
        "scale": DXFAttr(142, default=1),
        "overwrite_property_value": DXFAttr(295, default=0),
        "is_annotative": DXFAttr(296, default=0),
        "break_gap_size": DXFAttr(143, default=3.75),
        # 0 = Horizontal; 1 = Vertical:
        "text_attachment_direction": DXFAttr(271, default=0),
        # 9 = Center; 10 = Underline and Center:
        "text_bottom__attachment_direction": DXFAttr(272, default=9),
        # 9 = Center; 10 = Overline and Center:
        "text_top_attachment_direction": DXFAttr(273, default=9),
        "unknown2": DXFAttr(298, optional=True),  # boolean flag ?
    },
)
acdb_mleader_style_group_codes = group_code_mapping(acdb_mleader_style)


@register_entity
class MLeaderStyle(DXFObject):
    DXFTYPE = "MLEADERSTYLE"
    DXFATTRIBS = DXFAttributes(base_class, acdb_mleader_style)
    MIN_DXF_VERSION_FOR_EXPORT = const.DXF2000

    def load_dxf_attribs(
        self, processor: SubclassProcessor = None
    ) -> "DXFNamespace":
        dxf = super().load_dxf_attribs(processor)
        if processor:
            processor.fast_load_dxfattribs(
                dxf, acdb_mleader_style_group_codes, subclass=1
            )
        return dxf

    def export_entity(self, tagwriter: "TagWriter") -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tag2(const.SUBCLASS_MARKER, acdb_mleader_style.name)
        self.dxf.export_dxf_attribs(
            tagwriter, acdb_mleader_style.attribs.keys()
        )


class MLeaderStyleCollection(ObjectCollection):
    def __init__(self, doc: "Drawing"):
        super().__init__(
            doc, dict_name="ACAD_MLEADERSTYLE", object_type="MLEADERSTYLE"
        )
        self.create_required_entries()

    def create_required_entries(self) -> None:
        for name in ("Standard",):
            if name not in self.object_dict:
                mleader_style = self.new(name)
                # set standard text style
                text_style = self.doc.styles.get("Standard")
                mleader_style.dxf.text_style_handle = text_style.dxf.handle
