#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest

from ezdxf.math import Vec2
from ezdxf.path import Path2d
from ezdxf.addons.drawing import hpgl2, layout
from ezdxf.addons.drawing.properties import BackendProperties


def test_empty_page():
    backend = hpgl2.PlotterBackend()
    backend.draw_point(Vec2(0, 0), BackendProperties())
    assert backend.get_bytes(layout.Page(0, 0)) == b""


class TestPlotterBackend:
    @pytest.fixture(scope="class")
    def properties(self):
        return BackendProperties(color="#ff0000", lineweight=0.25)

    @pytest.fixture(scope="class")
    def result1(self, properties):
        backend = hpgl2.PlotterBackend()
        backend.draw_line(Vec2(0, 0), Vec2(100, 100), properties)
        return backend.get_bytes(layout.Page(0, 0))

    def test_enter_hpgl2_mode_prefix(self,result1):
        assert result1.startswith(b"%0B;")

    def test_init_commands_exist(self, result1):
        assert b"IN;" in result1
        assert b"BP;" in result1
        assert b"PS4000,4000;" in result1  # 40 plu = 1mm

    def test_pen_color_setup_exist(self, result1):
        assert b"PC1,255,0,0;" in result1

    def test_set_pen_command_exist(self, result1):
        assert b"SP1;" in result1

    def test_pen_width_command_exist(self, result1):
        assert b"PW0.25;" in result1

    def test_lines_are_7_bit_int_base_32_polyline_encoded(self, result1):
        assert b"PE7<=__?Yf?Yf;" in result1

    def test_curves_are_ascii_encoded_relative_bezier_curves(self, properties):
        path = Path2d((0, 0))
        path.curve4_to((100, 100), (25, 0), (75, 100))
        backend = hpgl2.PlotterBackend()
        backend.draw_path(path, properties)
        result = backend.get_bytes(layout.Page(0, 0))
        assert b"PU;PA0,0;PD;BR1000,0,3000,4000,4000,4000;PU;" in result


if __name__ == '__main__':
    pytest.main([__file__])

