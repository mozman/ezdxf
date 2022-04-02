#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import ezdxf
from ezdxf.math import Vec2
from ezdxf.render import mleader
# reserved for further imports, line numbers have to be preserved for
# .. literalinclude::
#
#
#
#

# ========================================
# Setup your preferred output directory
# ========================================
OUTDIR = pathlib.Path("~/Desktop/Outbox").expanduser()
if not OUTDIR.exists():
    OUTDIR = pathlib.Path()


def mtext_content_horizontal_left(filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "Line1\nLine2",
        style="OpenSans",
        alignment=mleader.TextAlignment.left,  # set MTEXT alignment!
    )
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(-20, -15)])
    ml_builder.add_leader_line(
        mleader.ConnectionSide.left,
        [Vec2(-20, 15), Vec2(-10, 15), Vec2(-15, 11), Vec2(-10, 7)],
    )
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / filename)


def mtext_content_horizontal_right(filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "Line1\nLine2",
        style="OpenSans",
        alignment=mleader.TextAlignment.right,  # set MTEXT alignment!
    )
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(40, -15)])
    ml_builder.build(insert=Vec2(15, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / filename)


def mtext_content_horizontal_left_and_right(filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "Line1\nLine1",
        style="OpenSans",
        alignment=mleader.TextAlignment.left,  # set MTEXT alignment!
    )
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(-20, -15)])
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(40, -15)])
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / filename)


def mtext_content_horizontal_center(filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "First Line\n2. Line",
        style="OpenSans",
        alignment=mleader.TextAlignment.center,  # set MTEXT alignment!
    )
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(-20, -15)])
    ml_builder.add_leader_line(mleader.ConnectionSide.right, [Vec2(40, -15)])
    ml_builder.build(insert=Vec2(10, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(OUTDIR / filename)


if __name__ == "__main__":
    mtext_content_horizontal_left("mtext_content_horizontal_left.dxf")
    mtext_content_horizontal_right("mtext_content_horizontal_right.dxf")
    mtext_content_horizontal_left_and_right("mtext_content_horizontal_left_and_right.dxf")
    mtext_content_horizontal_center("mtext_content_horizontal_center.dxf")
