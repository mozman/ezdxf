#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
import ezdxf
from ezdxf.math import Vec2
from ezdxf.enums import MTextEntityAlignment
from ezdxf.layouts import Modelspace

SIZE_X = 20
SIZE_Y = 20
GAP_X = 5
GAP_Y = 5
CHAR_HEIGHT = 3
TEXT_OFFSET = Vec2(3, 3)
TEXT_COLOR = 255
TEXT_BG_COLOR = (10, 10, 10)
GRADIENT = [9, 7, 5, 3, 1, 0, 2, 4, 6, 8]
ORDERED = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def add_index(msp: Modelspace, location: Vec2, aci: int):
    mtext = msp.add_mtext(
        str(aci),
        dxfattribs={
            "style": "OpenSans",
            "char_height": CHAR_HEIGHT,
            "layer": "TEXT",
        },
    )
    mtext.set_location(
        location + TEXT_OFFSET,
        attachment_point=MTextEntityAlignment.BOTTOM_LEFT,
    )
    mtext.set_bg_color(TEXT_BG_COLOR)


def add_color(msp: Modelspace, location: Vec2, aci: int):
    points = [
        location,
        location + Vec2(SIZE_X, 0),
        location + Vec2(0, SIZE_Y),
        location + Vec2(SIZE_X, SIZE_X),
    ]
    msp.add_solid(points, dxfattribs={"color": aci, "layer": "ACI"})


def add_row(msp: Modelspace, x: int, y: int, colors: list[int]):
    for color in colors:
        location = Vec2(x, y)
        add_color(msp, location, color)
        add_index(msp, location, color)
        x += SIZE_X + GAP_X


def draw_aci_color_table(msp: Modelspace, order: list[int], x: int, y: int):
    add_row(msp, x, y, [1, 2, 3, 4, 5, 6, 7, 8, 9])
    y -= SIZE_Y + GAP_Y
    for start_index in range(10, 250, 10):
        colors = [start_index + offset for offset in order]
        add_row(msp, x, y, colors)
        y -= SIZE_Y + GAP_Y
    add_row(msp, x, y, [250, 251, 252, 253, 254, 255])


def main():
    doc = ezdxf.new()
    doc.styles.add("OpenSans", font="OpenSans-Regular.ttf")
    doc.layers.add("SOLID")
    doc.layers.add("TEXT", color=TEXT_COLOR)
    msp = doc.modelspace()
    draw_aci_color_table(msp, order=ORDERED, x=0, y=700)
    draw_aci_color_table(msp, order=GRADIENT, x=300, y=700)
    doc.set_modelspace_vport(800, center=(300, 400))
    doc.saveas("aci_color_table.dxf")


if __name__ == "__main__":
    main()
