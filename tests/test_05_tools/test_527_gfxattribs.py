#  Copyright (c) 2021-2023, Manfred Moitzi
#  License: MIT License

import pytest
import ezdxf
from ezdxf import gfxattribs, const, colors
from ezdxf.gfxattribs import GfxAttribs
from ezdxf.entities import factory


class TestDefaultGfxAttribs:
    def test_default_init(self):
        attribs = GfxAttribs()
        assert attribs.layer == "0"
        assert attribs.color == ezdxf.colors.BYLAYER
        assert attribs.rgb is None
        assert attribs.linetype == "ByLayer"
        assert attribs.lineweight == ezdxf.const.LINEWEIGHT_BYLAYER
        assert attribs.transparency is None
        assert attribs.ltscale == 1.0

    def test_str(self):
        assert str(GfxAttribs()) == ""

    def test_repr(self):
        assert repr(GfxAttribs()) == "GfxAttribs()"

    def test_as_dict(self):
        assert dict(GfxAttribs()) == dict()

    def test_as_dict_default_values(self):
        assert GfxAttribs().asdict(default_values=True) == {
            "layer": gfxattribs.DEFAULT_LAYER,
            "color": gfxattribs.DEFAULT_ACI_COLOR,
            "linetype": gfxattribs.DEFAULT_LINETYPE,
            "lineweight": gfxattribs.DEFAULT_LINEWEIGHT,
            "ltscale": gfxattribs.DEFAULT_LTSCALE,
        }


class TestGfxAttribsFromDict:
    def test_set_aci_color(self):
        attribs = GfxAttribs.from_dict({"color": 10})
        assert attribs.layer == "0"
        assert attribs.color == 10
        assert attribs.rgb is None
        assert attribs.linetype == "ByLayer"
        assert attribs.lineweight == ezdxf.const.LINEWEIGHT_BYLAYER
        assert attribs.transparency is None
        assert attribs.ltscale == 1.0

    def test_set_transparency_as_float(self):
        attribs = GfxAttribs.from_dict({"transparency": 0.5})
        assert attribs.transparency == 0.5

    def test_set_transparency_by_block(self):
        attribs = GfxAttribs.from_dict({"transparency": colors.TRANSPARENCY_BYBLOCK})
        assert attribs.transparency == -1.0

    def test_set_transparency_as_raw_dxf_value(self):
        attribs = GfxAttribs.from_dict({"transparency": colors.TRANSPARENCY_40})
        assert attribs.transparency == pytest.approx(0.4)

    def test_validation_errors(self):
        with pytest.raises(const.DXFValueError):
            GfxAttribs.from_dict({"color": 300})
        with pytest.raises(const.DXFValueError):
            GfxAttribs.from_dict({"rgb": (0, )})

class TestGfxAttribLayer:
    def test_init_by_value(self):
        assert GfxAttribs(layer="Test").layer == "Test"

    def test_init_by_invalid_value_raises_exception(self):
        with pytest.raises(ezdxf.DXFValueError):
            assert GfxAttribs(layer="Test*")

    def test_set_value(self):
        attribs = GfxAttribs()
        attribs.layer = "Test"
        assert attribs.layer == "Test"

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.layer = "Test*"

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
        assert repr(GfxAttribs(rgb=(10, 20, 30))) == "GfxAttribs(rgb=(10, 20, 30))"


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
        assert repr(GfxAttribs(linetype="Test")) == "GfxAttribs(linetype='Test')"


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

    def test_set_by_block_value(self):
        attribs = GfxAttribs()
        attribs.transparency = gfxattribs.TRANSPARENCY_BYBLOCK
        assert attribs.transparency == gfxattribs.TRANSPARENCY_BYBLOCK

    def test_reset_value(self):
        attribs = GfxAttribs(transparency=0.5)
        attribs.transparency = None
        assert attribs.transparency is None

    def test_set_invalid_value_raises_exception(self):
        attribs = GfxAttribs()
        with pytest.raises(ezdxf.DXFValueError):
            attribs.transparency = 2.0

    def test_str(self):
        assert str(GfxAttribs(transparency=0.5001)) == "transparency=0.5"

    def test_by_block_str(self):
        assert str(GfxAttribs(transparency=-1)) == "transparency=-1.0"

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


def test_gfx_attribs_as_dict():
    attribs = GfxAttribs(
        layer="Test",
        color=1,
        rgb=(0xA, 0xB, 0xC),
        linetype="SOLID",
        lineweight=50,
        transparency=0.5,
        ltscale=2,
    )
    expected = {
        "layer": "Test",
        "color": 1,
        "true_color": 0x0A0B0C,
        "linetype": "SOLID",
        "lineweight": 50,
        "transparency": 0x200007F,
        "ltscale": 2.0,
    }

    assert sorted(attribs.items()) == sorted(expected.items())
    assert attribs.asdict() == expected
    assert dict(attribs) == expected


def test_transparency_by_block_as_dict():
    attribs = GfxAttribs(
        transparency=gfxattribs.TRANSPARENCY_BYBLOCK,
    )
    expected = [("transparency", ezdxf.colors.TRANSPARENCY_BYBLOCK)]
    assert attribs.items() == expected
    assert attribs.asdict() == dict(expected)
    assert dict(attribs) == dict(expected)


def test_gfx_attribs_string():
    attribs = GfxAttribs(layer="Test", color=1, ltscale=2)
    assert str(attribs) == "layer='Test', color=1, ltscale=2.0"


def test_gfx_attribs_repr():
    attribs = GfxAttribs(layer="Test", color=1, ltscale=2)
    assert repr(attribs) == "GfxAttribs(layer='Test', color=1, ltscale=2.0)"


def test_load_header_defaults():
    doc = ezdxf.new()
    attribs = GfxAttribs.load_from_header(doc)
    assert attribs.layer == "0"
    assert attribs.color == ezdxf.colors.BYLAYER
    assert attribs.linetype == "ByLayer"
    assert attribs.lineweight == ezdxf.const.LINEWEIGHT_BYLAYER
    assert attribs.ltscale == 1.0


def test_write_back_header_defaults():
    doc = ezdxf.new()
    doc.layers.new("Test")
    doc.linetypes.new("SOLID")
    attribs = GfxAttribs(
        layer="Test",
        color=1,
        linetype="SOLID",
        lineweight=50,
        ltscale=2,
    )
    attribs.write_to_header(doc)
    assert doc.header["$CLAYER"] == "Test"
    assert doc.header["$CECOLOR"] == 1
    assert doc.header["$CELTYPE"] == "SOLID"
    assert doc.header["$CELWEIGHT"] == 50
    assert doc.header["$CELTSCALE"] == 2.0


def test_from_entity():
    line = factory.new(
        "LINE",
        dict(
            GfxAttribs(
                layer="Test",
                color=3,
                rgb=(10, 20, 30),
                transparency=0.3019607843137255,
                linetype="SOLID",
                lineweight=50,
                ltscale=3.0,
            )
        ),
    )
    attribs = GfxAttribs.from_entity(line)
    assert attribs.layer == "Test"
    assert attribs.color == 3
    assert attribs.rgb == (10, 20, 30)
    assert attribs.transparency == 0.3019607843137255
    assert attribs.linetype == "SOLID"
    assert attribs.ltscale == 3.0


def test_update_dxf_attributes_from_gfx_attribs():
    attribs = GfxAttribs(
        layer="Test",
        color=3,
        rgb=(10, 20, 30),
        transparency=0.3019607843137255,
        linetype="SOLID",
        lineweight=50,
        ltscale=3.0,
    )
    line = factory.new("LINE")
    line.update_dxf_attribs(dict(attribs))
    assert attribs.layer == line.dxf.layer
    assert attribs.color == line.dxf.color
    assert attribs.rgb == ezdxf.colors.int2rgb(line.dxf.true_color)
    assert attribs.transparency == ezdxf.colors.transparency2float(
        line.dxf.transparency
    )
    assert attribs.linetype == line.dxf.linetype
    assert attribs.ltscale == line.dxf.ltscale

    line = factory.new("LINE")
    line.dxf.update(dict(attribs))
    assert attribs.layer == line.dxf.layer
    assert attribs.color == line.dxf.color
    assert attribs.rgb == ezdxf.colors.int2rgb(line.dxf.true_color)
    assert attribs.transparency == ezdxf.colors.transparency2float(
        line.dxf.transparency
    )
    assert attribs.linetype == line.dxf.linetype
    assert attribs.ltscale == line.dxf.ltscale


def test_update_transparency_by_block_from_gfx_attribs():
    attribs = GfxAttribs(
        transparency=gfxattribs.TRANSPARENCY_BYBLOCK,
    )
    line = factory.new("LINE")
    line.dxf.update(dict(attribs))
    assert line.dxf.transparency == ezdxf.colors.TRANSPARENCY_BYBLOCK


if __name__ == "__main__":
    pytest.main([__file__])
