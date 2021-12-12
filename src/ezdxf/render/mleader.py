#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Any, cast, List, Dict, Tuple, Optional, Union
import logging
import enum
from collections import defaultdict
from ezdxf import colors
from ezdxf.math import (
    Vec3,
    Vec2,
    Vertex,
    X_AXIS,
    Z_AXIS,
    fit_points_to_cad_cv,
    OCS,
    UCS,
    is_point_left_of_line,
)
from ezdxf.entities import factory
from ezdxf.lldxf import const
from ezdxf.proxygraphic import ProxyGraphic
from ezdxf.render.arrows import ARROWS, arrow_length
from ezdxf.tools.text_size import estimate_mtext_extents
from ezdxf.entities.mleader import (
    MultiLeader,
    MLeaderStyle,
    MTextData,
    BlockData,
    LeaderData,
    LeaderLine,
    acdb_mleader_style,
)

if TYPE_CHECKING:
    from ezdxf.document import Drawing
    from ezdxf.entities import (
        DXFGraphic,
        MText,
        Insert,
        Spline,
        Textstyle,
    )

__all__ = ["virtual_entities", "MultiLeaderBuilder", "ConnectionSide"]

logger = logging.getLogger("ezdxf")

# How to render MLEADER: https://atlight.github.io/formats/dxf-leader.html
# DXF reference:
# http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72D20B8C-0F5E-4993-BEB7-0FCF94F32BE0

# AutoCAD and BricsCAD always (?) use values stored in the MULTILEADER
# entity, even if the override flag isn't set!
IGNORE_OVERRIDE_FLAGS = True

OVERRIDE_FLAG = {
    "leader_type": 1 << 0,
    "leader_line_color": 1 << 1,
    "leader_linetype_handle": 1 << 2,
    "leader_lineweight": 1 << 3,
    "has_landing": 1 << 4,
    "landing_gap": 1 << 5,  # ??? not in MultiLeader
    "has_dogleg": 1 << 6,
    "dogleg_length": 1 << 7,
    "arrow_head_handle": 1 << 8,
    "arrow_head_size": 1 << 9,
    "content_type": 1 << 10,
    "text_style_handle": 1 << 11,
    "text_left_attachment_type": 1 << 12,
    "text_angle_type": 1 << 13,
    "text_alignment_type": 1 << 14,
    "text_color": 1 << 15,
    "char_height": 1 << 16,  # stored in MultiLeader.context.char_height
    "has_text_frame": 1 << 17,
    # 1 << 18 # use default content stored in MultiLeader.mtext.default_content
    "block_record_handle": 1 << 19,
    "block_color": 1 << 20,
    "block_scale_vector": 1 << 21,  # 3 values in MLeaderStyle
    "block_rotation": 1 << 22,
    "block_connection_type": 1 << 23,
    "scale": 1 << 24,
    "text_right_attachment_type": 1 << 25,
    "text_switch_alignment": 1 << 26,  # ??? not in MultiLeader/MLeaderStyle
    "text_attachment_direction": 1 << 27,  # this flag is not set by BricsCAD
    "text_top_attachment_type": 1 << 28,
    "text_bottom_attachment_type": 1 << 29,
}


class MLeaderStyleOverride:
    def __init__(self, style: MLeaderStyle, mleader: MultiLeader):
        self._style_dxf = style.dxf
        self._mleader_dxf = mleader.dxf
        self._context = mleader.context
        self._property_override_flags = mleader.dxf.get(
            "property_override_flags", 0
        )
        self._block_scale_vector = Vec3(
            (
                style.dxf.get("block_scale_x", 1.0),
                style.dxf.get("block_scale_y", 1.0),
                style.dxf.get("block_scale_z", 1.0),
            )
        )
        self.use_mtext_default_content = bool(
            self._property_override_flags & (1 << 18)
        )  # if False, what MTEXT content is used?

    def get(self, attrib_name: str) -> Any:
        # Set MLEADERSTYLE value as default value:
        if attrib_name == "block_scale_vector":
            value = self._block_scale_vector
        else:
            value = self._style_dxf.get_default(attrib_name)
        if IGNORE_OVERRIDE_FLAGS or self.is_overridden(attrib_name):
            # Get overridden value from MULTILEADER:
            if attrib_name == "char_height":
                value = self._context.char_height
            else:
                value = self._mleader_dxf.get(attrib_name, value)
        return value

    def is_overridden(self, attrib_name: str) -> bool:
        flag = OVERRIDE_FLAG.get(attrib_name, 0)
        return bool(flag & self._property_override_flags)


def virtual_entities(
    mleader: MultiLeader, proxy_graphic=False
) -> List["DXFGraphic"]:
    doc = mleader.doc
    assert doc is not None, "valid DXF document required"
    if proxy_graphic and mleader.proxy_graphic is not None:
        return list(ProxyGraphic(mleader.proxy_graphic, doc).virtual_entities())
    else:
        return RenderEngine(mleader, doc).run()


def get_style(mleader: MultiLeader, doc: "Drawing") -> MLeaderStyleOverride:
    handle = mleader.dxf.style_handle
    style = doc.entitydb.get(handle)
    if style is None:
        logger.warning(
            f"referenced MLEADERSTYLE(#{handle}) does not exist, "
            f"replaced by 'Standard'"
        )
        style = doc.mleader_styles.get("Standard")
    assert style is not None, "mandatory MLEADERSTYLE 'Standard' does not exist"
    return MLeaderStyleOverride(cast(MLeaderStyle, style), mleader)


def get_text_style(handle: str, doc: "Drawing") -> "Textstyle":
    text_style = doc.entitydb.get(handle)
    if text_style is None:
        logger.warning(
            f"referenced STYLE(#{handle}) does not exist, "
            f"replaced by 'Standard'"
        )
        text_style = doc.styles.get("Standard")
    assert text_style is not None, "mandatory STYLE 'Standard' does not exist"
    return text_style  # type: ignore


def get_arrow_direction(vertices: List[Vec3]) -> Vec3:
    if len(vertices) < 2:
        return X_AXIS
    direction = vertices[1] - vertices[0]
    return direction.normalize()


ACI_COLOR_TYPES = {
    colors.COLOR_TYPE_BY_BLOCK,
    colors.COLOR_TYPE_BY_LAYER,
    colors.COLOR_TYPE_ACI,
}


def decode_raw_color(raw_color: int) -> Tuple[int, Optional[int]]:
    aci_color = colors.BYBLOCK
    true_color: Optional[int] = None
    color_type, color = colors.decode_raw_color_int(raw_color)
    if color_type in ACI_COLOR_TYPES:
        aci_color = color
    elif color_type == colors.COLOR_TYPE_RGB:
        true_color = color
    # COLOR_TYPE_WINDOW_BG: not supported as entity color
    return aci_color, true_color


def copy_mtext_data(
    mtext: "MText", mtext_data: MTextData, scale: float
) -> None:
    # MLEADERSTYLE has a flag "use_mtext_default_content", what else should be
    # used as content if this flag is false?
    mtext.text = mtext_data.default_content
    dxf = mtext.dxf
    aci_color, true_color = decode_raw_color(mtext_data.color)
    dxf.color = aci_color
    if true_color is not None:
        dxf.true_color = true_color
    dxf.insert = mtext_data.insert
    assert mtext.doc is not None
    mtext.dxf.style = get_text_style(
        mtext_data.style_handle, mtext.doc
    ).dxf.name
    if not mtext_data.extrusion.isclose(Z_AXIS):
        dxf.extrusion = mtext_data.extrusion
    dxf.text_direction = mtext_data.text_direction
    # ignore rotation!
    dxf.width = mtext_data.width * scale
    dxf.line_spacing_factor = mtext_data.line_spacing_factor
    dxf.line_spacing_style = mtext_data.line_spacing_style
    dxf.flow_direction = mtext_data.flow_direction
    # alignment=attachment_point: 1=top left, 2=top center, 3=top right
    dxf.attachment_point = mtext_data.alignment


def set_mtext_bg_fill(mtext: "MText", mtext_data: MTextData) -> None:
    # Note: the "text frame" flag (16) in "bg_fill" is never set by BricsCAD!
    # Set required DXF attributes:
    mtext.dxf.box_fill_scale = mtext_data.bg_scale_factor
    mtext.dxf.bg_fill = 1
    mtext.dxf.bg_fill_color = colors.BYBLOCK
    mtext.dxf.bg_fill_transparency = mtext_data.bg_transparency
    color_type, color = colors.decode_raw_color_int(mtext_data.bg_color)
    if color_type in ACI_COLOR_TYPES:
        mtext.dxf.bg_fill_color = color
    elif color_type == colors.COLOR_TYPE_RGB:
        mtext.dxf.bg_fill_true_color = color

    if (
        mtext_data.use_window_bg_color
        or color_type == colors.COLOR_TYPE_WINDOW_BG
    ):
        # override fill mode, but keep stored colors
        mtext.dxf.bg_fill = 3


def set_mtext_columns(
    mtext: "MText", mtext_data: MTextData, scale: float
) -> None:
    # BricsCAD does not support columns for MTEXT content, so exploring
    # MLEADER with columns was not possible!
    pass


def _get_insert(entity: MultiLeader) -> Vec3:
    context = entity.context
    if context.mtext is not None:
        return context.mtext.insert
    elif context.block is not None:
        return context.block.insert
    return context.plane_origin


def _get_extrusion(entity: MultiLeader) -> Vec3:
    context = entity.context
    if context.mtext is not None:
        return context.mtext.extrusion
    elif context.block is not None:
        return context.block.extrusion
    return context.plane_z_axis


def _get_dogleg_vector(leader: LeaderData, default: Vec3 = X_AXIS) -> Vec3:
    # All leader vertices and directions in WCS!
    try:
        if leader.has_dogleg_vector:  # what else?
            return leader.dogleg_vector.normalize(leader.dogleg_length)
    except ZeroDivisionError:  # dogleg_vector is NULL
        pass
    return default.normalize(leader.dogleg_length)


def _get_block_name(handle: str, doc: "Drawing") -> Optional[str]:
    block_record = doc.entitydb.get(handle)
    if block_record is None:
        logger.error(f"required BLOCK_RECORD entity #{handle} does not exist")
        return None
    return block_record.dxf.get("name")  # has no default value


class RenderEngine:
    def __init__(self, mleader: MultiLeader, doc: "Drawing"):
        self.entities: List["DXFGraphic"] = []  # result container
        self.mleader = mleader
        self.doc = doc
        self.style: MLeaderStyleOverride = get_style(mleader, doc)
        self.context = mleader.context
        self.insert = _get_insert(mleader)
        self.extrusion: Vec3 = _get_extrusion(mleader)
        self.ocs: Optional[OCS] = None
        if not self.extrusion.isclose(Z_AXIS):
            self.ocs = OCS(self.extrusion)
        self.elevation: float = self.insert.z

        # Gather final parameters from various places:
        # This is the actual entity scaling, ignore scale in MLEADERSTYLE!
        self.scale: float = self.context.scale
        self.layer = mleader.dxf.layer
        self.linetype = self.linetype_name()
        self.lineweight = self.style.get("leader_lineweight")
        aci_color, true_color = decode_raw_color(
            self.style.get("leader_line_color")
        )
        self.leader_aci_color: int = aci_color
        self.leader_true_color: Optional[int] = true_color
        self.leader_type: int = self.style.get("leader_type")
        self.has_text_frame = False
        self.has_dogleg: bool = bool(self.style.get("has_dogleg"))
        self.arrow_heads: Dict[int, str] = {
            head.index: head.handle for head in mleader.arrow_heads
        }
        self.arrow_head_handle = self.style.get("arrow_head_handle")
        self.dxf_mtext_entity: Optional["MText"] = None
        self._dxf_mtext_extents: Optional[Tuple[float, float]] = None
        self.has_horizontal_attachment = bool(
            self.style.get("text_attachment_direction")
        )
        self.left_attachment_type = self.style.get("text_left_attachment_type")
        self.right_attachment_type = self.style.get(
            "text_right_attachment_type"
        )
        self.top_attachment_type = self.style.get("text_top_attachment_type")
        self.bottom_attachment_type = self.style.get(
            "text_bottom_attachment_type"
        )

    @property
    def has_extrusion(self) -> bool:
        return self.ocs is not None

    @property
    def has_text_content(self) -> bool:
        return self.context.mtext is not None

    @property
    def has_block_content(self) -> bool:
        return self.context.block is not None

    @property
    def mtext_extents(self) -> Tuple[float, float]:
        """Calculate MTEXT width on demand."""

        if self._dxf_mtext_extents is not None:
            return self._dxf_mtext_extents
        if self.dxf_mtext_entity is not None:
            # TODO: this is very inaccurate if using inline codes, better
            #  solution is required like a text layout engine with column width
            #  calculation from the MTEXT content.
            width, height = estimate_mtext_extents(self.dxf_mtext_entity)
        else:
            width, height = 0.0, 0.0
        self._dxf_mtext_extents = (width, height)
        return self._dxf_mtext_extents

    def run(self) -> List["DXFGraphic"]:
        """Entry point to render MLEADER entities."""
        self.entities.clear()
        if abs(self.scale) > 1e-9:
            self.add_content()
            self.add_leaders()
        # otherwise it vanishes by scaling down to almost "nothing"
        return self.entities

    def linetype_name(self) -> str:
        handle = self.style.get("leader_linetype_handle")
        ltype = self.doc.entitydb.get(handle)
        if ltype is not None:
            return ltype.dxf.name
        logger.warning(f"invalid linetype handle #{handle} in {self.mleader}")
        return "Continuous"

    def arrow_block_name(self, index: int) -> str:
        closed_filled = "_CLOSED_FILLED"
        handle = self.arrow_heads.get(index, self.arrow_head_handle)
        if handle is None or handle == "0":
            return closed_filled
        block_record = self.doc.entitydb.get(handle)
        if block_record is None:
            logger.warning(
                f"arrow block #{handle} in {self.mleader} does not exist, "
                f"replaced by closed filled arrow"
            )
            return closed_filled
        return block_record.dxf.name

    def leader_line_attribs(self, raw_color: int = None) -> Dict:
        aci_color = self.leader_aci_color
        true_color = self.leader_true_color

        # Ignore color override value BYBLOCK!
        if raw_color and raw_color is not colors.BY_BLOCK_RAW_VALUE:
            aci_color, true_color = decode_raw_color(raw_color)

        attribs = {
            "layer": self.layer,
            "color": aci_color,
            "linetype": self.linetype,
            "lineweight": self.lineweight,
        }
        if true_color is not None:
            attribs["true_color"] = true_color
        return attribs

    def add_content(self) -> None:
        # also check self.style.get("content_type") ?
        if self.has_text_content:
            self.add_mtext_content()
        elif self.has_block_content:
            self.add_block_content()

    def add_mtext_content(self) -> None:
        mtext = cast("MText", factory.new("MTEXT", doc=self.doc))
        mtext.dxf.layer = self.layer
        # !char_height is the final already scaled value!
        mtext.dxf.char_height = self.context.char_height
        mtext_data: MTextData = self.context.mtext
        if mtext_data is not None:
            copy_mtext_data(mtext, mtext_data, self.scale)
            if mtext_data.has_bg_fill:
                set_mtext_bg_fill(mtext, mtext_data)
            set_mtext_columns(mtext, mtext_data, self.scale)
        self.entities.append(mtext)
        self.dxf_mtext_entity = mtext

        if self.has_text_frame:
            self.add_text_frame()

    def add_text_frame(self) -> None:
        # not supported - yet?
        # 1. This requires a full MTEXT height calculation.
        # 2. Only the default rectangle and the rounded rectangle are
        #    acceptable every other text frame is just ugly, especially
        #    when the MTEXT gets more complex.
        pass

    def add_block_content(self) -> None:
        block = self.context.block
        assert block is not None
        block_name = _get_block_name(block.block_record_handle, self.doc)
        if block_name is None:
            return
        location = block.insert  # in WCS, really funny for an OCS entity!
        if self.ocs is not None:
            location = self.ocs.from_wcs(location)
        aci_color, true_color = decode_raw_color(block.color)
        scale = block.scale
        attribs = {
            "name": block_name,
            "insert": location,
            "color": aci_color,
            "extrusion": block.extrusion,
            "xscale": scale.x,
            "yscale": scale.y,
            "zscale": scale.z,
        }
        if true_color is not None:
            attribs["true_color"] = true_color
        insert = cast(
            "Insert", factory.new("INSERT", dxfattribs=attribs, doc=self.doc)
        )
        self.entities.append(insert)
        if self.mleader.block_attribs:
            self.add_block_attributes(insert)

    def add_block_attributes(self, insert: "Insert"):
        entitydb = self.doc.entitydb
        values: Dict[str, str] = dict()
        for attrib in self.mleader.block_attribs:
            attdef = entitydb.get(attrib.handle)
            if attdef is None:
                logger.error(
                    f"required ATTDEF entity #{attrib.handle} does not exist"
                )
                continue
            tag = attdef.dxf.tag
            values[tag] = attrib.text
        if values:
            insert.add_auto_attribs(values)

    def add_leaders(self) -> None:
        if self.leader_type == 0:
            return

        for leader in self.context.leaders:
            for line in leader.lines:
                self.add_leader_line(leader, line)

            if self.has_text_content:
                if leader.has_horizontal_attachment:
                    # add text underlines for these horizontal attachment styles:
                    # 5 = bottom of bottom text line & underline bottom text line
                    # 6 = bottom of top text line & underline top text line
                    self.add_text_underline(leader)
                else:
                    # text with vertical attachment may have an extra "overline"
                    # across the text
                    self.add_overline(leader)

    def add_text_underline(self, leader: LeaderData):
        mtext = self.context.mtext
        if mtext is None:
            return
        has_left_underline = self.left_attachment_type in (5, 6)
        has_right_underline = self.right_attachment_type in (5, 6)
        if not (has_left_underline or has_right_underline):
            return
        connection_point = leader.last_leader_point + _get_dogleg_vector(leader)
        width, height = self.mtext_extents
        length = width + self.context.landing_gap_size
        if length < 1e-9:
            return
        # The connection point is on the "left" or "right" side of the
        # detection line, which is a "vertical" line through the text
        # insertion point.
        start = mtext.insert
        if self.ocs is None:  # text plane is parallel to the xy-plane
            start2d = start.vec2
            up2d = mtext.text_direction.vec2.orthogonal()
            cp2d = connection_point.vec2
        else:  # project points into the text plane
            from_wcs = self.ocs.from_wcs
            start2d = Vec2(from_wcs(start))
            up2d = Vec2(from_wcs(mtext.text_direction)).orthogonal()
            cp2d = Vec2(from_wcs(connection_point))
        is_left = is_point_left_of_line(cp2d, start2d, start2d + up2d)
        is_right = not is_left
        line = mtext.text_direction.normalize(length if is_left else -length)
        if (is_left and has_left_underline) or (
            is_right and has_right_underline
        ):
            self.add_dxf_line(connection_point, connection_point + line)

    def add_overline(self, leader: LeaderData):
        mtext = self.context.mtext
        if mtext is None:
            return
        has_bottom_line = self.bottom_attachment_type == 10
        has_top_line = self.top_attachment_type == 10
        if not (has_bottom_line or has_top_line):
            return
        length, height = self.mtext_extents
        if length < 1e-9:
            return

        # The end of the leader is the center of the "overline".
        # The leader is on the bottom of the text if the insertion
        # point of the text is left of "overline" (start -> end).
        center = leader.last_leader_point
        insert = mtext.insert
        line2 = mtext.text_direction.normalize(length / 2)
        start = center - line2
        end = center + line2

        if self.ocs is None:  # z-axis is ignored
            bottom = is_point_left_of_line(insert, start, end)
        else:  # project points into the text plane, z-axis is ignored
            from_wcs = self.ocs.from_wcs
            bottom = is_point_left_of_line(
                from_wcs(insert), from_wcs(start), from_wcs(end)
            )
        top = not bottom
        if (bottom and has_bottom_line) or (top and has_top_line):
            self.add_dxf_line(start, end)

    def leader_vertices(
        self, leader: LeaderData, line_vertices: List[Vec3], has_dogleg=False
    ) -> List[Vec3]:
        # All leader vertices and directions in WCS!
        vertices = list(line_vertices)
        end_point = leader.last_leader_point
        if leader.has_horizontal_attachment:
            if has_dogleg:
                vertices.append(end_point)
            vertices.append(end_point + _get_dogleg_vector(leader))
        else:
            vertices.append(end_point)
        return vertices

    def add_leader_line(self, leader: LeaderData, line: LeaderLine):
        # All leader vertices and directions in WCS!
        leader_type: int = self.leader_type
        if leader_type == 0:  # invisible leader lines
            return
        has_dogleg: bool = self.has_dogleg
        if leader_type == 2:  # splines do not have a dogleg!
            has_dogleg = False
        vertices: List[Vec3] = self.leader_vertices(
            leader, line.vertices, has_dogleg
        )
        if len(vertices) < 2:  # at least 2 vertices required
            return

        arrow_direction: Vec3 = get_arrow_direction(vertices)
        raw_color: int = line.color
        index: int = line.index
        block_name: str = self.create_arrow_block(self.arrow_block_name(index))
        arrow_size: float = self.context.arrow_head_size
        self.add_arrow(
            name=block_name,
            location=vertices[0],
            direction=arrow_direction,
            scale=arrow_size,
            color=raw_color,
        )
        arrow_offset: Vec3 = arrow_direction * arrow_length(
            block_name, arrow_size
        )
        vertices[0] += arrow_offset
        if leader_type == 1:  # add straight lines
            for s, e in zip(vertices, vertices[1:]):
                self.add_dxf_line(s, e, raw_color)
        elif leader_type == 2:  # add spline
            if leader.has_horizontal_attachment:
                end_tangent = _get_dogleg_vector(leader)
            else:
                end_tangent = vertices[-1] - vertices[-2]
            self.add_dxf_spline(
                vertices,
                # tangent normalization is not required
                tangents=[arrow_direction, end_tangent],
                color=raw_color,
            )

    def create_arrow_block(self, name: str) -> str:
        if name not in self.doc.blocks:
            # create predefined arrows
            arrow_name = ARROWS.arrow_name(name)
            if arrow_name not in ARROWS:
                arrow_name = ARROWS.closed_filled
            name = ARROWS.create_block(self.doc.blocks, arrow_name)
        return name

    def add_dxf_spline(
        self, fit_points: List[Vec3], tangents=None, color: int = None
    ):
        attribs = self.leader_line_attribs(color)
        spline = cast(
            "Spline",
            factory.new("SPLINE", dxfattribs=attribs, doc=self.doc),
        )
        spline.apply_construction_tool(
            fit_points_to_cad_cv(fit_points, tangents=tangents)
        )
        self.entities.append(spline)

    def add_dxf_line(self, start: Vec3, end: Vec3, color: int = None):
        attribs = self.leader_line_attribs(color)
        attribs["start"] = start
        attribs["end"] = end
        self.entities.append(
            factory.new("LINE", dxfattribs=attribs, doc=self.doc)  # type: ignore
        )

    def add_arrow(
        self,
        name: str,
        location: Vec3,
        direction: Vec3,
        scale: float,
        color: int,
    ):
        attribs = self.leader_line_attribs(color)
        attribs["name"] = name
        if self.ocs is not None:
            location = self.ocs.from_wcs(location)
            direction = self.ocs.from_wcs(direction)
            attribs["extrusion"] = self.extrusion

        attribs["insert"] = location
        attribs["rotation"] = direction.angle_deg + 180.0
        attribs["xscale"] = scale
        attribs["yscale"] = scale
        attribs["zscale"] = scale
        self.entities.append(
            factory.new("INSERT", dxfattribs=attribs, doc=self.doc)  # type: ignore
        )


class LeaderType(enum.IntEnum):
    none = 0
    straight_lines = 1
    splines = 2


class ConnectionSide(enum.Enum):
    left = enum.auto()
    right = enum.auto()
    top = enum.auto()
    bottom = enum.auto()


class HorizontalConnection(enum.IntEnum):
    by_style = 0
    top_of_top_line = 1
    middle_of_top_line = 2
    middle_of_text = 2
    middle_of_bottom_line = 3
    bottom_of_bottom_line = 4
    bottom_of_bottom_line_underline = 5
    bottom_of_top_line_underline = 6
    bottom_of_top_line = 7
    bottom_of_top_line_underline_all = 8


class VerticalConnection(enum.IntEnum):
    by_style = 0
    center = 9
    center_overline = 10


class TextAlignment(enum.IntEnum):
    left = 1
    center = 2
    right = 3


class BlockAlignment(enum.IntEnum):
    center_extents = 0
    insertion_point = 1


class MultiLeaderBuilder:
    def __init__(self, multileader: MultiLeader):
        doc = multileader.doc
        assert doc is not None, "valid DXF document required"
        self.doc: "Drawing" = doc
        self.multileader = multileader
        self.context = multileader.context
        self.ucs = UCS()
        style: MLeaderStyle = self.doc.entitydb.get(
            self.multileader.dxf.style_handle
        )  # type: ignore

        self._mleader_style: MLeaderStyle = style
        self._leaders: Dict[ConnectionSide, List[List[Vec3]]] = defaultdict(
            list
        )
        self.set_mleader_style(style)
        # landing gap size is not stored in MULTILEADER
        self.landing_gap = self._mleader_style.dxf.landing_gap

    def set_mleader_style(self, style: MLeaderStyle):
        """Reset base properties by :class:`~ezdxf.entities.MLeaderStyle`
        properties. This also resets the content!
        """
        self._mleader_style = style
        multileader_dxf = self.multileader.dxf
        style_dxf = style.dxf
        keys = list(acdb_mleader_style.attribs.keys())
        for key in keys:
            if multileader_dxf.is_supported(key):
                multileader_dxf.set(key, style_dxf.get_default(key))
        multileader_dxf.block_scale_vector = Vec3(
            style_dxf.block_scale_x,
            style_dxf.block_scale_y,
            style_dxf.block_scale_z,
        )
        self._init_content()

    def _init_content(self):
        content_type = self.multileader.dxf.content_type
        if content_type == 1:
            self._build_block_content()
        elif content_type == 2:
            self._build_mtext_content()

    def _build_mtext_content(self):
        context = self.context
        style = self._mleader_style
        mleader = self.multileader

        # reset content type
        mleader.dxf.content_type = 2
        context.block = None

        # create default mtext content
        mtext = MTextData()
        context.mtext = mtext

        mtext.default_content = style.dxf.default_text_content
        mtext.extrusion = context.plane_z_axis
        mtext.style_handle = mleader.dxf.text_style_handle
        mtext.insert = context.base_point
        mtext.text_direction = context.plane_x_axis
        mtext.color = mleader.dxf.text_color
        mtext.alignment = mleader.dxf.text_attachment_point
        mtext.bg_color = colors.WINDOW_BG_RAW_VALUE
        mtext.bg_scale_factor = 1.5
        mtext.bg_transparency = 0
        mtext.use_window_bg_color = 0
        mtext.has_bg_fill = 0
        mtext.column_type = 0  # unknown values
        mtext.use_auto_height = 0
        mtext.column_width = 0.0  # not scaled
        mtext.column_gutter_width = 0.0  # not scaled
        mtext.column_flow_reversed = 0
        mtext.use_word_break = 1
        # todo: rotation

    def _build_block_content(self):
        context = self.context
        mleader = self.multileader

        # set content type
        mleader.dxf.content_type = 1
        context.mtext = None

        # create default block content
        block = BlockData()
        block.block_record_handle = mleader.dxf.block_record_handle
        block.extrusion = context.plane_z_axis
        block.insert = context.base_point
        block.scale = mleader.dxf.block_scale_vector
        block.rotation = mleader.dxf.block_rotation
        block.color = mleader.dxf.block_color

    def set_content_properties(  # todo: better method name
        self,
        landing_gap: float = 0.0,
        dogleg_length: float = 0.0,
        ucs: UCS = None,
    ):
        mleader = self.multileader
        context = mleader.context
        if ucs:
            self.ucs = ucs
            context.plane_origin = ucs.origin
            context.plane_x_axis = ucs.ux
            context.plane_y_axis = ucs.uy
            context.plane_normal_reversed = 0
        if dogleg_length:
            mleader.dxf.has_dogleg = 1
            mleader.dxf.dogleg_length = dogleg_length
        else:
            mleader.dxf.has_dogleg = 0
        self.landing_gap = landing_gap

    def set_connection_types(
        self,
        left=HorizontalConnection.by_style,
        right=HorizontalConnection.by_style,
        top=VerticalConnection.by_style,
        bottom=VerticalConnection.by_style,
    ):
        dxf = self.multileader.dxf
        style = self._mleader_style
        if left == HorizontalConnection.by_style:
            dxf.text_left_attachment_type = style.dxf.text_left_attachment_type
        else:
            dxf.text_left_attachment_type = int(left)

        if right == HorizontalConnection.by_style:
            dxf.text_right_attachment_type = (
                style.dxf.text_right_attachment_type
            )
        else:
            dxf.text_right_attachment_type = int(right)

        if top == VerticalConnection.by_style:
            dxf.text_top_attachment_type = style.dxf.text_top_attachment_type
        else:
            dxf.text_top_attachment_type = int(top)

        if bottom == VerticalConnection.by_style:
            dxf.text_bottom_attachment_type = (
                style.dxf.text_bottom_attachment_type
            )
        else:
            dxf.text_bottom_attachment_type = int(bottom)

    def set_mtext_content(
        self,
        location: Vertex,
        content: str,
        color: Union[int, colors.RGB] = colors.BYBLOCK,
        char_height: float = 0.0,  # 0.0 is by style
        alignment: TextAlignment = TextAlignment.left,
    ):
        mleader = self.multileader
        # update MULTILEADER DXF namespace
        mleader.dxf.text_color = colors.encode_raw_color(color)
        mleader.dxf.text_attachment_point = int(alignment)
        self._set_base_point(location)
        # build MTextData object
        self._build_mtext_content()
        # following attributes are not stored in the MULTILEADER DXF namespace
        self.context.mtext.default_content = content
        if char_height:
            self.context.char_height = char_height

    def _set_base_point(self, location: Vertex):
        # todo: is WCS conversion correct in context.plan_origin != (0, 0, 0)?
        self.context.base_point = self.ucs.to_wcs(location)

    def set_block_content(
        self,
        location: Vertex,
        name: str,  # block name
        color: Union[int, colors.RGB] = colors.BYBLOCK,
        scale: float = 1.0,
        rotation: float = 0.0,
        alignment=BlockAlignment.center_extents,
    ):
        mleader = self.multileader
        self._set_base_point(location)
        # update MULTILEADER DXF namespace
        block = self.doc.blocks.get(name)
        if block is None:
            raise ValueError(f"undefined BLOCK '{name}'")
        mleader.dxf.block_record_handle = block.block_record_handle
        mleader.dxf.block_color = colors.encode_raw_color(color)
        mleader.dxf.block_scale_vector = Vec3(scale, scale, scale)
        mleader.dxf.block_rotation = rotation
        mleader.dxf.block_connection_type = int(alignment)
        self._build_mtext_content()

    def set_leader_properties(
        self,
        color: Union[int, colors.RGB] = colors.BYBLOCK,
        linetype: str = "BYBLOCK",
        lineweight: int = const.LINEWEIGHT_BYBLOCK,
        leader_type=LeaderType.straight_lines,
    ):
        mleader = self.multileader
        mleader.dxf.leader_line_color = colors.encode_raw_color(color)  # type: ignore
        linetype_ = self.doc.linetypes.get(linetype)
        if linetype_ is None:
            raise ValueError(f"undefined linetype '{linetype}'")
        mleader.dxf.leader_linetype_handle = linetype_.dxf.handle
        mleader.dxf.leader_lineweight = lineweight
        mleader.dxf.leader_type = int(leader_type)

    def set_arrow_properties(
        self,
        name: str = "",
        size: float = 0.0,  # 0=by style
    ):
        if size:
            self.multileader.dxf.arrow_head_size = size
        else:
            self.multileader.dxf.arrow_head_size = (
                self._mleader_style.dxf.arrow_head_size
            )
        if name:
            self.multileader.dxf.arrow_head_handle = ARROWS.arrow_handle(
                self.doc.blocks, name
            )
        else:
            # empty string is the default "closed filled" arrow,
            # no handle needed
            del self.multileader.dxf.arrow_head_handle

    def add_leader_line(self, side: ConnectionSide, vertices: List[Vertex]):
        _vertices = Vec3.list(vertices)
        self._leaders[side].append(_vertices)

    def build(self):
        """Build geometry data"""
        pass
