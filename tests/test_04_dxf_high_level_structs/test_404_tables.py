# Copyright (c) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
import ezdxf
from ezdxf.sections.tables import TablesSection


@pytest.fixture(scope="module")
def tables():
    doc = ezdxf.new()
    return doc.tables


def test_constructor(tables):
    assert tables.layers is not None
    assert tables.linetypes is not None
    assert tables.appids is not None
    assert tables.styles is not None
    assert tables.dimstyles is not None
    assert tables.views is not None
    assert tables.viewports is not None
    assert tables.ucs is not None
    assert tables.block_records is not None


def test_getattr_upper_case(tables):
    with pytest.raises(AttributeError):
        _ = tables.LINETYPES


def test_error_getattr(tables):
    with pytest.raises(AttributeError):
        _ = tables.test


class TestAddLayerTableEntry:
    def test_add_layer(self, tables: TablesSection):
        layer = tables.layers.add(
            "NEW_LAYER",
            color=2,
            true_color=ezdxf.rgb2int((0x10, 0x20, 0x30)),
            linetype="DASHED",
            lineweight=18,
            plot=True
        )
        assert layer.dxf.name == "NEW_LAYER"
        assert layer.dxf.color == 2
        assert layer.dxf.true_color == 0x00102030
        assert layer.dxf.linetype == "DASHED", "no check if line type exist!"
        assert layer.dxf.lineweight == 18
        assert layer.dxf.plot == 1

    def test_check_invalid_aci_color(self, tables: TablesSection):
        with pytest.raises(ValueError):
            tables.layers.add("INVALID_ACI", color=300)

    def test_check_invalid_line_weight(self, tables: TablesSection):
        with pytest.raises(ValueError):
            tables.layers.add("INVALID_LINE_WEIGHT", lineweight=300)
