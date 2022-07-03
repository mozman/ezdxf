#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING
import pathlib

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import Vec2, NULLVEC, ConstructionBox
from ezdxf.render import forms
from ezdxf.render import mleader

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, BlockLayout

# reserved for further imports, line numbers have to be preserved for
# .. literalinclude::
#
#
#
#
#
#
#
#
# ========================================
# Setup your preferred output directory
# ========================================
CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path()


def create_square_block(
    doc: "Drawing", size: float, margin: float, base_point: Vec2 = NULLVEC
) -> "BlockLayout":
    attribs = GfxAttribs(color=colors.RED)
    block = doc.blocks.new("SQUARE", base_point=base_point)
    block.add_lwpolyline(forms.square(size), close=True, dxfattribs=attribs)

    attdef_attribs = dict(attribs)
    attdef_attribs["height"] = 1.0
    attdef_attribs["style"] = "OpenSans"
    tag = "ONE"
    attdef_attribs["prompt"] = tag
    bottom_left_attdef = block.add_attdef(
        tag, text=tag, dxfattribs=attdef_attribs
    )
    bottom_left_attdef.set_placement(
        (margin, margin), align=TextEntityAlignment.BOTTOM_LEFT
    )
    tag = "TWO"
    attdef_attribs["prompt"] = tag
    top_right_attdef = block.add_attdef(
        tag, text=tag, dxfattribs=attdef_attribs
    )
    top_right_attdef.set_placement(
        (size - margin, size - margin), align=TextEntityAlignment.TOP_RIGHT
    )
    return block


def block_content_horizontal(filename: str):
    base_point = Vec2(1, 2)
    x1, y1, x2, y2 = -20, -20, 40, 20
    construction_box = ConstructionBox.from_points((x1, y1), (x2, y2))

    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    block = create_square_block(
        doc, size=8.0, margin=0.25, base_point=base_point
    )
    ml_builder = msp.add_multileader_block(style="Standard")
    ml_builder.set_content(
        name=block.name, alignment=mleader.BlockAlignment.insertion_point
    )
    ml_builder.set_attribute("ONE", "Data1")
    ml_builder.set_attribute("TWO", "Data2")

    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(x2, y1)])
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(x2, y2)])
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(x1, y1)])
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(x1, y2)])

    ml_builder.build(insert=Vec2(5, 2), rotation=30)

    msp.add_circle(Vec2(5, 2), radius=0.25)  # show the insertion point
    msp.add_lwpolyline(construction_box.corners, close=True)  # draw target box
    doc.set_modelspace_vport(
        construction_box.width, center=construction_box.center
    )
    doc.saveas(CWD / filename)


def block_content_vertical(filename: str):
    base_point = Vec2(1, 2)
    x1, y1, x2, y2 = -20, -20, 40, 20
    construction_box = ConstructionBox.from_points((x1, y1), (x2, y2))

    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    block = create_square_block(
        doc, size=8.0, margin=0.25, base_point=base_point
    )
    ml_builder = msp.add_multileader_block(style="Standard")
    ml_builder.set_content(
        name=block.name, alignment=mleader.BlockAlignment.center_extents
    )
    ml_builder.set_attribute("ONE", "Data1")
    ml_builder.set_attribute("TWO", "Data2")

    ml_builder.add_leader_line(mleader.ConnectionSide.top, [Vec2(x2, y2)])
    ml_builder.add_leader_line(mleader.ConnectionSide.top, [Vec2(x1, y2)])
    ml_builder.add_leader_line(mleader.ConnectionSide.bottom, [Vec2(x1, y1)])
    ml_builder.add_leader_line(mleader.ConnectionSide.bottom, [Vec2(x2, y1)])

    ml_builder.build(insert=Vec2(5, 2))

    msp.add_circle(Vec2(5, 2), radius=0.25)  # show the insertion point
    msp.add_lwpolyline(construction_box.corners, close=True)  # draw target box
    doc.set_modelspace_vport(
        construction_box.width, center=construction_box.center
    )
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    block_content_horizontal("block_content_horizontal.dxf")
    block_content_vertical("block_content_vertical.dxf")
