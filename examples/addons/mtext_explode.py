#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.addons import MTextExplode

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to explode MTEXT entities into TEXT and LINE primitives.
#
# docs: https://ezdxf.mozman.at/docs/addons/mtxpl.html
# ------------------------------------------------------------------------------


LOREM_IPSUM = (
    r"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam "
    r"nonumy eirmod tempor {\C1invidunt ut labore} et dolore mag{\C3na al}iquyam "
    r"erat, sed {\C5diam voluptua.} At vero eos et accusam et justo duo dolores "
    r"et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est "
    r"Lorem ipsum dolor sit amet."
)
LEFT = LOREM_IPSUM + "\n\n"
CENTER = r"\pxqc;" + LOREM_IPSUM + "\n\n"
RIGHT = r"\pxqr;" + LOREM_IPSUM + "\n\n"
JUSTIFIED = r"\pi1,qj;" + LOREM_IPSUM + "\n\n"


def new_doc(content: str, width: float = 30):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    mtext = msp.add_mtext(
        content,
        dxfattribs={
            "layer": "MTEXT_EXPLODE",
            "width": width,
            "char_height": 1,
            "color": 7,
            "style": "OpenSans",
            "line_spacing_style": ezdxf.const.MTEXT_EXACT,
        },
    )
    mtext.set_bg_color(None, text_frame=True)
    zoom.extents(msp)
    return doc


def explode_mtext(doc, filename, destroy=False):
    msp = doc.modelspace()
    with MTextExplode(msp) as xpl:
        for mtext in msp.query("MTEXT"):
            xpl.explode(mtext, destroy=destroy)
            if mtext.is_alive:
                mtext.dxf.layer = "SOURCE"
    zoom.extents(msp)
    doc.saveas(CWD / filename)


def explode_mtext_to_block(doc, filename, destroy=False):
    msp = doc.modelspace()
    blk = doc.blocks.new("EXPLODE")
    with MTextExplode(blk) as xpl:
        for mtext in msp.query("MTEXT"):
            xpl.explode(mtext, destroy=destroy)
            if mtext.is_alive:
                mtext.dxf.layer = "SOURCE"
    msp.add_blockref("EXPLODE", (0, 0))
    zoom.extents(msp)
    doc.saveas(CWD / filename)


def create(filename):
    doc = new_doc(LEFT + CENTER + RIGHT + JUSTIFIED)
    doc.saveas(CWD / filename)
    return doc


def load(filename):
    return ezdxf.readfile(CWD / filename)


if __name__ == "__main__":
    doc = create("mtext_source.dxf")
    explode_mtext_to_block(doc, "mtext_xpl_blk.dxf", destroy=True)
    # doc = load("mtext_tab_stops.dxf")
    # explode_mtext(doc, "mtext_xpl_tabs.dxf", destroy=False)
