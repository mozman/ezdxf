# Copyright (c) 2022-2023, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import text2path
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.fonts import fonts
from ezdxf.math import Matrix44
from ezdxf import zoom, path
from ezdxf.render import hatching

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to render text as HATCH entities by the text2path add-on.
#
# docs:
# text2path add-on: https://ezdxf.mozman.at/docs/addons/text2path.html
# hatching module: https://ezdxf.mozman.at/docs/render/hatching.html
# ------------------------------------------------------------------------------

SAMPLE_STRING = "Sample Text: 1234567890 abc ABC"
FONT = fonts.FontFace(family="Arial")


def text_to_solid_filling():
    doc = ezdxf.new()
    msp = doc.modelspace()

    hatches = text2path.make_hatches_from_str(
        SAMPLE_STRING, font=FONT, size=4, m=Matrix44.translate(2, 1.5, 0)
    )
    for hatch in hatches:
        # style: 0 = normal; 1 = outer; 2 = ignore
        hatch.set_solid_fill(color=1, style=0)
        msp.add_entity(hatch)

    zoom.extents(msp)
    doc.saveas(CWD / "text2solid.dxf")


def text_to_predefined_pattern():
    doc = ezdxf.new()
    msp = doc.modelspace()

    hatches = text2path.make_hatches_from_str(
        SAMPLE_STRING, font=FONT, size=4, m=Matrix44.translate(2, 1.5, 0)
    )
    for hatch in hatches:
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

    m = Matrix44.translate(2, 1.5, 0)
    hatches = text2path.make_hatches_from_str(
        SAMPLE_STRING, font=FONT, size=4, m=m
    )
    # ANSI31 definition: [angle, base_point, offset, dash_length_items]
    # "ANSI31": [[45.0, (0.0, 0.0), (-2.2450640303, 2.2450640303), []]]
    offset = (0, 0.05)  # (x, y) offset in drawing units
    continuous = []
    dashed = [0.5, -0.3]  # > 0 line, < 0 gap, 0 = point
    MY_PATTERN = [
        [0.0, (0.0, 0.0), offset, continuous],  # a single hatch line definition
    ]

    for hatch in hatches:
        hatch.set_pattern_fill(
            name="MY_PATTERN",
            color=1,
            style=0,  # 0 = normal; 1 = outer; 2 = ignore
            pattern_type=2,  # 0 = user-defined; 1 = predefined; 2 = custom
            # I have no idea what the difference between a user-defined pattern
            # type and a custom pattern type is, both values work for this example.
            definition=MY_PATTERN,
        )
        msp.add_entity(hatch)

    # optional: add outline to text
    outlines = text2path.make_paths_from_str(
        SAMPLE_STRING, font=FONT, size=4, m=m
    )
    path.render_splines_and_polylines(
        msp, outlines, dxfattribs=GfxAttribs(color=ezdxf.colors.YELLOW)
    )

    zoom.extents(msp)
    doc.saveas(CWD / "text2custom_pattern.dxf")


def render_hatch_entities():
    doc = ezdxf.new()
    msp = doc.modelspace()

    hatches = text2path.make_hatches_from_str(SAMPLE_STRING, font=FONT, size=4)
    offset = (0, 0.05)  # (x, y) offset in drawing units
    # The hatching algorithm has some issues when pattern lines are coincident
    # to HATCH boundary lines, shifting the origin of the pattern slightly by an
    # arbitrary small amount may prevent such problems:
    origin = (0.00142387564, 0.0067462384)
    MY_PATTERN = [[0.0, origin, offset, []]]

    for hatch in hatches:
        hatch.set_pattern_fill(
            name="MY_PATTERN",
            color=1,
            style=0,  # 0 = normal; 1 = outer; 2 = ignore
            pattern_type=2,  # 0 = user-defined; 1 = predefined; 2 = custom
            # I have no idea what the difference between a user-defined pattern
            # type and a custom pattern type is, both values work for this example.
            definition=MY_PATTERN,
        )
        # Adding LINE entities to the modelspace instead of HATCH entities:
        attribs = GfxAttribs(color=ezdxf.colors.RED)
        for start, end in hatching.hatch_entity(hatch):
            msp.add_line(start, end, dxfattribs=attribs)

    zoom.extents(msp)
    doc.saveas(CWD / "text2lines.dxf")


if __name__ == "__main__":
    text_to_solid_filling()
    text_to_predefined_pattern()
    text_to_custom_pattern()
    render_hatch_entities()
