# Copyright (c) 2013-2021, Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.enums import TextEntityAlignment


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
        msp.add_text("BASELINE ADJUSTMENTS", dxfattribs=attribs).set_placement(
            (x, y - 1.5)
        )
        msp.add_text("LEFT", dxfattribs=attribs).set_placement(
            (x, y - 1), align=TextEntityAlignment.LEFT
        )
        msp.add_text("CENTER", dxfattribs=attribs).set_placement(
            (x + dx, y - 1), align=TextEntityAlignment.CENTER
        )
        msp.add_text("RIGHT", dxfattribs=attribs).set_placement(
            (x + width, y - 1), align=TextEntityAlignment.RIGHT
        )

        attribs["color"] = 2
        msp.add_line((x, y), (x + width, y))
        msp.add_text("BOTTOM_LEFT", dxfattribs=attribs).set_placement(
            (x, y), align=TextEntityAlignment.BOTTOM_LEFT
        )
        msp.add_text("BOTTOM_CENTER", dxfattribs=attribs).set_placement(
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
        msp.add_text("MIDDLE_CENTER", dxfattribs=attribs).set_placement(
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
        msp.add_text("TOP_CENTER", dxfattribs=attribs).set_placement(
            (x + dx, y), align=TextEntityAlignment.TOP_CENTER
        )
        msp.add_text("TOP_RIGHT", dxfattribs=attribs).set_placement(
            (x + width, y), align=TextEntityAlignment.TOP_RIGHT
        )

    def show_insert_points(msp):
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

    def shift_insert_point(msp):
        for text in msp.query("TEXT"):
            text.dxf.insert += (1, 1)

    doc = ezdxf.new(dxfversion="R2004")
    msp = doc.modelspace()
    add_grid((0, 0), width=10, height=10)
    # shift_insert_point(msp)

    add_justify_text(
        "ALIGNED-TEXT-ALIGNED-TEXT-ALIGNED-TEXT-ALIGNED-TEXT",
        (15, 0),
        (35, 5),
        TextEntityAlignment.ALIGNED,
    )
    add_justify_text(
        "FITTED-TEXT-FITTED-TEXT-FITTED-TEXT-FITTED-TEXT",
        (15, 10),
        (35, 5),
        TextEntityAlignment.FIT,
    )
    add_justify_text("MIDDLE", (15, 15), (35, 10), TextEntityAlignment.MIDDLE)
    show_insert_points(msp)

    doc.set_modelspace_vport(height=30, center=(15, 0))
    doc.saveas(filename)


if __name__ == "__main__":
    create_doc("text_alignments.dxf")
