# Copyright (c) 2022, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.addons import text2path
from ezdxf.tools import fonts
from ezdxf.math import Matrix44
from ezdxf import zoom

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")

# ------------------------------------------------------------------------------
# This example shows how to render text as HATCH entities by the text2path add-on.
#
# docs: https://ezdxf.mozman.at/docs/addons/text2path.html
# ------------------------------------------------------------------------------

SAMPLE_STRING = "Sample Text: 1234567890 abc ABC"
FONT = fonts.FontFace(family="Arial")


def text_to_solid_filling():
    doc = ezdxf.new()
    msp = doc.modelspace()

    hatches = text2path.make_hatches_from_str(SAMPLE_STRING, font=FONT, size=4)
    m = Matrix44.translate(2, 1.5, 0)
    for hatch in hatches:
        hatch.transform(m)
        # style: 0 = normal; 1 = outer; 2 = ignore
        hatch.set_solid_fill(color=1, style=0)
        msp.add_entity(hatch)

    zoom.extents(msp)
    doc.saveas(CWD / "text2solid.dxf")


def text_to_predefined_pattern():
    doc = ezdxf.new()
    msp = doc.modelspace()

    hatches = text2path.make_hatches_from_str(SAMPLE_STRING, font=FONT, size=4)
    m = Matrix44.translate(2, 1.5, 0)
    for hatch in hatches:
        hatch.transform(m)
        # style: 0 = normal; 1 = outer; 2 = ignore
        hatch.set_pattern_fill(
            name="ANSI31", color=1, scale=0.02, angle=-45, style=0
        )
        msp.add_entity(hatch)

    zoom.extents(msp)
    doc.saveas(CWD / "text2ansi31.dxf")


def text_to_custom_pattern():
    doc = ezdxf.new()
    msp = doc.modelspace()

    hatches = text2path.make_hatches_from_str(SAMPLE_STRING, font=FONT, size=4)
    m = Matrix44.translate(2, 1.5, 0)
    # ANSI31 definition: [angle, base_point, offset, dash_length_items]
    # "ANSI31": [[45.0, (0.0, 0.0), (-2.2450640303, 2.2450640303), []]]
    OFFSET = (0, 0.05)  # (x, y) offset in drawing units
    SOLID = []  # continuous line
    DASHED = [0.5, -0.3]  # > 0 line, < 0 gap, 0 = point
    MY_PATTERN = [
        [0.0, (0.0, 0.0), OFFSET, SOLID],  # a single hatch line definition
    ]

    for hatch in hatches:
        hatch.transform(m)
        hatch.set_pattern_fill(
            name="MY_PATTERN",
            color=1,
            style=0,  # 0 = normal; 1 = outer; 2 = ignore
            pattern_type=2,  # 0 = user-defined; 1 = predefined; 2 = custom
            # I have no idea what the difference between a user-defined pattern
            # type and custom pattern type is, both values work for this example.
            definition=MY_PATTERN,
        )
        msp.add_entity(hatch)

    zoom.extents(msp)
    doc.saveas(CWD / "text2custom_pattern.dxf")


if __name__ == "__main__":
    text_to_solid_filling()
    text_to_predefined_pattern()
    text_to_custom_pattern()
