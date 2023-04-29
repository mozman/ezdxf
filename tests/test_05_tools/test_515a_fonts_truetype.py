#  Copyright (c) 2020-2023, Manfred Moitzi
#  License: MIT License

import pytest
import platform

from ezdxf.math import BoundingBox2d
from ezdxf.fonts import fonts

TEST_FONTS = [
    ("LiberationSans-Regular.ttf", "Liberation Sans"),
    ("LiberationSerif-Regular.ttf", "Liberation Serif"),
    ("LiberationMono-Regular.ttf", "Liberation Mono"),
    ("LiberationSansNarrow-Regular.ttf", "Liberation Sans Narrow"),
    ("DejaVuSans.ttf", "DejaVu Sans"),
    ("DejaVuSerif.ttf", "DejaVu Serif"),
    ("DejaVuSansMono.ttf", "DejaVu Sans Mono"),
    ("OpenSans-Regular.ttf", "Open Sans"),
    ("OpenSansCondensed-Light.ttf", "Open Sans Condensed"),
    ("NotoSansSC-Regular.otf", "Noto Sans SC"),
]


@pytest.mark.parametrize("ttf,family", TEST_FONTS)
def test_if_all_test_fonts_are_available(ttf, family):
    font_face = fonts.font_manager.get_font_face(ttf)
    assert font_face.family == family, "required test-font not found"


def default_font():
    return fonts.font_manager.get_font_face("default")


def test_find_font_face_without_definition():
    assert (
        fonts.find_font_face("mozman.ttf") is default_font()
    ), "returns a default font"
    assert fonts.find_font_face(None) is default_font(), "returns a default font"


def test_find_font_face():
    r = fonts.find_font_face("LiberationSans-Regular.ttf")
    assert fonts.find_font_face("LiberationSans-Regular.ttf") == (
        "LiberationSans-Regular.ttf",
        "Liberation Sans",
        "Regular",
        400,
        5,
    )


def test_get_font_without_definition():
    default_font = fonts.font_manager.get_font_face("default")
    assert fonts.get_font_face("mozman.ttf") is default_font


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


def test_get_font_measurement():
    assert len(fonts.get_font_measurements("LiberationSans-Regular.ttf")) == 4


def test_get_font_measurement_for_shx_fonts():
    assert len(fonts.get_font_measurements("TXT.shx")) == 4


class TestFontFace:
    def test_same_font_faces_have_equal_hash_values(self):
        f1 = fonts.FontFace("arial.ttf", "Arial")
        f2 = fonts.FontFace("arial.ttf", "Arial")
        assert hash(f1) == hash(f2)

    def test_font_face_is_italic(self):
        assert fonts.FontFace(style="italic").is_italic is True
        assert fonts.FontFace(style="oblique-italic").is_italic is True
        assert fonts.FontFace(style="").is_italic is False
        assert fonts.FontFace().is_italic is False

    def test_font_face_is_oblique(self):
        assert fonts.FontFace(style="oblique").is_oblique is True
        assert fonts.FontFace(style="oblique-italic").is_oblique is True
        assert fonts.FontFace(style="").is_oblique is False
        assert fonts.FontFace().is_oblique is False

    def test_font_face_is_bold(self):
        assert fonts.FontFace().is_bold is False
        assert fonts.FontFace(weight=300).is_bold is False
        assert fonts.FontFace(weight=500).is_bold is True
        assert fonts.FontFace(weight=700).is_bold is True
        assert fonts.FontFace(weight=900).is_bold is True

    def test_weight_str(self):
        assert fonts.FontFace(weight=-1000).weight_str == "Thin"
        assert fonts.FontFace(weight=0).weight_str == "Thin"
        assert fonts.FontFace(weight=90).weight_str == "Thin"
        assert fonts.FontFace(weight=110).weight_str == "Thin"
        assert fonts.FontFace(weight=390).weight_str == "Normal"
        assert fonts.FontFace(weight=410).weight_str == "Normal"
        assert fonts.FontFace(weight=890).weight_str == "Black"
        assert fonts.FontFace(weight=950).weight_str == "Black"
        assert fonts.FontFace(weight=3000).weight_str == "Black"

    def test_width_str(self):
        assert fonts.FontFace(width=-1000).width_str == "UltraCondensed"
        assert fonts.FontFace(width=0).width_str == "UltraCondensed"
        assert fonts.FontFace(width=1).width_str == "UltraCondensed"
        assert fonts.FontFace(width=5).width_str == "Medium"
        assert fonts.FontFace(width=9).width_str == "UltraExpanded"
        assert fonts.FontFace(width=1000).width_str == "UltraExpanded"


class TestFontMeasurements:
    @pytest.fixture
    def default(self):
        return fonts.FontMeasurements(
            baseline=1.3, cap_height=1.0, x_height=0.5, descender_height=0.25
        )

    def test_total_height(self, default):
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


class TestMonospaceFont:
    @pytest.fixture(scope="class")
    def mono(self):
        # special name tio create the MonospaceFont for testing
        return fonts.make_font("*monospace", 2.5, 0.75)

    def test_space_width(self, mono):
        assert mono.space_width() == pytest.approx(1.875)

    def test_text_width(self, mono):
        assert mono.text_width("1234") == pytest.approx(7.5)

    def test_text_width_ex(self, mono):
        assert mono.text_width_ex(
            "1234", cap_height=3, width_factor=1
        ) == pytest.approx(12)

    def test_text_path(self, mono):
        box = BoundingBox2d(mono.text_path("1234").control_vertices())
        assert box.size.x == pytest.approx(7.5)
        assert box.size.y == pytest.approx(2.5)

    def test_text_path_ex(self, mono):
        box = BoundingBox2d(
            mono.text_path_ex("1234", cap_height=3, width_factor=1).control_vertices()
        )
        assert box.size.x == pytest.approx(12)
        assert box.size.y == pytest.approx(3)


class TestTrueTypeFont:
    """Just test if the methods are implemented and return plausible values, don't test
    exact values, this is not a test of the rendering engine itself and results may
    change by the next revision of the font DejaVuSans.ttf or the fontTools.
    """

    @pytest.fixture(scope="class")
    def ttf(self):
        return fonts.make_font("DejaVuSans.ttf", 2.5)

    def test_space_width(self, ttf):
        assert ttf.space_width() > 1

    def test_text_width(self, ttf):
        assert ttf.text_width("1234") > 7.5

    def test_text_width_ex(self, ttf):
        assert ttf.text_width_ex("1234", cap_height=3, width_factor=2) > 19

    def test_text_path(self, ttf):
        box = BoundingBox2d(ttf.text_path("1234").control_vertices())
        assert box.size.x > 7.5
        assert box.size.y > 2.5

    def test_text_path_ex(self, ttf):
        box = BoundingBox2d(
            ttf.text_path_ex("1234", cap_height=3, width_factor=2).control_vertices()
        )
        assert box.size.x > 19
        assert box.size.y > 3


# This test works when testing only this test script in PyCharm or with pytest, but does
# not work when launching the whole test suite.
@pytest.mark.skipif(
    platform.system() != "Windows", reason="does not work on github/linux?"
)
def test_find_font_file_by_best_match():
    assert (
        fonts.find_best_match(family="Noto Sans SC").filename
        == "NotoSansSC-Regular.otf"
    )
    assert fonts.find_best_match(family="mozman") is None
    assert (
        fonts.find_best_match(family="Liberation Sans").filename
        == "LiberationSans-Regular.ttf"
    )
    assert fonts.find_best_match(family="DejaVu Sans").filename == "DejaVuSans.ttf"


# Works on Windows and Linux Mint, but not on github/Ubuntu
@pytest.mark.skipif(platform.system() != "Windows", reason="does not work on github")
def test_find_generic_font_family():
    assert fonts.find_best_match(family="serif").filename == "DejaVuSerif.ttf"
    assert fonts.find_best_match(family="sans-serif").filename == "DejaVuSans.ttf"
    assert fonts.find_best_match(family="monospace").filename == "DejaVuSansMono.ttf"


if __name__ == "__main__":
    pytest.main([__file__])
