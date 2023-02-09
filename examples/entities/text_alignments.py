# Copyright (c) 2013-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf import disassemble, options
from ezdxf.enums import TextEntityAlignment

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create all kinds of TEXT alignments.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/text.html
# tutorial: https://ezdxf.mozman.at/docs/tutorials/text.html
# ------------------------------------------------------------------------------


def create_doc(filename):
    def add_justify_text(content, p1, p2, align: TextEntityAlignment):
        msp.add_text(content).set_placement(p1, p2, align)
        msp.add_line(p1, p2)

    def add_grid(pos, width, height):
        attribs = {"height": 0.2, "color": 3}
        x, y = pos
        dx = width / 2
        dy = height / 2
        msp.add_line((x, y), (x, y + height))
        msp.add_line((x + dx, y), (x + dx, y + height))
        msp.add_line((x + width, y), (x + width, y + height))

        msp.add_line((x, y - 1), (x + width, y - 1))
        msp.add_text(
            "BASELINE ADJUSTMENTS (gjpqy)", dxfattribs=attribs
        ).set_placement((x, y - 1.5))
        msp.add_text("LEFT", dxfattribs=attribs).set_placement(
            (x, y - 1), align=TextEntityAlignment.LEFT
        )
        msp.add_text("CENTER", dxfattribs=attribs).set_pos(
            (x + dx, y - 1), align="CENTER"
        )
        msp.add_text("RIGHT", dxfattribs=attribs).set_placement(
            (x + width, y - 1), align=TextEntityAlignment.RIGHT
        )

        attribs["color"] = 2
        msp.add_line((x, y), (x + width, y))
        msp.add_text("BOTTOM_LEFT", dxfattribs=attribs).set_placement(
            (x, y), align=TextEntityAlignment.BOTTOM_LEFT
        )
        msp.add_text("BOTTOM_CENTER_gjpqy", dxfattribs=attribs).set_placement(
            (x + dx, y), align=TextEntityAlignment.BOTTOM_CENTER
        )
        msp.add_text("BOTTOM_RIGHT", dxfattribs=attribs).set_placement(
            (x + width, y), align=TextEntityAlignment.BOTTOM_RIGHT
        )

        y += dy

        msp.add_line((x, y), (x + width, y))
        msp.add_text("MIDDLE_LEFT", dxfattribs=attribs).set_placement(
            (x, y), align=TextEntityAlignment.MIDDLE_LEFT
        )
        msp.add_text("MIDDLE_CENTER_gjpqy", dxfattribs=attribs).set_placement(
            (x + dx, y), align=TextEntityAlignment.MIDDLE_CENTER
        )
        msp.add_text("MIDDLE_RIGHT", dxfattribs=attribs).set_placement(
            (x + width, y), align=TextEntityAlignment.MIDDLE_RIGHT
        )

        y += dy

        msp.add_line((x, y), (x + width, y))
        msp.add_text("TOP_LEFT", dxfattribs=attribs).set_placement(
            (x, y), align=TextEntityAlignment.TOP_LEFT
        )
        msp.add_text("TOP_CENTER_gjpqy", dxfattribs=attribs).set_placement(
            (x + dx, y), align=TextEntityAlignment.TOP_CENTER
        )
        msp.add_text("TOP_RIGHT", dxfattribs=attribs).set_placement(
            (x + width, y), align=TextEntityAlignment.TOP_RIGHT
        )

    doc = ezdxf.new(dxfversion="R2004")
    msp = doc.modelspace()
    add_justify_text(
        "ALIGNED-TEXT-ALIGNED-TEXT-gjpqy-ALIGNED-TEXT-ALIGNED-TEXT",
        (15, 0),
        (35, 5),
        TextEntityAlignment.ALIGNED,
    )
    add_justify_text(
        "FITTED-TEXT-FITTED-TEXT-gjpqy-FITTED-TEXT-FITTED-TEXT",
        (15, 10),
        (35, 5),
        TextEntityAlignment.FIT,
    )
    add_grid((0, 0), width=10, height=10)

    doc.layers.new("INSERT_POINTS")
    draw_insert_points(msp)
    doc.layers.new("BOUNDARIES")
    draw_text_boundaries(msp, True)

    doc.set_modelspace_vport(height=30, center=(15, 0))
    doc.saveas(filename)


def draw_text_boundaries(msp, matplotlib=False):
    # Change Matplotlib support temporarily:
    options.use_matplotlib = matplotlib
    for text in msp.query("TEXT"):
        bbox = disassemble.make_primitive(text)
        msp.add_polyline3d(
            bbox.vertices(),
            dxfattribs={
                "color": 6,
                "layer": "BOUNDARIES",
            },
        )
    # reactivate Matplotlib support, if available:
    options.use_matplotlib = True


def draw_insert_points(msp):
    for text in msp.query("TEXT"):
        msp.add_circle(
            text.dxf.insert,
            radius=0.1,
            dxfattribs={
                "color": 1,
                "layer": "INSERT_POINTS",
            },
        )
        msp.add_circle(
            text.dxf.align_point,
            radius=0.075,
            dxfattribs={
                "color": 2,
                "layer": "INSERT_POINTS",
            },
        )


if __name__ == "__main__":
    create_doc(CWD / "text_alignments.dxf")
