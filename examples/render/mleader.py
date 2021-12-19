#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pathlib
import ezdxf
from ezdxf.math import Vec2, UCS, NULLVEC
import logging
from ezdxf.render.mleader import ConnectionSide, VerticalConnection

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
    ml_builder.add_leader_line(ConnectionSide.right, [Vec2(40, 15)])
    ml_builder.add_leader_line(ConnectionSide.right, [Vec2(40, -15)])
    ml_builder.add_leader_line(ConnectionSide.left, [Vec2(-20, -15)])

    # The insert point (in UCS coordinates= is the alignment point for MTEXT
    # content and the insert location for BLOCK content:
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
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
        top=VerticalConnection.center_overline,
        bottom=VerticalConnection.center_overline,
    )
    ml_builder.add_leader_line(ConnectionSide.top, [Vec2(15, 40)])
    ml_builder.add_leader_line(ConnectionSide.bottom, [Vec2(15, -40)])

    # The insert point (in UCS coordinates= is the alignment point for MTEXT
    # content and the insert location for BLOCK content:
    ml_builder.build(insert=Vec2(5, 0))
    msp.add_circle(
        ml_builder.multileader.context.base_point,
        radius=0.5,
        dxfattribs={"color": ezdxf.colors.RED}
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
        target_point, radius=0.5, dxfattribs={"color": ezdxf.colors.RED}
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
        target_point, radius=0.5, dxfattribs={"color": ezdxf.colors.RED}
    )

    for angle in [45, 135, 225, -45]:
        ml_builder = msp.add_multileader_mtext("EZDXF")
        ml_builder.quick_leader(
            "Line1\nLine2",
            target=target_point,
            segment1=Vec2.from_deg_angle(angle, 14),
            connection_type=VerticalConnection.center_overline,
        )

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


if __name__ == "__main__":
    quick_mtext_horizontal("mleader_quick_mtext_horizontal")
    quick_mtext_vertical("mleader_quick_mtext_vertical")
    simple_mtext_content_horizontal("mleader_simple_mtext_horizontal")
    simple_mtext_content_vertical("mleader_simple_mtext_vertical")
