#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest

pytest.importorskip("PyQt5")

from ezdxf.lldxf.types import dxftag, render_tag
from ezdxf.math import Vec3


class TestRenderTag:
    def test_render_string_type(self):
        tag = dxftag(1, "text")
        assert render_tag(tag, 0) == "1"
        assert render_tag(tag, 1) == "<str>"
        assert render_tag(tag, 2) == "text"

    def test_render_int_type(self):
        tag = dxftag(70, 1)
        assert render_tag(tag, 0) == "70"
        assert render_tag(tag, 1) == "<int>"
        assert render_tag(tag, 2) == "1"

    def test_render_float_type(self):
        tag = dxftag(40, 1.1)
        assert render_tag(tag, 0) == "40"
        assert render_tag(tag, 1) == "<float>"
        assert render_tag(tag, 2) == "1.1"

    def test_render_handle_type(self):
        tag = dxftag(5, "ABBA")
        assert render_tag(tag, 0) == "5"
        assert render_tag(tag, 1) == "<hex>"
        assert render_tag(tag, 2) == "ABBA"

    def test_render_ctrl_type(self):
        tag = dxftag(0, "LINE")
        assert render_tag(tag, 0) == "0"
        assert render_tag(tag, 1) == "<ctrl>"
        assert render_tag(tag, 2) == "LINE"

    def test_render_point_type(self):
        tag = dxftag(10, Vec3(1, 2, 3))
        assert render_tag(tag, 0) == "10"
        assert render_tag(tag, 1) == "<point>"
        assert render_tag(tag, 2) == "(1.0, 2.0, 3.0)"

    def test_render_binary_data_type(self):
        tag = dxftag(310, "FEFE")
        assert render_tag(tag, 0) == "310"
        assert render_tag(tag, 1) == "<bin>"
        assert render_tag(tag, 2) == "FEFE"

    def test_raise_index_error_for_invalid_column_index(self):
        tag = dxftag(1, "text")
        pytest.raises(IndexError, render_tag, tag, 3)


if __name__ == "__main__":
    pytest.main([__file__])
