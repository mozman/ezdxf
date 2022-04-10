#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf

from ezdxf.layouts import Paperspace
from ezdxf.entities.layer import LayerOverrides
from ezdxf.lldxf import const


@pytest.fixture(scope="module")
def doc():
    doc_ = ezdxf.new(setup=["linetypes"])
    doc_.layers.add("VIEWPORTS")  # default viewport layer
    doc_.layers.add("LayerA", color=ezdxf.colors.RED)
    doc_.layers.add("LayerB", color=ezdxf.colors.YELLOW)
    layout: Paperspace = doc_.layout("Layout1")  # type: ignore
    layout.add_viewport(
        center=(2.5, 2.5),
        size=(5, 5),
        view_center_point=(7.5, 7.5),
        view_height=10,
    )
    layout.add_viewport(
        center=(8.5, 2.5),
        size=(5, 5),
        view_center_point=(10, 5),
        view_height=25,
    )
    return doc_


@pytest.fixture
def layer_a(doc):
    return doc.layers.get("LayerA")


def test_doc_setup(doc):
    assert "VIEWPORTS" in doc.layers
    assert "LayerA" in doc.layers
    l1 = doc.layout("Layout1")
    viewports = l1.query("VIEWPORT")
    assert len(viewports) == 2


def test_get_new_vp_override_object(layer_a):
    vp_overrides = layer_a.get_vp_overrides()
    assert isinstance(vp_overrides, LayerOverrides) is True


def test_if_a_layer_has_any_overrides(layer_a):
    vp_overrides = layer_a.get_vp_overrides()
    assert vp_overrides.has_overrides() is False


def test_if_a_layer_has_overrides_for_specific_viewport(layer_a):
    vp_overrides = layer_a.get_vp_overrides()
    assert vp_overrides.has_overrides("ABBA") is False


def test_get_default_layer_values_for_missing_overrides(layer_a):
    vp_handle = "ABBA"
    overrides = layer_a.get_vp_overrides()
    assert overrides.has_overrides(vp_handle) is False
    assert overrides.get_color(vp_handle) == ezdxf.colors.RED
    assert overrides.get_rgb(vp_handle) is None
    assert overrides.get_transparency(vp_handle) == 0.0
    assert overrides.get_linetype(vp_handle) == "Continuous"
    assert overrides.get_lineweight(vp_handle) == const.LINEWEIGHT_DEFAULT
    assert overrides.is_frozen(vp_handle) is False


class TestSetOverridesWithoutCommit:
    def test_set_color_override(self, layer_a):
        vp_overrides = layer_a.get_vp_overrides()
        vp_handle = "FEFE"
        vp_overrides.set_color(vp_handle, 6)
        assert vp_overrides.get_color(vp_handle) == 6

    @pytest.mark.parametrize(
        "value", [300, ezdxf.colors.BYLAYER, ezdxf.colors.BYBLOCK]
    )
    def test_invalid_color_raises_value_error(self, layer_a, value):
        vp_overrides = layer_a.get_vp_overrides()
        with pytest.raises(ValueError):
            vp_overrides.set_color("FEFE", value)

    def test_set_rgb_override(self, layer_a):
        vp_handle = "FEFE"
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.set_rgb(vp_handle, (1, 2, 3))
        assert vp_overrides.get_rgb(vp_handle) == (1, 2, 3)

    @pytest.fixture
    def layer_rgb(self, doc):
        yield doc.layers.add("LAYER_RGB")
        doc.layers.discard("LAYER_RGB")

    def test_remove_rgb_by_override(self, layer_rgb):
        layer_rgb.rgb = (1, 2, 3)
        vp_handle = "FEFE"
        vp_overrides = layer_rgb.get_vp_overrides()
        vp_overrides.set_rgb(vp_handle, None)
        assert vp_overrides.get_rgb(vp_handle) is None

    def test_set_transparency_override(self, layer_a):
        vp_handle = "FEFE"
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.set_transparency(vp_handle, 0.5)
        assert vp_overrides.get_transparency(vp_handle) == 0.5

    def test_set_linetype_override(self, layer_a):
        vp_handle = "FEFE"
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.set_linetype(vp_handle, "DASHED")
        assert vp_overrides.get_linetype(vp_handle) == "DASHED"

    def test_linetype_without_table_entry_raises_value_error(self, layer_a):
        vp_overrides = layer_a.get_vp_overrides()
        with pytest.raises(ValueError):
            vp_overrides.set_linetype("FEFE", "DoesNotExist")

    def test_set_lineweight_override(self, layer_a):
        vp_handle = "FEFE"
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.set_lineweight(vp_handle, 18)
        assert vp_overrides.get_lineweight(vp_handle) == 18

    @pytest.mark.parametrize(
        "value", [300, const.LINEWEIGHT_BYLAYER, const.LINEWEIGHT_BYBLOCK]
    )
    def test_invalid_lineweight_raises_value_error(self, layer_a, value):
        vp_overrides = layer_a.get_vp_overrides()
        with pytest.raises(ValueError):
            vp_overrides.set_lineweight("FEFE", value)

    def test_freeze_layer_in_vp(self, layer_a):
        vp_handle = "FEFE"
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.freeze(vp_handle)
        assert vp_overrides.is_frozen(vp_handle) is True

    @pytest.fixture
    def frozen_layer(self, doc):
        layer = doc.layers.add("LAYER_FROZEN")
        layer.freeze()
        yield layer
        doc.layers.discard(layer.dxf.name)

    def test_thaw_layer_in_vp(self, frozen_layer):
        vp_handle = "FEFE"
        vp_overrides = frozen_layer.get_vp_overrides()
        vp_overrides.thaw(vp_handle)
        assert vp_overrides.is_frozen(vp_handle) is False

    def test_discard_specific_overrides(self, layer_a):
        vp_overrides = layer_a.get_vp_overrides()
        vp_handle = "FEFE"
        vp_overrides.set_color(vp_handle, 6)
        assert vp_overrides.has_overrides(vp_handle) is True
        vp_overrides.discard(vp_handle)
        assert vp_overrides.has_overrides(vp_handle) is False

    def test_discard_all_overrides(self, layer_a):
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.set_color("FEFE", 6)
        vp_overrides.set_color("ABBA", 5)
        assert vp_overrides.has_overrides() is True
        vp_overrides.discard()
        assert vp_overrides.has_overrides() is False

    def test_discard_ignores_none_existing_vp_handles(self, layer_a):
        vp_overrides = layer_a.get_vp_overrides()
        vp_overrides.set_color("FEFE", 6)
        vp_overrides.discard("xyz")  # should not throw an exception
        assert vp_overrides.has_overrides() is True


if __name__ == "__main__":
    pytest.main([__file__])
