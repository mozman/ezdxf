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


if __name__ == "__main__":
    pytest.main([__file__])
