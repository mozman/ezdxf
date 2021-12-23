#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf.gfxattribs import GfxAttribs


class TestDefaultGfxAttribs:
    def test_default_init(self):
        attribs = GfxAttribs()
        assert attribs.layer == "0"
        assert attribs.color == ezdxf.colors.BYLAYER
        assert attribs.rgb is None
        assert attribs.linetype == "BYLAYER"
        assert attribs.lineweight == ezdxf.const.LINEWEIGHT_BYLAYER
        assert attribs.transparency == 0.0
        assert attribs.ltscale == 1.0

    def test_str(self):
        assert str(GfxAttribs()) == ""

    def test_repr(self):
        assert repr(GfxAttribs()) == "GfxAttribs()"


class TestGfxAttribLayer:
    def test_init_by_value(self):
        assert GfxAttribs(layer="Test").layer == "Test"

    def test_init_by_invalid_value_raises_exception(self):
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(layer="*Test")

    def test_set_value(self):
        attribs = GfxAttribs()
        attribs.layer = "Test"
        assert attribs.layer == "Test"

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.layer = "*Test"

    def test_str(self):
        assert str(GfxAttribs(layer="Test")) == "layer='Test'"

    def test_repr(self):
        assert repr(GfxAttribs(layer="Test")) == "GfxAttribs(layer='Test')"


class TestGfxAttribColor:
    def test_init_by_value(self):
        assert GfxAttribs(color=ezdxf.colors.RED).color == ezdxf.colors.RED

    def test_init_by_invalid_value_raises_exception(self):
        """ACI color tests see validator test suite 020: is_valid_aci_color()"""
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(color=300)

    def test_set_value(self):
        attribs = GfxAttribs()
        attribs.color = ezdxf.colors.RED
        assert attribs.color == ezdxf.colors.RED

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.color = 300

    def test_str(self):
        assert str(GfxAttribs(color=1)) == "color=1"

    def test_repr(self):
        assert repr(GfxAttribs(color=1)) == "GfxAttribs(color=1)"


class TestGfxAttribTrueColor:
    def test_init_by_value(self):
        assert GfxAttribs(rgb=(10, 20, 30)).rgb == (10, 20, 30)

    def test_init_by_invalid_value_raises_exception(self):
        """RGB color tests see validator test suite 020: is_valid_rgb()"""
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(rgb=(-1, 0, 0))

    def test_set_value(self):
        attribs = GfxAttribs()
        attribs.rgb = (10, 20, 30)
        assert attribs.rgb == (10, 20, 30)

    def test_reset_value(self):
        attribs = GfxAttribs(rgb=(10, 20, 30))
        attribs.rgb = None
        assert attribs.rgb is None

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.rgb = (-1, 0, 0)

    def test_str(self):
        assert str(GfxAttribs(rgb=(10, 20, 30))) == "rgb=(10, 20, 30)"

    def test_repr(self):
        assert (
            repr(GfxAttribs(rgb=(10, 20, 30))) == "GfxAttribs(rgb=(10, 20, 30))"
        )


class TestGfxAttribLinetype:
    def test_init_by_value(self):
        assert GfxAttribs(linetype="Test").linetype == "Test"

    def test_init_by_invalid_value_raises_exception(self):
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(linetype="*Test")

    def test_set_value(self):
        attribs = GfxAttribs()
        attribs.linetype = "Test"
        assert attribs.linetype == "Test"

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.linetype = "*Test"

    def test_str(self):
        assert str(GfxAttribs(linetype="Test")) == "linetype='Test'"

    def test_repr(self):
        assert (
            repr(GfxAttribs(linetype="Test")) == "GfxAttribs(linetype='Test')"
        )


class TestGfxAttribLineweight:
    def test_init_by_value(self):
        assert GfxAttribs(lineweight=18).lineweight == 18

    def test_init_by_invalid_value_raises_exception(self):
        """lineweight tests see validator test suite 020: is_valid_lineweight()"""
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(lineweight=300)

    def test_set_value(self):
        attribs = GfxAttribs()
        attribs.lineweight = 25
        assert attribs.lineweight == 25

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.lineweight = 300

    def test_str(self):
        assert str(GfxAttribs(lineweight=18)) == "lineweight=18"

    def test_repr(self):
        assert repr(GfxAttribs(lineweight=18)) == "GfxAttribs(lineweight=18)"


class TestGfxAttribTransparency:
    def test_init_by_value(self):
        assert GfxAttribs(transparency=0.5).transparency == 0.5

    def test_init_by_invalid_value_raises_exception(self):
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(transparency=2.0)

    @pytest.mark.parametrize("value", [0.0, 0.5, 1.0])
    def test_set_value(self, value):
        attribs = GfxAttribs()
        attribs.transparency = value
        assert attribs.transparency == value

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.transparency = 2.0

    def test_str(self):
        assert str(GfxAttribs(transparency=0.5001)) == "transparency=0.5"

    def test_repr(self):
        assert repr(GfxAttribs(transparency=0.5001)) == "GfxAttribs(transparency=0.5)"


class TestGfxAttribLinetypeScale:
    def test_init_by_value(self):
        assert GfxAttribs(ltscale=0.5).ltscale == 0.5

    def test_init_by_invalid_value_raises_exception(self):
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(ltscale=-1.0)

    @pytest.mark.parametrize("value", [0.5, 1.0, 2.0, 1])
    def test_set_value(self, value):
        attribs = GfxAttribs()
        attribs.ltscale = value
        assert attribs.ltscale == value

    @pytest.mark.parametrize("value", [-1.0, 0.0, -1])
    def test_set_invalid_value_raises_exception(self, value):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.ltscale = value

    def test_str(self):
        assert str(GfxAttribs(ltscale=0.5001)) == "ltscale=0.5"

    def test_repr(self):
        assert repr(GfxAttribs(ltscale=0.5001)) == "GfxAttribs(ltscale=0.5)"


if __name__ == "__main__":
    pytest.main([__file__])
