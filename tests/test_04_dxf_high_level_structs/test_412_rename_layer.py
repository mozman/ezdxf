# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import pytest
import ezdxf

LAYER = "test"


@pytest.fixture
def dxf():
    doc = ezdxf.new("R2000")
    doc.layers.new(LAYER)
    msp = doc.modelspace()
    msp.add_text("A", dxfattribs={"layer": LAYER})
    blk = doc.blocks.new("TEST")
    blk.add_text("A", dxfattribs={"layer": LAYER})
    return doc


def test_rename_layer(dxf):
    NEW_LAYER = "XYZ"
    layer = dxf.layers.get(LAYER)
    layer.rename(NEW_LAYER)

    assert dxf.layers.has_entry(NEW_LAYER)

    msp = dxf.modelspace()
    assert msp[0].dxf.layer == NEW_LAYER

    blk = dxf.blocks.get("TEST")
    assert blk[0].dxf.layer == NEW_LAYER


def test_rename_layer_errors(dxf):
    layer = dxf.layers.get(LAYER)
    pytest.raises(ValueError, layer.rename, "*XXX")
    pytest.raises(ValueError, layer.rename, LAYER)

    layer = dxf.layers.get("0")
    pytest.raises(ValueError, layer.rename, LAYER)

    layer = dxf.layers.get("DEFPOINTS")
    pytest.raises(ValueError, layer.rename, LAYER)
