#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Any, cast, List, Dict, Tuple, Optional
import logging

from ezdxf import colors
from ezdxf.math import (
    Vec3,
    X_AXIS,
    Z_AXIS,
    fit_points_to_cad_cv,
    OCS,
)
from ezdxf.entities import factory
from ezdxf.proxygraphic import ProxyGraphic
from ezdxf.render.arrows import ARROWS, arrow_length

if TYPE_CHECKING:
    from ezdxf.document import Drawing
    from ezdxf.entities import (
        DXFGraphic,
        MText,
        Insert,
        Attrib,
        Line,
        Spline,
        Textstyle,
    )
    from ezdxf.entities.mleader import (
        MLeader,
        MLeaderStyle,
        MTextData,
        LeaderData,
        LeaderLine,
    )
    from ezdxf.layouts import BlockLayout

__all__ = ["virtual_entities"]

logger = logging.getLogger("ezdxf")

# DXF Examples:
# "D:\source\dxftest\CADKitSamples\house design for two family with common staircasedwg.dxf"
# "D:\source\dxftest\CADKitSamples\house design.dxf"

# How to render MLEADER: https://atlight.github.io/formats/dxf-leader.html
# DXF reference:
# http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72D20B8C-0F5E-4993-BEB7-0FCF94F32BE0

OVERRIDE_FLAG = {
    "leader_type": 1 << 0,
    "leader_line_color": 1 << 1,
    "leader_linetype_handle": 1 << 2,
    "leader_lineweight": 1 << 3,
    "has_landing": 1 << 4,
    "landing_gap": 1 << 5,  # ??? not in MLeader
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
    "char_height": 1 << 16,  # stored in MLeader.context.char_height
    "has_text_frame": 1 << 17,
    # 1 << 18 # use default content stored in MLeader.mtext.default_content
    "block_record_handle": 1 << 19,
    "block_color": 1 << 20,
    "block_scale_vector": 1 << 21,  # 3 values in MLeaderStyle
    "block_rotation": 1 << 22,
    "block_connection_type": 1 << 23,
    "scale": 1 << 24,
    "text_right_attachment_type": 1 << 25,
    "text_switch_alignment": 1 << 26,  # ??? not in MLeader/MLeaderStyle
    "text_attachment_direction": 1 << 27,  # this flag is not set by BricsCAD
    "text_top_attachment_direction": 1 << 28,
    "text_bottom_attachment_direction": 1 << 29,
}


class MLeaderStyleOverride:
    def __init__(self, style: "MLeaderStyle", mleader: "MLeader"):
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
        # Set MLEADERSTYLE value as default:
        if attrib_name == "block_scale_vector":
            value = self._block_scale_vector
        else:
            value = self._style_dxf.get_default(attrib_name)
        if self.is_overridden(attrib_name):
            # Get overridden value from MLEADER
            if attrib_name == "char_height":
                value = self._context.char_height
            else:
                value = self._mleader_dxf.get(attrib_name, value)
        return value

    def is_overridden(self, attrib_name: str) -> bool:
        flag = OVERRIDE_FLAG.get(attrib_name, 0)
        return bool(flag & self._property_override_flags)


def virtual_entities(
    mleader: "MLeader", proxy_graphic=False
) -> List["DXFGraphic"]:
    doc = mleader.doc
    assert doc is not None, "valid DXF document required"
    if proxy_graphic and mleader.proxy_graphic is not None:
        return list(ProxyGraphic(mleader.proxy_graphic, doc).virtual_entities())
    else:
        return RenderEngine(mleader, doc).run()


def get_style(mleader: "MLeader", doc: "Drawing") -> MLeaderStyleOverride:
    handle = mleader.dxf.style_handle
    style = doc.entitydb.get(handle)
    if style is None:
        logger.warning(
            f"referenced MLEADERSTYLE(#{handle}) does not exist, "
            f"replaced by 'Standard'"
        )
        style = doc.mleader_styles.get("Standard")
    assert style is not None, "mandatory MLEADERSTYLE 'Standard' does not exist"
    return MLeaderStyleOverride(cast("MLeaderStyle", style), mleader)


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
    mtext: "MText", mtext_data: "MTextData", scale: float
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
    mtext.dxf.style = get_text_style(mtext_data.style_handle, mtext.doc)
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


def set_mtext_bg_fill(mtext: "MText", mtext_data: "MTextData") -> None:
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
    mtext: "MText", mtext_data: "MTextData", scale: float
) -> None:
    # BricsCAD does not support columns for MTEXT content, so exploring
    # MLEADER with columns was not possible!
    pass


def _get_insert(entity: "MLeader") -> Vec3:
    context = entity.context
    if context.mtext is not None:
        return context.mtext.insert
    elif context.block is not None:
        return context.block.insert
    return context.plane_origin


def _get_extrusion(entity: "MLeader") -> Vec3:
    context = entity.context
    if context.mtext is not None:
        return context.mtext.extrusion
    elif context.block is not None:
        return context.block.extrusion
    return context.plane_z_axis


def _get_dogleg_vector(leader: "LeaderData", default: Vec3 = X_AXIS) -> Vec3:
    # All leader vertices and directions in WCS!
    if leader.has_dogleg_vector:  # what else?
        return leader.dogleg_vector.normalize(leader.dogleg_length)
    return default.normalize(leader.dogleg_length)


def _get_block_layout(handle: str, doc: "Drawing") -> Optional["BlockLayout"]:
    block_record = doc.entitydb.get(handle)
    if block_record is None:
        logger.error(f"required BLOCK_RECORD entity #{handle} does not exist")
        return None
    block_name = block_record.dxf.name
    block_layout = doc.blocks.get(block_name)
    if block_layout is None:
        logger.error(f"required BLOCK definition '{block_name}' does not exist")
    return block_layout


class RenderEngine:
    def __init__(self, mleader: "MLeader", doc: "Drawing"):
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
        # 0= horizontal; 1=vertical - override flag (27) is not set by BricsCAD!
        self.has_horizontal_attachment = not bool(
            mleader.dxf.text_attachment_direction
        )

    @property
    def has_extrusion(self) -> bool:
        return self.ocs is not None

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
        if raw_color is not None:
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
        if self.context.mtext is not None:
            self.add_mtext_content()
        elif self.context.block is not None:
            self.add_block_content()

    def add_mtext_content(self) -> None:
        mtext = cast("MText", factory.new("MTEXT", doc=self.doc))
        mtext.dxf.layer = self.layer
        # !char_height is the final already scaled value!
        mtext.dxf.char_height = self.context.char_height
        mtext_data: "MTextData" = self.context.mtext
        if mtext_data is not None:
            copy_mtext_data(mtext, mtext_data, self.scale)
            if mtext_data.has_bg_fill:
                set_mtext_bg_fill(mtext, mtext_data)
            set_mtext_columns(mtext, mtext_data, self.scale)
        self.entities.append(mtext)
        if self.has_text_frame:
            self.add_text_frame()

    def add_text_frame(self) -> None:
        pass

    def add_block_content(self) -> None:
        block = self.context.block
        block_layout = _get_block_layout(block.block_record_handle, self.doc)
        if block_layout is None:
            return
        aci_color, true_color = decode_raw_color(block.color)
        location = block.insert  # in WCS, really funny for an OCS entity!
        if self.ocs is not None:
            location = self.ocs.from_wcs(location)
        attribs = {
            "name": block_layout.name,
            "insert": location,
            "color": aci_color,
            "extrusion": block.extrusion
        }
        if true_color is not None:
            attribs["true_color"] = true_color
        scale = block.scale
        attribs["xscale"] = scale.x
        attribs["yscale"] = scale.y
        attribs["zscale"] = scale.z

        self.entities.append(
            factory.new("INSERT", dxfattribs=attribs, doc=self.doc)  # type: ignore
        )
        if self.mleader.block_attribs:
            self.add_block_attributes(block_layout)

    def add_block_attributes(self, block_layout: "BlockLayout"):
        pass

    def add_leaders(self) -> None:
        if self.leader_type == 0:
            return

        for leader in self.context.leaders:
            if (
                self.leader_type == 1  # straight lines
                and self.has_dogleg
                and self.has_horizontal_attachment
            ):
                self.add_dogleg(leader)
            for line in leader.lines:
                self.add_leader_line(leader, line)

    def add_dogleg(self, leader: "LeaderData"):
        # All leader vertices and directions in WCS!
        start_point = leader.last_leader_point
        end_point = start_point + leader.dogleg_vector.normalize(
            leader.dogleg_length
        )
        self.add_dxf_line(start_point, end_point)

    def leader_vertices(
        self, leader: "LeaderData", line_vertices: List[Vec3], has_dogleg=False
    ) -> List[Vec3]:
        # All leader vertices and directions in WCS!
        vertices = list(line_vertices)
        end_point = leader.last_leader_point
        if self.has_horizontal_attachment:
            if has_dogleg:
                vertices.append(end_point)
            vertices.append(end_point + _get_dogleg_vector(leader))
        else:
            vertices.append(end_point)
        return vertices

    def add_leader_line(self, leader: "LeaderData", line: "LeaderLine"):
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
        arrow_size: float = self.context.arrowhead_size
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
            if self.has_horizontal_attachment:
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
