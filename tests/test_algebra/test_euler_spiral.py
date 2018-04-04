# Created: 28.03.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
from ezdxf.algebra.eulerspiral import EulerSpiral
from ezdxf.algebra import is_close_points, is_close

expected_points = [
    (0.0, 0.0),
    (0.4999511740825297, 0.0052079700401204106),
    (0.99843862987320509, 0.041620186803547267),
    (1.4881781381789292, 0.13983245006538086),
    (1.9505753764262783, 0.32742809475246343),
    (2.3516635639763064, 0.62320387651494735),
    (2.6419212729287223, 1.0273042715153904),
    (2.7637635905799862, 1.5086926753401932),
    (2.6704397998515645, 1.9952561538526452),
    (2.3566156629790327, 2.3766072153088964),
    (1.8936094203448928, 2.5322897289776636)
]


def test_approximate():
    spiral = EulerSpiral(2.0)
    results = spiral.approximate(5, 10)
    for expected, result in zip(expected_points, results):
        assert is_close_points(expected, result)


def test_radius():
    spiral = EulerSpiral(2.0)
    assert is_close(spiral.radius(1), 4.)
    assert is_close(spiral.radius(0), 0.)


def test_tangent():
    spiral = EulerSpiral(2.0)
    assert is_close(spiral.tangent(1).angle_rad, 0.125)


def test_distance():
    spiral = EulerSpiral(2.0)
    assert is_close(spiral.distance(10), 0.4)


def test_circle_midpoint():
    spiral = EulerSpiral(2.0)
    m = spiral.circle_midpoint(2.0)
    assert is_close_points(m, (0.9917242992178723, 2.082593218533209))


def test_as_bspline():
    spiral = EulerSpiral(2.0)
    spline = spiral.bspline(5, 10)
    assert spline.degree == 3
    assert spline.max_t == 5
    results = spline.approximate(10)
    for expected, result in zip(expected_points, results):
        assert is_close_points(expected, result)
