#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.math import BoundingBox2d
from ezdxf.fonts import fonts


@pytest.fixture(scope="module", autouse=True)
def check_shape_files_available():
    if not fonts.font_manager.has_font("txt.shx"):
        pytest.skip(reason="required shapefile fonts are not available")


def test_get_font_family_for_shx_files():
    font_face = fonts.font_manager.get_font_face("txt.shx")
    assert font_face.family == "txt"


def test_get_font_family_for_shp_files():
    font_face = fonts.font_manager.get_font_face("txt.shp")
    assert font_face.family == "txt"


def test_get_font_style_for_shx_files():
    font_face = fonts.font_manager.get_font_face("txt.shx")
    assert font_face.style == ".shx"
    # Same weight and width for all shapefile fonts, because this information is not
    # included in the font definition file.
    assert font_face.weight_str == "Normal"
    assert font_face.width_str == "Medium"


def test_best_match_for_shape_files():
    font_face = fonts.find_best_match(family="iso")
    assert font_face.style == ".shx"

    font_face = fonts.find_best_match(family="iso", style=".shp")
    assert font_face.style == ".shp"

    font_face = fonts.find_best_match(family="iso", style=".lff")
    assert font_face.style == ".lff"


def test_width_value_influences_the_best_match_for_shape_files():
    # Note: the width property is used to prioritize font types:
    # 1st .shx; 2nd: .shp; 3rd: .lff
    font_face = fonts.find_best_match(family="iso", width=5)
    assert font_face.filename == "ISO.shx"
    assert font_face.style == ".shx"

    font_face = fonts.find_best_match(family="iso", width=6)
    assert font_face.style == ".shp"

    font_face = fonts.find_best_match(family="iso", width=7)
    assert font_face.style == ".lff"


class TestShapeFileFont:
    @pytest.fixture(scope="class")
    def shx(self):
        return fonts.make_font("txt.shx", 2.5)

    def test_space_width(self, shx):
        assert shx.space_width() == pytest.approx(2.5)

    def test_text_width(self, shx):
        assert shx.text_width("1234") == pytest.approx(9.1666666666)

    def test_text_width_ex(self, shx):
        assert shx.text_width_ex("1234", cap_height=3, width_factor=2) == pytest.approx(
            22
        )

    def test_text_path(self, shx):
        box = BoundingBox2d(shx.text_path("1234").control_vertices())
        assert box.size.x == pytest.approx(9.166666666)
        assert box.size.y == pytest.approx(2.5)

    def test_text_path_ex(self, shx):
        box = BoundingBox2d(
            shx.text_path_ex("1234", cap_height=3, width_factor=2).control_vertices()
        )
        assert box.size.x == pytest.approx(22)
        assert box.size.y == pytest.approx(3)


class TestGlyphCache:
    @pytest.fixture(scope="class")
    def cache(self):
        return fonts.font_manager.get_shapefile_glyph_cache("txt.shx")

    def test_get_glyphs(self, cache):
        glyph = cache.get_shape(ord("A"))
        box = BoundingBox2d(glyph.control_vertices())
        assert box.size.x == 6
        assert box.size.y == 6
        assert glyph is cache.get_shape(ord("A"))

    def test_get_advance_width(self, cache):
        glyph = cache.get_shape(ord("A"))
        assert glyph.end.x == 6  # last move_to defines the advance width
        assert cache.get_advance_width(ord("A")) == 6

    def test_get_space_width(self, cache):
        assert cache.space_width == 6

    def test_get_font_measurements(self, cache):
        fm = cache.font_measurements
        assert fm.cap_height == 6
        assert fm.baseline == 0
        assert fm.x_height == 4
        assert fm.descender_height == 2

    def test_path_for_unsupported_glyphs(self, cache):
        box = cache.get_shape(1234)
        assert len(box) == 5

    def test_spaces_are_measured(self, cache):
        assert cache.get_text_length("   ", cache.font_measurements.cap_height) == 18

    def test_spaces_are_rendered(self, cache):
        p = cache.get_text_path("   ", cache.font_measurements.cap_height)
        assert p.end.isclose((18, 0))


def test_resolve_shx_font_name():
    assert fonts.resolve_shx_font_name("txt", order="s") == "txt.shx"
    assert fonts.resolve_shx_font_name("txt.shx", order="s") == "txt.shx"
    # txt_____.ttf is not available under test
    # prefer LibreCAD fonts:
    assert fonts.resolve_shx_font_name("txt", order="tls") == "standard.lff"
    assert fonts.resolve_shx_font_name("txt.shx", order="tls") == "standard.lff"


if __name__ == "__main__":
    pytest.main([__file__])
