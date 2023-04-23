#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pytest


from ezdxf.addons.drawing.clipper import ClippingRect
from ezdxf.math import Vec2
from ezdxf.path import rect


def test_clipping_points():
    clipper = ClippingRect()
    clipper.push(rect(2, 2), None)
    assert clipper.clip_point(Vec2(3, 3)) is None
    assert clipper.clip_point(Vec2(0.5, 0.5)).isclose((0.5, 0.5))


def test_clipping_lines():
    clipper = ClippingRect()
    clipper.push(rect(2, 2), None)
    points = clipper.clip_line(Vec2(-3, 0), Vec2(3, 0))
    assert len(points) == 2
    start, end = points
    assert start.isclose((-1, 0))
    assert end.isclose((1, 0))


def test_clip_polyline():
    clipper = ClippingRect()
    clipper.push(rect(4, 4), None)
    polyline = Vec2.list([(0, 1), (3, 0), (0, -1)])
    result = clipper.clip_polygon(polyline)
    assert len(result) == 4


if __name__ == '__main__':
    pytest.main([__file__])
