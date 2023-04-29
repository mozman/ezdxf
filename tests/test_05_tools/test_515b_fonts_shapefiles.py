#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.fonts import fonts

if not fonts.font_manager.has_font("txt.shx"):
    pytest.skip(
        reason="required shapefile fonts are not available", allow_module_level=True
    )


def test_get_font_family_for_shx_files():
    font_face = fonts.font_manager.get_font_face("txt.shx")
    assert font_face.family == "txt"


def test_get_font_family_for_shp_files():
    font_face = fonts.font_manager.get_font_face("txt.shp")
    assert font_face.family == "txt"


def test_get_font_family_for_lff_files():
    # LibreCAD does not include a replacement font for TXT
    font_face = fonts.font_manager.get_font_face("iso.lff")
    assert font_face.family == "iso"


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
    fm = fonts.font_manager
    font_face = fonts.find_best_match(family="iso", width=5)
    assert font_face.filename == "ISO.shx"
    assert font_face.style == ".shx"

    font_face = fonts.find_best_match(family="iso", width=6)
    assert font_face.style == ".shp"

    font_face = fonts.find_best_match(family="iso", width=7)
    assert font_face.style == ".lff"


if __name__ == "__main__":
    pytest.main([__file__])
