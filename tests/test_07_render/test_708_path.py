# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

import pytest
import math
from ezdxf.render.path import Path, Command
from ezdxf.math import Vector, Matrix44, Bezier4P


def test_init():
    path = Path()
    assert path.start == (0, 0)
    assert len(path) == 0
    assert path.end == (0, 0)


def test_init_start():
    path = Path(start=(1, 2))
    assert path.start == (1, 2)


def test_line_to():
    path = Path()
    path.line_to((1, 2, 3))
    assert path[0] == (Command.LINE, Vector(1, 2, 3))
    assert path.end == (1, 2, 3)


def test_curve_to():
    path = Path()
    path.curve_to((1, 2, 3), (0, 1, 0), (0, 2, 0))
    assert path[0] == (Command.CUBIC, (1, 2, 3), (0, 1, 0), (0, 2, 0))
    assert path.end == (1, 2, 3)


def test_add_curves():
    path = Path()
    c1 = Bezier4P(((0, 0, 0), (0, 1, 0), (2, 1, 0), (2, 0, 0)))
    c2 = Bezier4P(((2, 0, 0), (2, -1, 0), (0, -1, 0), (0, 0, 0)))
    path.add_curves([c1, c2])
    assert len(path) == 2
    assert path.end == (0, 0, 0)


def test_add_curves_with_gap():
    path = Path()
    c1 = Bezier4P(((0, 0, 0), (0, 1, 0), (2, 1, 0), (2, 0, 0)))
    c2 = Bezier4P(((2, -1, 0), (2, -2, 0), (0, -2, 0), (0, -1, 0)))
    path.add_curves([c1, c2])
    assert len(path) == 3  # added a line segment between curves
    assert path.end == (0, -1, 0)


def test_add_curves_reverse():
    path = Path(start=(0, 0, 0))
    c1 = Bezier4P(((2, 0, 0), (2, 1, 0), (0, 1, 0), (0, 0, 0)))
    path.add_curves([c1])
    assert len(path) == 1
    assert path.end == (2, 0, 0)


def test_add_spline():
    from ezdxf.math import BSpline
    spline = BSpline.from_fit_points([(2, 0), (4, 1), (6, -1), (8, 0)])
    path = Path()
    path.add_spline(spline)
    assert path.start == (2, 0)
    assert path.end == (8, 0)

    # set start point to end of spline
    path = Path(start=(8, 0))
    # add reversed spline, by default the start of
    # an empty path is set to the spline start
    path.add_spline(spline, reset=False)
    assert path.start == (8, 0)
    assert path.end == (2, 0)

    path = Path()
    # add a line segment from (0, 0) to start of spline
    path.add_spline(spline, reset=False)
    assert path.start == (0, 0)
    assert path.end == (8, 0)


def test_add_ellipse():
    from ezdxf.math import ConstructionEllipse
    ellipse = ConstructionEllipse(center=(3, 0), major_axis=(1, 0), ratio=0.5,
                                  start_param=0, end_param=math.pi)
    path = Path()
    path.add_ellipse(ellipse)
    assert path.start == (4, 0)
    assert path.end == (2, 0)

    # set start point to end of ellipse
    path = Path(start=(2, 0))
    # add reversed ellipse, by default the start of
    # an empty path is set to the ellipse start
    path.add_ellipse(ellipse, reset=False)
    assert path.start == (2, 0)
    assert path.end == (4, 0)

    path = Path()
    # add a line segment from (0, 0) to start of ellipse
    path.add_ellipse(ellipse, reset=False)
    assert path.start == (0, 0)
    assert path.end == (2, 0)


def test_approximate_lines():
    path = Path()
    path.line_to((1, 1))
    path.line_to((2, 0))
    vertices = list(path.approximate())
    assert len(vertices) == 3
    assert vertices[0] == path.start == (0, 0)
    assert vertices[2] == path.end == (2, 0)


def test_approximate_curves():
    path = Path()
    path.curve_to((2, 0), (0, 1), (2, 1))
    vertices = list(path.approximate(10))
    assert len(vertices) == 11
    assert vertices[0] == (0, 0)
    assert vertices[-1] == (2, 0)


def test_approximate_line_curves():
    path = Path()
    path.line_to((2, 0))
    path.curve_to((4, 0), (2, 1), (4, 1))
    vertices = list(path.approximate(10))
    assert len(vertices) == 12
    assert vertices[0] == (0, 0)
    assert vertices[1] == (2, 0)
    assert vertices[-1] == (4, 0)


def test_transform():
    path = Path()
    path.line_to((2, 0))
    path.curve_to((4, 0), (2, 1), (4, 1))
    p2 = path.transform(Matrix44.translate(1, 1, 0))
    assert p2.start == (1, 1)
    assert p2[0][1] == (3, 1)  # line to location
    assert p2[1][1] == (5, 1)  # cubic to location
    assert p2[1][2] == (3, 2)  # cubic ctrl1
    assert p2[1][3] == (5, 2)  # cubic ctrl2
    assert p2.end == (5, 1)


if __name__ == '__main__':
    pytest.main([__file__])
