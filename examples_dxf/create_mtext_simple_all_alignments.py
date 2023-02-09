#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import ezdxf
from ezdxf.math import Vec3
from ezdxf.enums import MTextEntityAlignment

# This is the only way to create MTEXT entities where the "width" attribute
# is missing or equals 0.
# MTEXT entities created by AutoCAD or BricsCAD ALWAYS have a
# "width" attribute > 0.

CONTENT = "This is a long MTEXT line without line wrapping!\\PThe second line."

doc = ezdxf.new(setup=True)
doc.layers.new("MTEXT", dxfattribs={"color": ezdxf.const.RED})
msp = doc.modelspace()
attribs = {
    "char_height": 0.7,
    "style": "OpenSans",
    "layer": "MTEXT",
}


def add_mtext(
    location: Vec3, attachment_point: MTextEntityAlignment, size: float = 2
):
    msp.add_line(location - (size, 0), location + (size, 0))
    msp.add_line(location - (0, size), location + (0, size))
    mtext = msp.add_mtext(CONTENT, attribs)
    mtext.set_location(location, attachment_point=attachment_point)


params = [
    ((0, 0), MTextEntityAlignment.BOTTOM_LEFT),
    ((100, 0), MTextEntityAlignment.BOTTOM_CENTER),
    ((200, 0), MTextEntityAlignment.BOTTOM_RIGHT),
    ((0, 100), MTextEntityAlignment.MIDDLE_LEFT),
    ((100, 100), MTextEntityAlignment.MIDDLE_CENTER),
    ((200, 100), MTextEntityAlignment.MIDDLE_RIGHT),
    ((0, 200), MTextEntityAlignment.TOP_LEFT),
    ((100, 200), MTextEntityAlignment.TOP_CENTER),
    ((200, 200), MTextEntityAlignment.TOP_RIGHT),
]

for location, attachment_point in params:
    add_mtext(Vec3(location), attachment_point)

doc.set_modelspace_vport(300, (100, 100))
doc.saveas("mtext_simple_all_alignments.dxf")
