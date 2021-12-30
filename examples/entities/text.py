# Copyright (c) 2013-2021, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf import disassemble, options
from ezdxf.enums import TextEntityAlignment
DIR = Path("~/Desktop/Outbox").expanduser()


def create_doc(filename):
    def add_justify_text(content, p1, p2, align):
        msp.add_text(content).set_pos(p1, p2, align)
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
        ).set_pos((x, y - 1.5))
        msp.add_text("LEFT", dxfattribs=attribs).set_pos(
            (x, y - 1), align="LEFT"
        )
        msp.add_text("CENTER", dxfattribs=attribs).set_pos(
            (x + dx, y - 1), align="CENTER"
        )
        msp.add_text("RIGHT", dxfattribs=attribs).set_pos(
            (x + width, y - 1), align="RIGHT"
        )

        attribs["color"] = 2
        msp.add_line((x, y), (x + width, y))
        msp.add_text("BOTTOM_LEFT", dxfattribs=attribs).set_pos(
            (x, y), align="BOTTOM_LEFT"
        )
        msp.add_text("BOTTOM_CENTER_gjpqy", dxfattribs=attribs).set_pos(
            (x + dx, y), align="BOTTOM_CENTER"
        )
        msp.add_text("BOTTOM_RIGHT", dxfattribs=attribs).set_pos(
            (x + width, y), align="BOTTOM_RIGHT"
        )

        y += dy

        msp.add_line((x, y), (x + width, y))
        msp.add_text("MIDDLE_LEFT", dxfattribs=attribs).set_pos(
            (x, y), align="MIDDLE_LEFT"
        )
        msp.add_text("MIDDLE_CENTER_gjpqy", dxfattribs=attribs).set_pos(
            (x + dx, y), align="MIDDLE_CENTER"
        )
        msp.add_text("MIDDLE_RIGHT", dxfattribs=attribs).set_pos(
            (x + width, y), align="MIDDLE_RIGHT"
        )

        y += dy

        msp.add_line((x, y), (x + width, y))
        msp.add_text("TOP_LEFT", dxfattribs=attribs).set_pos(
            (x, y), align="TOP_LEFT"
        )
        msp.add_text("TOP_CENTER_gjpqy", dxfattribs=attribs).set_pos(
            (x + dx, y), align="TOP_CENTER"
        )
        msp.add_text("TOP_RIGHT", dxfattribs=attribs).set_pos(
            (x + width, y), align="TOP_RIGHT"
        )

    doc = ezdxf.new(dxfversion="R2004")
    msp = doc.modelspace()
    add_justify_text(
        "ALIGNED-TEXT-ALIGNED-TEXT-gjpqy-ALIGNED-TEXT-ALIGNED-TEXT",
        (15, 0),
        (35, 5),
        "ALIGNED",
    )
    add_justify_text(
        "FITTED-TEXT-FITTED-TEXT-gjpqy-FITTED-TEXT-FITTED-TEXT",
        (15, 10),
        (35, 5),
        "FIT",
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
    # Reactive Matplotlib support, if available:
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
    create_doc(DIR / "text_alignments.dxf")
