#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib

import colors
import ezdxf
from ezdxf.math import Vec2
from ezdxf.render import mleader
# reserved for further imports, line numbers have to be preserved for
# .. literalinclude::
#

# ========================================
# Setup your preferred output directory
# ========================================
CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path()


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
    doc.saveas(CWD / filename)


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
    doc.saveas(CWD / filename)


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
    doc.saveas(CWD / filename)


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
    doc.saveas(CWD / filename)


def mtext_content_horizontal_connection_types(filename: str):
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
    ml_builder.set_connection_types(
        left=mleader.HorizontalConnection.middle_of_top_line,
        right=mleader.HorizontalConnection.middle_of_bottom_line,
    )
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(CWD / filename)


def mtext_content_spline_left(filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "MText",
        style="OpenSans",
        alignment=mleader.TextAlignment.left,  # set MTEXT alignment!
    )
    ml_builder.set_leader_properties(leader_type=mleader.LeaderType.splines)
    ml_builder.add_leader_line(
        mleader.ConnectionSide.left,
        [Vec2(-20, 15), Vec2(-10, 15), Vec2(-15, 11), Vec2(-10, 7)],
    )
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(CWD / filename)


def mtext_content_leader_properties(filename: str):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "MText",
        style="OpenSans",
        alignment=mleader.TextAlignment.left,  # set MTEXT alignment!
    )
    ml_builder.set_leader_properties(
        color=colors.MAGENTA,
        linetype="DASHEDX2",
        lineweight=70,
    )
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(-20, -15)])
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(CWD / filename)


def mtext_content_arrow_properties(filename: str):
    from ezdxf.render import ARROWS
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    ml_builder = msp.add_multileader_mtext("Standard")
    ml_builder.set_content(
        "MText",
        style="OpenSans",
        alignment=mleader.TextAlignment.left,  # set MTEXT alignment!
    )
    ml_builder.set_arrow_properties(name=ARROWS.closed_blank, size=8.0)
    ml_builder.add_leader_line(mleader.ConnectionSide.left, [Vec2(-20, -15)])
    ml_builder.build(insert=Vec2(5, 0))

    doc.set_modelspace_vport(60, center=(10, 5))
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    mtext_content_horizontal_left("mtext_content_horizontal_left.dxf")
    mtext_content_horizontal_right("mtext_content_horizontal_right.dxf")
    mtext_content_horizontal_left_and_right("mtext_content_horizontal_left_and_right.dxf")
    mtext_content_horizontal_center("mtext_content_horizontal_center.dxf")
    mtext_content_horizontal_connection_types("mtext_content_horizontal_connection_types.dxf")
    mtext_content_spline_left("mtext_content_spline_lef.dxf")
    mtext_content_leader_properties("leader_properties.dxf")
    mtext_content_arrow_properties("arrow_properties.dxf")