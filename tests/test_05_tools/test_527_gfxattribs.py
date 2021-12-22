#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.gfxattribs import gfxattribs


def test_build_layer_name():
    assert gfxattribs(layer="LAYER") == {"layer": "LAYER"}


def test_invalid_layer_name_raises_exception():
    """layer name tests see validator test suite 020: is_valid_layer_name()
    """
    with pytest.raises(ezdxf.DXFValueError):
        gfxattribs(layer="*Layer")


def test_build_aci_color():
    assert gfxattribs(color=1) == {"color": 1}


def test_invalid_aci_color_raises_exception():
    """ACI color tests see validator test suite 020: is_valid_aci_color()
    """
    with pytest.raises(ezdxf.DXFValueError):
        gfxattribs(color=-1)


def test_build_true_color():
    assert gfxattribs(rgb=(0xA, 0xB, 0xC)) == {"true_color": 0x0A0B0C}


def test_invalid_true_color_raises_exception():
    """RGB color tests see validator test suite 020: is_valid_rgb()
    """
    with pytest.raises(ezdxf.DXFValueError):
        gfxattribs(rgb=(-1, 0, 0))


def test_build_linetype():
    assert gfxattribs(linetype="XYZ") == {"linetype": "XYZ"}


def test_invalid_linetype_name_raises_exception():
    with pytest.raises(ezdxf.DXFValueError):
        gfxattribs(linetype="*XYZ")


def test_build_lineweight():
    assert gfxattribs(lineweight=25) == {"lineweight": 25}


def test_invalid_lineweight_value_raises_exception():
    """lineweight tests see validator test suite 020: is_valid_lineweight()
    """
    with pytest.raises(ezdxf.DXFValueError):
        gfxattribs(lineweight=17)


def test_build_transparency():
    assert gfxattribs(transparency=0.5) == {"transparency": 0x200007f}


def test_invalid_transparency_value_raises_exception():
    with pytest.raises(ezdxf.DXFValueError):
        gfxattribs(transparency=2.0)


if __name__ == "__main__":
    pytest.main([__file__])
