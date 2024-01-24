#  Copyright (c) 2020-2023, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf.lldxf import const
from ezdxf.math import Shape2d

def add_top_zero_bottom_mlines(
    msp, vertices, closed: bool = False, style: str = "Standard"
):
    shape = Shape2d(vertices)
    msp.add_mline(
        shape.vertices,
        close=closed,
        dxfattribs={
            "style_name": style,
            "justification": const.MLINE_BOTTOM,
        },
    )
    shape.translate((0, 20, 0))
    msp.add_mline(
        shape.vertices,
        close=closed,
        dxfattribs={
            "style_name": style,
            "justification": const.MLINE_ZERO,
        },
    )
    shape.translate((0, 20, 0))
    msp.add_mline(
        shape.vertices,
        close=closed,
        dxfattribs={
            "style_name": style,
            "justification": const.MLINE_TOP,
        },
    )


def create_simple_mline(style="Standard"):
    doc = ezdxf.new()
    setup_styles(doc)
    msp = doc.modelspace()
    add_top_zero_bottom_mlines(msp, [(0, 0), (10, 0)], style=style)
    doc.set_modelspace_vport(60, center=(10, 30))
    doc.saveas(f"mline_1_seg_{style}.dxf")


def create_3seg_mline(style="Standard"):
    doc = ezdxf.new()
    setup_styles(doc)
    msp = doc.modelspace()
    add_top_zero_bottom_mlines(
        msp, [(0, 0), (10, 0), (15, 5), (15, 10)], style=style
    )
    doc.set_modelspace_vport(60, center=(10, 30))
    doc.saveas(f"mline_3_seg_{style}.dxf")


def create_square_mline(style="Standard"):
    doc = ezdxf.new()
    setup_styles(doc)
    msp = doc.modelspace()
    add_top_zero_bottom_mlines(
        msp, [(0, 0), (10, 0), (10, 10), (0, 10)], closed=True, style=style
    )
    doc.set_modelspace_vport(60, center=(10, 30))
    doc.saveas(f"mline_square_{style}.dxf")


def setup_styles(doc):
    style = doc.mline_styles.new("above")
    style.elements.append(0.5, 1)
    style.elements.append(0.25, 3)
    style = doc.mline_styles.new("below")
    style.elements.append(-0.5, 2)
    style.elements.append(-0.25, 4)
    style = doc.mline_styles.new("angle")
    style.dxf.start_angle = 45
    style.dxf.end_angle = 45
    style.elements.append(0.5, 6)
    style.elements.append(-0.5, 5)
    style = doc.mline_styles.new("everything")
    style.dxf.flags = 0xFFFF
    style.dxf.fill_color = 5
    style.elements.append(1.0, 1)
    style.elements.append(0.25, 6)
    style.elements.append(0.0, 3)
    style.elements.append(-0.25, 4)
    style.elements.append(-0.5, 2)


if __name__ == "__main__":
    for style in ("Standard", "above", "below", "angle", "everything"):
        create_simple_mline(style)
        create_3seg_mline(style)
        create_square_mline(style)
