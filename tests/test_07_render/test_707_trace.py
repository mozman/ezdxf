# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.render.trace import TraceBuilder
from ezdxf.math import BSpline


def test_trace_builder_init():
    t = TraceBuilder()
    assert len(t) == 0


def test_add_station_2d():
    t = TraceBuilder()
    t.add_station((0, 0), 1, 2)
    assert len(t) == 1
    assert t[0].vertex == (0, 0)
    assert t[0].start_width == 1
    assert t[0].end_width == 2
    t.add_station((1, 0), 1)
    assert len(t) == 2
    assert t[1].vertex == (1, 0)
    assert t[1].start_width == 1
    assert t[1].end_width == 1


def test_add_station_3d():
    # z-axis is ignored
    t = TraceBuilder()
    t.add_station((0, 0, 0), 1, 2)
    assert t[0].vertex == (0, 0)


def test_add_spline_segment():
    t = TraceBuilder()
    t.add_station((0, 0), 1)
    t.add_station((1, 0), 1)
    assert len(t) == 2
    t.add_spline(BSpline.from_fit_points([(1, 0), (3, 1), (5, -1), (6, 0)]), start_width=2, end_width=1, segments=10)
    assert len(t) == 12
    assert t.last_station.vertex == (6, 0)  # last vertex
    assert math.isclose(t.last_station.start_width, 1.0)
    assert math.isclose(t.last_station.end_width, 1.0)
    # last station connects to following station with
    # end width of spline, the following element
    # (line, spline) should start at the last spline vertex
    # and replaces the actual last_station.


if __name__ == '__main__':
    pytest.main([__file__])
