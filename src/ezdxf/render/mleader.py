#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Any, cast, List
import logging

from ezdxf import colors
from ezdxf.lldxf import const
from ezdxf.math import Vec3, Z_AXIS
from ezdxf.entities import factory
from ezdxf.proxygraphic import ProxyGraphic

if TYPE_CHECKING:
    from ezdxf.entities import (
        MLeader,
        MLeaderStyle,
        DXFGraphic,
        MText,
        Insert,
        Attrib,
        Line,
        Spline,
        Textstyle,
    )
    from ezdxf.document import Drawing

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
    "text_attachment_direction": 1 << 27,
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
            value = self._style_dxf.get(attrib_name)
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
    entities: List["DXFGraphic"] = list()
    if proxy_graphic and mleader.proxy_graphic is not None:
        entities.extend(
            ProxyGraphic(mleader.proxy_graphic, doc).virtual_entities()
        )
    else:
        engine = RenderEngine(mleader, doc)
        entities.extend(engine.build_content())
        entities.extend(engine.build_leaders())
    return entities


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


ACI_COLOR_TYPES = {
    colors.COLOR_TYPE_BY_BLOCK,
    colors.COLOR_TYPE_BY_LAYER,
    colors.COLOR_TYPE_ACI,
}


def set_mtext_color(mtext: "MText", raw_color: int) -> None:
    color_type, color = colors.decode_raw_color(raw_color)
    if color_type in ACI_COLOR_TYPES:
        mtext.dxf.color = color
    elif color_type == colors.COLOR_TYPE_RGB:
        # shortcut for mtext.rgb = color
        mtext.dxf.true_color = raw_color & 0xffffff
    else:
        mtext.dxf.color = const.BYBLOCK  # set default color
    # colors.COLOR_TYPE_WINDOW_BG: not supported for text color


class RenderEngine:
    def __init__(self, mleader: "MLeader", doc: "Drawing"):
        self.mleader = mleader
        self.doc = doc
        self.style: MLeaderStyleOverride = get_style(mleader, doc)
        self.context = mleader.context
        # Gather final parameters from various places:
        # Ignore MLeaderStyleOverride at all?
        self.scale: float = self.context.scale  # ignore scale in style?
        self.layer = mleader.dxf.layer

    @property
    def has_text_frame(self) -> bool:
        return False

    def build_content(self) -> List["DXFGraphic"]:
        context = self.mleader.context
        # also check self.style.get("content_type") ?
        if context.mtext is not None:
            return self.build_mtext_content()
        elif context.block is not None:
            return self.build_block_content()
        return []

    def build_mtext_content(self) -> List["DXFGraphic"]:
        # BricsCAD does not support columns in MTEXT content, so exploring
        # MLEADER with columns was not possible!
        mtext = cast("MText", factory.new("MTEXT", doc=self.doc))
        dxf = mtext.dxf
        dxf.layer = self.layer
        mctx = self.context.mtext
        if mctx is not None:
            # What else could be used as MTEXT content?
            mtext.text = mctx.default_content

            dxf.style = get_text_style(mctx.style_handle, self.doc)
            dxf.insert = mctx.insert
            if not mctx.extrusion.isclose(Z_AXIS):
                dxf.extrusion = mctx.extrusion
            dxf.text_direction = mctx.text_direction
            # ignore rotation!
            dxf.char_height = self.context.char_height
            dxf.width = mctx.rect_width
            dxf.line_spacing_factor = mctx.line_spacing_factor
            dxf.line_spacing_style = mctx.line_spacing_style
            dxf.flow_direction = mctx.flow_direction
            set_mtext_color(mtext, mctx.color)  # set raw color value

            # alignment=attachment_point: 1=top left, 2=top center, 3=top right
            dxf.attachment_point = mctx.alignment

            # todo: background color, columns

        content = [mtext]
        if self.has_text_frame:
            content.extend(self.build_text_frame())
        return content

    def build_text_frame(self) -> List["DXFGraphic"]:
        return []

    def build_block_content(self) -> List["DXFGraphic"]:
        blkref = cast("Insert", factory.new("INSERT", doc=self.doc))
        return [blkref]

    def build_leaders(self) -> List["DXFGraphic"]:
        return []
