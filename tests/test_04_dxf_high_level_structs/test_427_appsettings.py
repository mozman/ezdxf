#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import appsettings


@pytest.fixture(scope="module")
def doc():
    return ezdxf.new()


def test_set_current_layer(doc):
    appsettings.set_current_layer(doc, "0")
    assert doc.header["$CLAYER"] == "0"


def test_invalid_layer_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_layer(doc, "INVALID")


def test_set_current_aci_color(doc):
    appsettings.set_current_color(doc, 7)
    assert doc.header["$CECOLOR"] == 7


def test_invalid_aci_color_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_color(doc, 300)


def test_set_current_linetype(doc):
    doc.linetypes.add("TEST", [0.0])
    appsettings.set_current_linetype(doc, "TEST")
    assert doc.header["$CELTYPE"] == "TEST"


def test_invalid_linetype_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_linetype(doc, "INVALID")


def test_set_current_lineweight(doc):
    appsettings.set_current_lineweight(doc, 50)
    assert doc.header["$CELWEIGHT"] == 50


def test_invalid_lineweight_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_lineweight(doc, 300)


def test_set_current_linetype_scale(doc):
    appsettings.set_current_linetype_scale(doc, 2.0)
    assert doc.header["$CELTSCALE"] == 2.0


def test_invalid_linetype_scale_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_linetype_scale(doc, 0)


def test_set_current_textstyle(doc):
    doc.styles.add("TEST", font="arial.ttf")
    appsettings.set_current_textstyle(doc, "TEST")
    assert doc.header["$TEXTSTYLE"] == "TEST"


def test_invalid_textstyle_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_textstyle(doc, "INVALID")


def test_set_current_dimstyle(doc):
    doc.dimstyles.add("TEST")
    appsettings.set_current_dimstyle(doc, "TEST")
    assert doc.header["$DIMSTYLE"] == "TEST"


def test_invalid_dimstyle_raises_exception(doc):
    with pytest.raises(ezdxf.DXFValueError):
        appsettings.set_current_dimstyle(doc, "INVALID")


if __name__ == "__main__":
    pytest.main([__file__])
