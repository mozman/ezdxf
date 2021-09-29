#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.tools import fonts

# Load default font definitions, included in ezdxf:
fonts.load()


def test_find_font_face_without_definition():
    assert fonts.find_font_face("mozman.ttf") is None
    assert fonts.find_font_face(None) is None, "should accept None as argument"


def test_find_font_face():
    assert fonts.find_font_face("Arial.ttf") == (
        "arial.ttf",
        "Arial",
        "normal",
        "normal",
        400,
    )


def test_get_font_without_definition():
    # Creates a pseudo entry:
    assert fonts.get_font_face("mozman.ttf") == (
        "mozman.ttf",
        "mozman",
        "normal",
        "normal",
        "normal",
    )
    with pytest.raises(TypeError):
        fonts.get_font_face(None)  # should not accept None as argument"


def test_get_font_face_with_definition():
    assert fonts.get_font_face("Arial.ttf") is fonts.find_font_face("arial.ttf")


def test_map_shx_to_ttf():
    assert fonts.map_shx_to_ttf("TXT") == "txt_____.ttf"
    assert fonts.map_shx_to_ttf("TXT.SHX") == "txt_____.ttf"
    assert fonts.map_shx_to_ttf("txt.shx") == "txt_____.ttf"


def test_map_ttf_to_shx():
    assert fonts.map_ttf_to_shx("txt_____.ttf") == "TXT.SHX"
    assert fonts.map_ttf_to_shx("TXT_____.TTF") == "TXT.SHX"
    assert fonts.map_ttf_to_shx("xxx.ttf") is None


def test_get_font_face_for_shx_fonts():
    assert fonts.get_font_face("TXT") == (
        "txt_____.ttf",
        "Txt",
        "normal",
        "normal",
        400,
    )


def test_get_font_measurement():
    assert fonts.get_font_measurements("Arial.ttf") == (
        0.0,
        0.71578125,
        0.51859375,
        0.19875,
    )


def test_get_font_measurement_for_shx_fonts():
    assert fonts.get_font_measurements("TXT.shx") == (
        -0.0053125,
        0.7293750000000001,
        0.49171875,
        0.23390625,
    )


def test_get_undefined_font_measurement():
    assert fonts.get_font_measurements("mozman.ttf") == (
        0.0,
        1,
        fonts.X_HEIGHT_FACTOR,
        fonts.DESCENDER_FACTOR,
    )


def test_get_cache_file_path():
    path = fonts.get_cache_file_path(None, name="mozman.cfg")
    assert path.name == "mozman.cfg"
    path = fonts.get_cache_file_path("~/ezdxf", "mozman.json")
    assert path.name == "mozman.json"
    assert path.parent.name == "ezdxf"


def test_save_and_load_caches(tmp_path):
    fonts.save(tmp_path)
    assert (tmp_path / "font_face_cache.json").exists()
    assert (tmp_path / "font_measurement_cache.json").exists()
    fonts.font_face_cache = {}
    fonts.font_measurement_cache = {}
    fonts.load(tmp_path)
    assert len(fonts.font_face_cache) > 0
    assert len(fonts.font_measurement_cache) > 0


def test_same_font_faces_have_equal_hash_values():
    f1 = fonts.FontFace("arial.ttf", "Arial")
    f2 = fonts.FontFace("arial.ttf", "Arial")
    assert hash(f1) == hash(f2)


def test_font_face_is_italic():
    assert fonts.FontFace(style="italic").is_italic is True
    assert fonts.FontFace(style="oblique-italic").is_italic is True
    assert fonts.FontFace(style="").is_italic is False
    assert fonts.FontFace().is_italic is False


def test_font_face_is_oblique():
    assert fonts.FontFace(style="oblique").is_oblique is True
    assert fonts.FontFace(style="oblique-italic").is_oblique is True
    assert fonts.FontFace(style="").is_oblique is False
    assert fonts.FontFace().is_oblique is False


def test_font_face_is_bold():
    assert fonts.FontFace().is_bold is False
    assert fonts.FontFace(weight=300).is_bold is False
    assert fonts.FontFace(weight="bold").is_bold is True
    assert fonts.FontFace(weight="black").is_bold is True
    assert fonts.FontFace(weight=500).is_bold is True


class TestFontMeasurements:
    @pytest.fixture
    def default(self):
        return fonts.FontMeasurements(
            baseline=1.3, cap_height=1.0, x_height=0.5, descender_height=0.25
        )

    def test_total_heigth(self, default):
        assert default.total_height == 1.25

    def test_scale(self, default):
        fm = default.scale(2)
        assert fm.baseline == 2.6, "expected scaled baseline"
        assert fm.total_height == 2.5, "expected scaled total height"

    def test_shift(self, default):
        fm = default.shift(1.0)
        assert fm.baseline == 2.3
        assert fm.total_height == 1.25

    def test_scale_from_baseline(self, default):
        fm = default.scale_from_baseline(desired_cap_height=2.0)
        assert fm.baseline == 1.3, "expected unchanged baseline value"
        assert fm.cap_height == 2.0
        assert fm.x_height == 1.0
        assert fm.descender_height == 0.50
        assert fm.total_height == 2.5

    def test_cap_top(self, default):
        assert default.cap_top == 2.3

    def test_x_top(self, default):
        assert default.x_top == 1.8

    def test_bottom(self, default):
        assert default.bottom == 1.05

    def test_monospace_font(self):
        font = fonts.MonospaceFont(2.5, 0.75)
        assert font.text_width("1234") == 7.5


def test_find_font_file_by_family():
    assert fonts.find_font_face_by_family("simsun").ttf == "simsun.ttc"
    assert fonts.find_font_face_by_family("mozman") is None


if __name__ == "__main__":
    pytest.main([__file__])
