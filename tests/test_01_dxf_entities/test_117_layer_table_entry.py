# Copyright (C) 2011-2022, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.entities.layer import Layer
from ezdxf.lldxf.const import DXFValueError


@pytest.fixture
def layer():
    return Layer.new(handle="FFFF")


def test_get_handle(layer):
    assert "FFFF" == layer.dxf.handle


def test_get_name(layer):
    assert "0" == layer.dxf.name


def test_get_flags(layer):
    assert layer.dxf.flags == 0


def test_get_color(layer):
    assert layer.dxf.color == 7


def test_get_linetype(layer):
    assert layer.dxf.linetype.upper() == "CONTINUOUS"


def test_set_name(layer):
    layer.dxf.name = "MOZMAN"
    assert "MOZMAN" == layer.dxf.name


def test_set_color(layer):
    layer.dxf.color = "1"
    assert 1 == layer.dxf.color


def test_set_color_2(layer):
    layer.set_color(-1)
    assert 1 == layer.get_color()


def test_set_color_for_off_layer(layer):
    layer.set_color(7)
    layer.off()
    assert 7 == layer.get_color()
    assert -7 == layer.dxf.color


def test_color_as_property(layer):
    layer.color = 7
    layer.off()
    assert 7 == layer.color
    assert -7 == layer.dxf.color


def test_is_locked(layer):
    layer.lock()
    assert layer.is_locked() is True


def test_is_not_locked(layer):
    assert layer.is_locked() is False


def test_is_on(layer):
    assert layer.is_on() is True


def test_is_off(layer):
    layer.dxf.color = -100
    assert layer.is_off() is True


def test_is_frozen(layer):
    assert layer.is_frozen() is False


def test_freeze(layer):
    layer.freeze()
    assert layer.is_frozen() is True
    assert 1 == layer.dxf.flags


def test_thaw(layer):
    layer.dxf.flags = 1
    assert layer.is_frozen() is True
    layer.thaw()
    assert layer.is_frozen() is False
    assert 0 == layer.dxf.flags


def test_invald_layer_name():
    with pytest.raises(DXFValueError):
        Layer.new("FFFF", dxfattribs={"name": "Layer/"})


def test_set_true_color_as_rgb(layer):
    layer.rgb = (10, 10, 10)
    assert layer.dxf.true_color == 657930


def test_get_true_color_as_rgb(layer):
    layer.dxf.true_color = 657930
    assert layer.rgb == (10, 10, 10)


def test_get_default_description(layer):
    assert layer.description == ""


def test_get_default_description_at_existing_xdata(layer):
    layer.set_xdata("mozman", [(1000, "test")])
    assert layer.description == ""


def test_description_for_unusual_xdata_structure(layer):
    # Just one group code 1000 tag - not reproducible with BricsCAD
    layer.set_xdata("AcAecLayerStandard", [(1000, "test")])
    assert layer.description == ""

    # or empty XDATA section - not reproducible with BricsCAD
    layer.set_xdata("AcAecLayerStandard", [])
    assert layer.description == ""


def test_set_description(layer):
    layer.description = "my Layer"
    assert layer.description == "my Layer"

    # test DXF internals
    assert "AcAecLayerStandard" in layer.xdata


def test_replace_description(layer):
    layer.description = "my Layer"
    assert layer.description == "my Layer"
    layer.description = "new Description"
    assert layer.description == "new Description"


def test_get_default_transparency(layer):
    assert layer.transparency == 0


def test_fully_transparent_layer(layer):
    layer.set_xdata("AcCmTransparency", [(1071, 0x02000000)])
    assert layer.transparency == 1.0


def test_half_transparent_layer(layer):
    layer.set_xdata("AcCmTransparency", [(1071, 0x0200007F)])
    assert round(layer.transparency, 2) == 0.5


def test_opaque_layer(layer):
    layer.set_xdata("AcCmTransparency", [(1071, 0x020000FF)])
    assert layer.transparency == 0.0


def test_invalid_transparency_returns_opaque(layer):
    # The flag 0x02000000 has to be set for a valid transparency
    layer.set_xdata("AcCmTransparency", [(1071, 0)])
    assert layer.transparency == 0.0


def test_transparency_byblock_returns_opaque(layer):
    # Transparency BYBLOCK (0x01000000) make no sense for a layer!?
    layer.set_xdata("AcCmTransparency", [(1071, 0x01000000)])
    assert layer.transparency == 0.0


def test_set_transparency(layer):
    layer.transparency = 0.11
    assert round(layer.transparency, 2) == 0.11

    # test DXF internals
    assert "AcCmTransparency" in layer.xdata


def test_replace_transparency(layer):
    layer.transparency = 0.11
    assert round(layer.transparency, 2) == 0.11
    layer.transparency = 0.77
    assert round(layer.transparency, 2) == 0.77


MALFORMED_LAYER = """0
LAYER
2
LY_EZDXF
5
FEFE
100
AcDbLayerTableRecord
70
0
62
7
6
CONTINUOUS
100
AcDbSymbolTableRecord
"""


def test_malformed_layer():
    layer = Layer.from_text(MALFORMED_LAYER)
    assert layer.dxf.name == "LY_EZDXF"
    assert layer.dxf.handle == "FEFE"
    assert layer.dxf.color == 7
    assert layer.dxf.linetype == "CONTINUOUS"
