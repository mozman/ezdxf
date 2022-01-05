#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING
import pathlib
import logging

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.math import Vec2, UCS, NULLVEC, ConstructionBox
from ezdxf.render import forms, mleader

if TYPE_CHECKING:
    from ezdxf.eztypes import Drawing, BlockLayout

# ========================================
# Setup logging
# ========================================
logging.basicConfig(level="WARNING")

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()

DXFVERSION = "R2013"


def simple_mtext_content_horizontal(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content("Line1\nLine2", style="OpenSans")

    # Construction plane of the entity is defined by an render UCS.
    # The default render UCS is the WCS.
    # The leader lines vertices are expected in render UCS coordinates, which
    # means relative to the UCS origin!
    # This example shows the simplest way UCS==WCS!
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(40, 15)])
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(40, -15)])
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(-20, -15)])

    # The insert point (in UCS coordinates= is the alignment point for MTEXT
    # content and the insert location for BLOCK content:
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def all_mtext_content_horizontal(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    attribs = GfxAttribs(color=colors.RED)
    for direction in range(9):
        for ax, alignment in enumerate(
            [
                mleader.TextAlignment.left,
                mleader.TextAlignment.center,
                mleader.TextAlignment.right,
            ]
        ):
            ml_builder = msp.add_multileader_mtext("Standard")
            dir_enum = mleader.HorizontalConnection(direction)
            ml_builder.set_connection_types(
                left=dir_enum,
                right=dir_enum,
            )

            ml_builder.set_content(
                f"{dir_enum.name}\n{dir_enum.name}\n{dir_enum.name}",
                alignment=alignment,
                style="OpenSans",
            )
            width = len(dir_enum.name) * 2.5
            x0 = -30
            x1 = 40 + width
            y0 = -15
            y1 = 20

            ml_builder.add_leader_line(
                mleader.ConnectionSide.right, [Vec2(x1, y1)]
            )
            ml_builder.add_leader_line(
                mleader.ConnectionSide.right, [Vec2(x1, y0)]
            )
            ml_builder.add_leader_line(
                mleader.ConnectionSide.left, [Vec2(x0, y0)]
            )
            ml_builder.add_leader_line(
                mleader.ConnectionSide.left, [Vec2(x0, y1)]
            )
            x = 5
            if alignment == mleader.TextAlignment.center:
                x += width / 2
            elif alignment == mleader.TextAlignment.right:
                x += width
            ucs = UCS(origin=(ax * 250, direction * 50))
            insert = Vec2(x, y1 / 2)
            ml_builder.build(insert=insert, ucs=ucs)
            e = msp.add_lwpolyline(
                [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                close=True,
                dxfattribs=attribs,
            )
            e.transform(ucs.matrix)
            e = msp.add_circle(insert, radius=0.5, dxfattribs=attribs)
            e.transform(ucs.matrix)

    height = 600
    doc.set_modelspace_vport(height, center=(200, height / 2))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def simple_mtext_content_vertical(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content("Line1\nLine2", style="OpenSans")

    # Construction plane of the entity is defined by an render UCS.
    # The default render UCS is the WCS.
    # The leader lines vertices are expected in render UCS coordinates, which
    # means relative to the UCS origin!
    # This example shows the simplest way UCS==WCS!
    ml_builder.set_connection_types(
        top=mleader.VerticalConnection.center_overline,
        bottom=mleader.VerticalConnection.center_overline,
    )
    ml_builder.add_leader_line(mleader.ConnectionSide.top, [Vec2(15, 40)])
    ml_builder.add_leader_line(mleader.ConnectionSide.bottom, [Vec2(15, -40)])

    # The insert point (in UCS coordinates= is the alignment point for MTEXT
    # content and the insert location for BLOCK content:
    ml_builder.build(insert=Vec2(5, 0))
    msp.add_circle(
        ml_builder.multileader.context.base_point,
        radius=0.5,
        dxfattribs=GfxAttribs(color=colors.RED),
    )
    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def quick_mtext_horizontal(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    mleaderstyle = doc.mleader_styles.duplicate_entry("Standard", "EZDXF")
    mleaderstyle.set_mtext_style("OpenSans")  # type: ignore
    msp = doc.modelspace()
    target_point = Vec2(40, 15)
    msp.add_circle(
        target_point, radius=0.5, dxfattribs=GfxAttribs(color=colors.RED)
    )

    for angle in [45, 135, 225, -45]:
        ml_builder = msp.add_multileader_mtext("EZDXF")
        ml_builder.quick_leader(
            "Line1\nLine2",
            target=target_point,
            segment1=Vec2.from_deg_angle(angle, 14),
        )

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def quick_mtext_vertical(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    mleaderstyle = doc.mleader_styles.duplicate_entry("Standard", "EZDXF")
    mleaderstyle.set_mtext_style("OpenSans")  # type: ignore
    msp = doc.modelspace()
    target_point = Vec2(40, 15)
    msp.add_circle(
        target_point, radius=0.5, dxfattribs=GfxAttribs(color=colors.RED)
    )

    for angle in [45, 135, 225, -45]:
        ml_builder = msp.add_multileader_mtext("EZDXF")
        ml_builder.quick_leader(
            "Line1\nLine2",
            target=target_point,
            segment1=Vec2.from_deg_angle(angle, 14),
            connection_type=mleader.VerticalConnection.center_overline,
        )

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def create_block(
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


def block_content_horizontal(
    name: str,
    align: mleader.BlockAlignment,
    base_point=Vec2(0, 0),
    block_scale=1.0,
    block_rotation=0.0,
    overall_scale=1.0,
):
    x1, y1, x2, y2 = -40, -40, 60, 40
    construction_box = ConstructionBox.from_points((x1, y1), (x2, y2))

    doc = ezdxf.new(DXFVERSION, setup=True)
    block = create_block(doc, size=8.0, margin=0.25, base_point=base_point)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_block(style="Standard")
    ml_builder.set_content(name=block.name, alignment=align, scale=block_scale)
    ml_builder.set_overall_scaling(overall_scale)
    ml_builder.set_attribute("ONE", "Data1")
    ml_builder.set_attribute("TWO", "Data2")

    # Construction plane of the entity is defined by an render UCS.
    # The default render UCS is the WCS.
    # The leader lines vertices are expected in render UCS coordinates, which
    # means relative to the UCS origin!
    # This example shows the simplest way UCS==WCS!
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(x2, y1)])
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(x2, y2)])
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(x1, y1)])
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(x1, y2)])

    # The insert point (in UCS coordinates is the insert location for BLOCK
    # content:
    insert = Vec2(5, 2)
    ml_builder.build(insert=insert, rotation=block_rotation)

    # visual additions:
    msp.add_circle(insert, radius=0.25)  # show the insertion point
    msp.add_lwpolyline(construction_box.corners, close=True)  # draw target box
    doc.set_modelspace_vport(
        construction_box.width, center=construction_box.center
    )
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def block_content_vertical(
    name: str,
    align: mleader.BlockAlignment,
    base_point=Vec2(0, 0),
    block_scale=1.0,
    block_rotation=0.0,
    overall_scale=1.0,
):
    x1, y1, x2, y2 = -30, -30, 30, 30
    construction_box = ConstructionBox.from_points((x1, y1), (x2, y2))

    doc = ezdxf.new(DXFVERSION, setup=True)
    block = create_block(doc, size=8.0, margin=0.25, base_point=base_point)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_block(style="Standard")
    ml_builder.set_content(
        name=block.name, alignment=align, scale=block_scale
    )  # block scale
    ml_builder.set_overall_scaling(overall_scale)
    ml_builder.set_attribute("ONE", "Data1")
    ml_builder.set_attribute("TWO", "Data2")
    ml_builder.add_leader_line(mleader.ConnectionSide.top, [Vec2(x1, y2)])
    ml_builder.add_leader_line(mleader.ConnectionSide.top, [Vec2(x2, y2)])
    ml_builder.add_leader_line(mleader.ConnectionSide.bottom, [Vec2(x1, y1)])
    ml_builder.add_leader_line(mleader.ConnectionSide.bottom, [Vec2(x2, y1)])

    # The insert point (in UCS coordinates= is the insert location for BLOCK
    # content:
    insert = Vec2(5, 2)
    ml_builder.build(insert=insert, rotation=block_rotation)

    # visual additions:
    msp.add_circle(insert, radius=0.25)  # show the insertion point
    msp.add_lwpolyline(construction_box.corners, close=True)  # draw target box
    doc.set_modelspace_vport(
        construction_box.width, center=construction_box.center
    )
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


def make_template(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    create_block(doc, size=8.0, margin=0.25)
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


if __name__ == "__main__":
    make_template("brics_block")
    # quick_mtext_horizontal("mleader_quick_mtext_horizontal")
    # quick_mtext_vertical("mleader_quick_mtext_vertical")
    # simple_mtext_content_horizontal("mleader_simple_mtext_horizontal")
    # simple_mtext_content_vertical("mleader_simple_mtext_vertical")
    # all_mtext_content_horizontal("mleader_all_mtext_horizontal")

    # only block scaling - dogleg_length and arrow_size is not affected
    block_content_horizontal(
        "horizontal_block_x2_center_extents",
        mleader.BlockAlignment.center_extents,
        base_point=Vec2(1, 2),
        block_scale=2,
        block_rotation=30,
    )
    # only block scaling - dogleg_length and arrow_size is not affected
    block_content_horizontal(
        "horizontal_block_center_extents_all_x2",
        mleader.BlockAlignment.center_extents,
        base_point=Vec2(1, 2),
        overall_scale=2,
        block_rotation=30,
    )

    block_content_horizontal(
        "horizontal_block_x2_insertion_point",
        mleader.BlockAlignment.insertion_point,
        base_point=Vec2(1, 2),
        block_scale=2,
        block_rotation=30,
    )
    block_content_horizontal(
        "horizontal_block_insertion_point_all_x2",
        mleader.BlockAlignment.insertion_point,
        base_point=Vec2(1, 2),
        block_scale=2,
        block_rotation=30,
    )
    block_content_vertical(
        "vertical_block_center_extents",
        mleader.BlockAlignment.center_extents,
        block_rotation=30,
        base_point=Vec2(1, 2),
    )
    block_content_vertical(
        "vertical_block_insertion_point",
        mleader.BlockAlignment.insertion_point,
        block_rotation=30,
        base_point=Vec2(1, 2),
    )
