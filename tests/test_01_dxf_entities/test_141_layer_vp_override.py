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
    doc_.layers.add("LayerA", color=ezdxf.colors.RED)
    doc_.layers.add("LayerB", color=ezdxf.colors.YELLOW)
    return doc_


@pytest.fixture
def layer_a(doc):
    return doc.layers.get("LayerA")


def test_doc_setup(doc):
    assert "LayerA" in doc.layers


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


class TestCommitChanges:
    @pytest.fixture(scope="class")
    def vp1(self, doc):
        layout: Paperspace = doc.layout("Layout1")  # type: ignore
        return layout.add_viewport(
            center=(2.5, 2.5),
            size=(5, 5),
            view_center_point=(7.5, 7.5),
            view_height=10,
        )

    @pytest.fixture(scope="class")
    def vp2(self, doc):
        layout: Paperspace = doc.layout("Layout1")  # type: ignore
        return layout.add_viewport(
            center=(2.5, 2.5),
            size=(5, 5),
            view_center_point=(7.5, 7.5),
            view_height=10,
        )

    @staticmethod
    def set_all_ovr(ovr: LayerOverrides, vp_handle, color, alpha, ltype, lw):
        ovr.set_color(vp_handle, color)
        ovr.set_transparency(vp_handle, alpha)
        ovr.set_linetype(vp_handle, ltype)
        ovr.set_lineweight(vp_handle, lw)

    def test_commit_creates_proper_xdict_structure(self, doc, vp1):
        vp_handle = vp1.dxf.handle
        layer = doc.layers.add("LS_001")
        ovr = layer.get_vp_overrides()
        self.set_all_ovr(ovr, vp_handle, 3, 0.4, "DASHED", 50)
        ovr.commit()

        assert layer.has_extension_dict is True
        xdict = layer.get_extension_dict()
        assert const.OVR_COLOR_KEY in xdict
        assert const.OVR_ALPHA_KEY in xdict
        assert const.OVR_LTYPE_KEY in xdict
        assert const.OVR_LW_KEY in xdict

    def test_load_overrides_for_one_vp(self, doc, vp1):
        vp_handle = vp1.dxf.handle
        layer = doc.layers.add("LS_002")
        ovr = layer.get_vp_overrides()
        self.set_all_ovr(ovr, vp_handle, 3, 0.4, "DASHED", 50)
        ovr.commit()

        ovr2 = layer.get_vp_overrides()
        assert ovr2.has_overrides() is True
        assert ovr2.has_overrides(vp_handle) is True
        assert ovr2.get_color(vp_handle) == 3
        assert ovr2.get_transparency(vp_handle) == pytest.approx(0.4)
        assert ovr2.get_linetype(vp_handle) == "DASHED"
        assert ovr2.get_lineweight(vp_handle) == 50

    def test_load_overrides_for_two_vp(self, doc, vp1, vp2):
        h1 = vp1.dxf.handle
        h2 = vp2.dxf.handle
        layer = doc.layers.add("LS_003")
        ovr = layer.get_vp_overrides()
        self.set_all_ovr(ovr, h1, 3, 0.4, "DASHED", 50)
        self.set_all_ovr(ovr, h2, 4, 0.2, "CENTER", 35)
        ovr.commit()

        ovr2 = layer.get_vp_overrides()
        assert ovr2.has_overrides() is True
        assert ovr2.has_overrides(h1) is True
        assert ovr2.get_color(h1) == 3
        assert ovr2.get_transparency(h1) == pytest.approx(0.4)
        assert ovr2.get_linetype(h1) == "DASHED"
        assert ovr2.get_lineweight(h1) == 50

        assert ovr2.has_overrides(h2) is True
        assert ovr2.get_color(h2) == 4
        assert ovr2.get_transparency(h2) == pytest.approx(0.2)
        assert ovr2.get_linetype(h2) == "CENTER"
        assert ovr2.get_lineweight(h2) == 35


if __name__ == "__main__":
    pytest.main([__file__])
