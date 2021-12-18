#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pathlib
import ezdxf
from ezdxf.math import Vec2, UCS, NULLVEC
import logging
from ezdxf.render.mleader import ConnectionSide

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


def simple_mtext_content(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader("Standard")
    ml_builder.set_mtext_content("Line1\nLine2", style="OpenSans")

    # Construction plane of the entity is defined by an render UCS.
    # The default render UCS is the WCS.
    # The leader lines vertices are expected in render UCS coordinates, which
    # means relative to the UCS origin!
    # This example shows the simplest way UCS==WCS!
    ml_builder.add_leader_line(ConnectionSide.right, [(40, 15)])
    ml_builder.add_leader_line(ConnectionSide.right, [(40, -15)])
    ml_builder.add_leader_line(ConnectionSide.left, [(-20, -15)])

    # The insert point (in UCS coordinates= is the alignment point for MTEXT
    # content and the insert location for BLOCK content:
    ml_builder.build(insert=(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")

    # Rotation of the MULTILEADER entity can only be achieved by rotating the
    # UCS or transform the whole entity after creation, this is shown in
    # another example.


def quick_mtext(name: str):
    doc = ezdxf.new(DXFVERSION, setup=True)
    mleaderstyle = doc.mleader_styles.duplicate_entry("Standard", "EZDXF")
    mleaderstyle.set_mtext_style("OpenSans")  # type: ignore
    msp = doc.modelspace()
    ml_builder = msp.add_multileader("EZDXF")
    ml_builder.quick_mtext(
        "Line1\nLine2",
        target=Vec2(40, 15),
        segment1=Vec2(-10, -10)
    )
    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / f"{name}_{DXFVERSION}.dxf")


if __name__ == "__main__":
    quick_mtext("mleader_quick_mtext")
    simple_mtext_content("mleader_simple_mtext")

