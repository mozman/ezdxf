#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest
import ezdxf
from ezdxf.addons import MTextExplode

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
    return doc


def explode_mtext(doc, destroy=False):
    msp = doc.modelspace()
    with MTextExplode(msp) as xpl:
        for mtext in msp.query("MTEXT"):
            xpl.explode(mtext, destroy=destroy)
            if mtext.is_alive:
                mtext.dxf.layer = "SOURCE"


def test_created_text_styles_exists():
    from ezdxf.tools.text import MTextEditor

    doc = ezdxf.new()
    msp = doc.modelspace()
    editor = MTextEditor()
    editor.append("LINE0\n")
    editor.font("Open Sans")
    editor.append("LINE1")
    mtext = msp.add_mtext(editor.text)
    with MTextExplode(msp) as xpl:
        xpl.explode(mtext)
    assert doc.styles.has_entry("MtXpl_DejaVu Sans Condensed")  # default font
    assert doc.styles.has_entry("MtXpl_Open Sans")  # MTEXT inline set font


def test_addon_is_still_working():
    # Testing only the basic functionality!
    # The text layout engine has its own test suite in test file 517!
    # The MTextParser has its own test suite in test file 521!
    doc = new_doc(LEFT + CENTER + RIGHT + JUSTIFIED)
    explode_mtext(doc, destroy=True)
    msp = doc.modelspace()
    assert len(msp.query("MTEXT")) == 0
    assert len(msp.query("TEXT")) == 208  # checked by BricsCAD
