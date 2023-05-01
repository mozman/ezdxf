#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License
import pytest

from ezdxf.math import BoundingBox2d
from ezdxf import path
from ezdxf.fonts import fonts

FONT = "standard.lff"


@pytest.fixture(scope="module", autouse=True)
def check_libre_cad_fonts_available():
    if not fonts.font_manager.has_font(FONT):
        pytest.skip(reason=f"required LibreCAD '{FONT}' font is not available")


def test_get_font_family_for_lff_files():
    # LibreCAD does not include a replacement font for TXT
    font_face = fonts.font_manager.get_font_face("standard.lff")
    assert font_face.family == "standard"


TOL = 0.001


class TestLibreCadFont:
    @pytest.fixture(scope="class")
    def lff(self):
        return fonts.make_font(FONT, 2.5)

    def test_is_a_lff_font(self, lff):
        assert lff.name == FONT

    def test_space_width(self, lff):
        assert lff.space_width() == pytest.approx(1.875, abs=TOL)

    def test_text_width(self, lff):
        assert lff.text_width("1234") == pytest.approx(7.578981985029027, abs=TOL)

    def test_text_width_ex(self, lff):
        assert lff.text_width_ex("1234", cap_height=3, width_factor=2) == pytest.approx(
            18.189556764069664, abs=TOL
        )

    def test_text_path(self, lff):
        box = BoundingBox2d(lff.text_path("1234").control_vertices())
        assert box.size.x == pytest.approx(7.578981985029027, abs=TOL)
        assert box.size.y == pytest.approx(2.5789819850290274, abs=TOL)

    def test_text_path_ex(self, lff):
        box = path.bbox(  # get exact bounding box
            [lff.text_path_ex("1234", cap_height=3, width_factor=2)], fast=False
        )
        assert box.size.x == pytest.approx(18.189556764069664, abs=TOL)
        assert box.size.y == pytest.approx(3, abs=TOL)


def test_map_shx_to_lff():
    assert fonts.map_shx_to_lff("txt") == "standard.lff"
    assert fonts.map_shx_to_lff("txt.shx") == "standard.lff"
    assert fonts.map_shx_to_lff("iso") == "iso.lff"
    assert fonts.map_shx_to_lff("iso.shx") == "iso.lff"
    assert fonts.map_shx_to_lff("unknown.shx") == "unknown.shx"


if __name__ == "__main__":
    pytest.main([__file__])
