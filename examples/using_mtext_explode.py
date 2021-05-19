#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import sys
import pathlib
import ezdxf
from ezdxf import zoom
from ezdxf.explode_mtext import MTextExplode

if not ezdxf.options.use_matplotlib:
    print("The Matplotlib package is required.")
    sys.exit(1)

DIR = pathlib.Path('~/Desktop/Outbox').expanduser()

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam " \
              "nonumy eirmod tempor {\C1invidunt ut labore} et dolore mag{\C3na al}iquyam " \
              "erat, sed {\C5diam voluptua.} At vero eos et accusam et justo duo dolores " \
              "et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est " \
              "Lorem ipsum dolor sit amet."
LEFT = LOREM_IPSUM + "\n\n"
CENTER = r"\pxqc;" + LOREM_IPSUM + "\n\n"
RIGHT = r"\pxqr;" + LOREM_IPSUM + "\n\n"
JUSTIFIED = r"\pi1,qj;" + LOREM_IPSUM + "\n\n"


def new_doc(content: str, width: float = 30):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()
    mtext = msp.add_mtext(content, dxfattribs={
        "layer": "MTEXT_EXPLODE",
        "width": width,
        "char_height": 1,
        "color": 7,
        "style": "OpenSans",
        "line_spacing_style": ezdxf.const.MTEXT_EXACT
    })
    mtext.set_bg_color(None, text_frame=True)
    zoom.extents(msp)
    return doc


def explode_mtext(doc, destroy=True):
    msp = doc.modelspace()
    xpl = MTextExplode(msp)
    for mtext in msp.query("MTEXT"):
        xpl.explode(mtext, destroy=destroy)
        if mtext.is_alive:
            mtext.dxf.layer = "SOURCE"
    xpl.finalize()  # create required text styles
    zoom.extents(msp)
    return doc


def create(filename):
    doc = new_doc(LEFT + CENTER + RIGHT + JUSTIFIED)
    doc.saveas(DIR / filename)
    return doc


def load(filename):
    return ezdxf.readfile(DIR / filename)


def explode(doc, filename):
    doc = explode_mtext(doc, destroy=True)
    doc.saveas(DIR / filename)


if __name__ == '__main__':
    doc = create("mtext_source.dxf")
    # doc = load("mtext_source.dxf")
    explode(doc, "mtext_xplode.dxf")
