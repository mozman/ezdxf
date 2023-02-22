#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.document import Drawing
from ezdxf import r12strict


def setup_drawing(doc: Drawing):
    doc.appids.add("my appid")
    doc.linetypes.add("my ltype", [0])
    doc.layers.add("my layer", linetype="my ltype")
    doc.styles.add("my style", font="arial.ttf")
    doc.dimstyles.add(
        "my dimstyle",
        dxfattribs={
            "dimblk": "my block 0",
            "dimblk1": "my block 1",
            "dimblk2": "my block 2",
        },
    )
    doc.ucs.add("my ucs")
    doc.views.add("my view")
    doc.viewports.add("my vport")

    doc.header["$CELTYPE"] = "my ltype"
    doc.header["$CLAYER"] = "my layer"
    doc.header["$DIMBLK"] = "my block 0"
    doc.header["$DIMBLK1"] = "my block 1"
    doc.header["$DIMBLK2"] = "my block 2"
    doc.header["$DIMSTYLE"] = "my dimstyle"
    doc.header["$TEXTSTYLE"] = "my style"
    doc.header["$UCSNAME"] = "my ucs"

    common_attribs = {"layer": "my layer", "linetype": "my ltype"}
    for name in ["my block 0", "my block 1", "my block 2"]:
        blk = doc.blocks.new(name)
        blk.add_point((0, 0), dxfattribs=common_attribs)
    msp = doc.modelspace()

    msp.add_line((0, 0), (1, 0), dxfattribs=common_attribs)

    text = msp.add_text("any text", dxfattribs=common_attribs)
    text.dxf.style = "my style"

    insert = msp.add_blockref("my block 0", (0, 0), dxfattribs=common_attribs)
    insert.add_attrib("my attrib", "any value")

    msp.add_linear_dim((0, 0), (0, 0), (1, 0), dimstyle="my dimstyle")


@pytest.fixture(scope="module")
def doc():
    doc = ezdxf.new("R12")
    setup_drawing(doc)
    r12strict.translate_names(doc)
    return doc


def test_translated_header_vars(doc: Drawing):
    assert doc.header["$CLAYER"] == "MY_LAYER"
    assert doc.header["$CELTYPE"] == "MY_LTYPE"
    assert doc.header["$DIMBLK"] == "MY_BLOCK_0"
    assert doc.header["$DIMBLK1"] == "MY_BLOCK_1"
    assert doc.header["$DIMBLK2"] == "MY_BLOCK_2"
    assert doc.header["$DIMSTYLE"] == "MY_DIMSTYLE"
    assert doc.header["$TEXTSTYLE"] == "MY_STYLE"
    assert doc.header["$UCSNAME"] == "MY_UCS"


def test_translated_appid(doc: Drawing):
    my_appid = doc.appids.get("MY_APPID")
    assert my_appid.dxf.name == "MY_APPID"


def test_translated_ltype(doc: Drawing):
    my_ltype = doc.linetypes.get("MY_LTYPE")
    assert my_ltype.dxf.name == "MY_LTYPE"


def test_translated_layer(doc: Drawing):
    my_layer = doc.layers.get("MY_LAYER")
    assert my_layer.dxf.name == "MY_LAYER"
    assert my_layer.dxf.linetype == "MY_LTYPE"


def test_translated_text_style(doc: Drawing):
    my_style = doc.styles.get("MY_STYLE")
    assert my_style.dxf.name == "MY_STYLE"


def test_translated_dimstyle(doc: Drawing):
    my_dimstyle = doc.dimstyles.get("MY_DIMSTYLE")
    assert my_dimstyle.dxf.name == "MY_DIMSTYLE"
    assert my_dimstyle.dxf.dimblk == "MY_BLOCK_0"
    assert my_dimstyle.dxf.dimblk1 == "MY_BLOCK_1"
    assert my_dimstyle.dxf.dimblk2 == "MY_BLOCK_2"


def test_translated_ucs(doc: Drawing):
    my_ucs = doc.ucs.get("MY_UCS")
    assert my_ucs.dxf.name == "MY_UCS"


def test_translated_view(doc: Drawing):
    my_view = doc.views.get("MY_VIEW")
    assert my_view.dxf.name == "MY_VIEW"


def test_translated_vport(doc: Drawing):
    my_vport = doc.viewports.get("MY_VPORT")
    assert my_vport[0].dxf.name == "MY_VPORT"


if __name__ == "__main__":
    pytest.main([__file__])
