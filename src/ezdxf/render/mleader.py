#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Any
from ezdxf.math import Vec3

if TYPE_CHECKING:
    from ezdxf.entities import MLeader, MLeaderStyle

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
    "text_height": 1 << 16,  # ??? not in MLeader
    "has_text_frame": 1 << 17,
    "unknown": 1 << 18,  # ??? Enable use of default MTEXT (from MLEADERSTYLE)
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
    def __init__(self, style: "MLeaderStyle", leader: "MLeader"):
        self._style_dxf = style.dxf
        self._leader_dxf = leader.dxf
        self._property_override_flags = leader.dxf.get(
            "property_override_flags", 0
        )
        self._block_scale_vector = Vec3((
               style.dxf.get("block_scale_x", 1.0),
               style.dxf.get("block_scale_y", 1.0),
               style.dxf.get("block_scale_z", 1.0),
        ))

    def get(self, attrib_name: str) -> Any:
        if attrib_name == "block_scale_vector":
            value = self._block_scale_vector
        else:
            value = self._style_dxf.get(attrib_name)
        if self.is_overridden(attrib_name):
            value = self._leader_dxf.get(attrib_name, value)
        return value

    def is_overridden(self, attrib_name: str) -> bool:
        flag = OVERRIDE_FLAG.get(attrib_name, 0)
        return bool(flag & self._property_override_flags)
