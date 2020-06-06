# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
# created 2019-03-06
import pytest
import math

import ezdxf
from ezdxf.entities.spline import Spline
from ezdxf.lldxf.tagwriter import TagCollector, basic_tags_from_text
from ezdxf.math import Vector, Matrix44

SPLINE = """0
SPLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbSpline
70
0
71
3
72
0
73
0
74
0
"""


def test_registered():
    from ezdxf.entities.factory import ENTITY_CLASSES
    assert 'SPLINE' in ENTITY_CLASSES


def test_default_init():
    entity = Spline()
    assert entity.dxftype() == 'SPLINE'
    assert entity.dxf.handle is None
    assert entity.dxf.owner is None


def test_default_new():
    entity = Spline.new(handle='ABBA', owner='0', dxfattribs={
        'color': 7,
        'flags': 4,
        'degree': 4,
        'knot_tolerance': 42,
        'control_point_tolerance': 43,
        'fit_tolerance': 44,
        'start_tangent': (1, 2, 3),
        'end_tangent': (4, 5, 6),
        'extrusion': (7, 8, 9),

    })
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 7
    assert entity.dxf.flags == 4
    assert entity.dxf.degree == 4
    assert entity.dxf.knot_tolerance == 42
    assert entity.dxf.control_point_tolerance == 43
    assert entity.dxf.fit_tolerance == 44
    assert entity.dxf.start_tangent == (1, 2, 3)
    assert entity.dxf.end_tangent == (4, 5, 6)
    assert entity.dxf.extrusion == (7, 8, 9)


def test_load_from_text():
    entity = Spline.from_text(SPLINE)
    assert entity.dxf.layer == '0'
    assert entity.dxf.color == 256, 'default color is 256 (by layer)'
    assert entity.dxf.extrusion == (0, 0, 1)
    assert entity.dxf.flags == 0
    assert entity.dxf.degree == 3
    assert entity.dxf.n_knots == 0
    assert entity.dxf.n_control_points == 0
    assert entity.dxf.n_fit_points == 0


def test_write_dxf():
    entity = Spline.from_text(SPLINE2)
    result = TagCollector.dxftags(entity)
    expected = basic_tags_from_text(SPLINE2)
    assert cmp_tags(result, expected, abs_tol=1e-4) == 0


def cmp_tags(result, expected, abs_tol=1e-6):
    if len(result) != len(expected):
        return -1
    pos = 0
    for r, e in zip(result, expected):
        rc, rv = r
        ec, ev = e
        if rc != ec:
            return pos
        if isinstance(rv, float):
            if not math.isclose(rv, ev, abs_tol=abs_tol):
                return pos
        elif rv != ev:
            return pos
        pos += 1
    return 0


@pytest.fixture
def spline():
    return Spline.from_text(SPLINE)


@pytest.fixture
def points():
    return [(1., 1., 0.), (2.5, 3., 0.), (4.5, 2., 0), (6.5, 4., 0)]


@pytest.fixture
def weights():
    return [1, 2, 3, 4]


def test_start_tangent(spline):
    spline = spline
    spline.dxf.start_tangent = (1, 2, 3)
    assert (1, 2, 3) == spline.dxf.start_tangent


def test_end_tangent(spline):
    spline = spline
    spline.dxf.end_tangent = (4, 5, 6)
    assert (4, 5, 6) == spline.dxf.end_tangent


def test_knot_values(spline):
    spline = spline
    values = [1, 2, 3, 4, 5, 6, 7]
    spline.knots = values
    assert 7 == spline.dxf.n_knots
    assert values == list(spline.knots)


def test_weights(spline):
    spline = spline
    weights = [1, 2, 3, 4, 5, 6, 7]
    spline.weights = weights
    assert weights == list(spline.weights)


def test_control_points(spline, points):
    spline.control_points = points
    assert spline.dxf.n_control_points == 4
    assert points == list(spline.control_points)


def test_fit_points(spline, points):
    spline.fit_points = points
    assert spline.dxf.n_fit_points == 4
    assert points == list(spline.fit_points)


def test_set_open_uniform(spline, points):
    spline.set_open_uniform(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_uniform(spline, points):
    spline.set_uniform(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_periodic(spline, points):
    spline.set_periodic(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


def test_set_open_rational(spline, points, weights):
    spline.set_open_rational(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert list(spline.weights) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.weights) == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_uniform_rational(spline, points, weights):
    spline.set_uniform_rational(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert list(spline.weights) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.weights) == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_set_periodic_rational(spline, points, weights):
    spline.set_periodic_rational(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert list(spline.weights) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.weights) == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


@pytest.fixture(scope='module')
def msp():
    doc = ezdxf.new('R2000')
    return doc.modelspace()


def test_open_spline(msp, points):
    spline = msp.add_open_spline(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_closed_spline(msp, points):
    spline = msp.add_closed_spline(points, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert spline.dxf.n_control_points == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


def test_open_rational_spline(msp, points, weights):
    spline = msp.add_rational_spline(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert list(spline.weights) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.weights) == len(points)
    assert spline.dxf.n_knots == len(points) + spline.dxf.degree + 1  # n + p + 2
    assert spline.closed is False


def test_closed_rational_spline(msp, points, weights):
    spline = msp.add_closed_rational_spline(points, weights, degree=3)
    assert spline.dxf.degree == 3
    assert list(spline.control_points) == points
    assert list(spline.weights) == weights
    assert spline.dxf.n_control_points == len(points)
    assert len(spline.weights) == len(points)
    assert spline.dxf.n_knots == len(points) + 1  # according the Autodesk developer documentation
    assert spline.closed is True


def test_spline_transform_interface():
    spline = Spline()
    spline.set_uniform([(1, 0, 0), (3, 3, 0), (6, 0, 1)])
    spline.dxf.start_tangent = Vector(1, 0, 0)
    spline.dxf.end_tangent = Vector(2, 0, 0)
    spline.dxf.extrusion = Vector(3, 0, 0)
    spline.transform(Matrix44.translate(1, 2, 3))
    assert spline.control_points[0] == (2, 2, 3)
    # direction vectors are not transformed by translation
    assert spline.dxf.start_tangent == (1, 0, 0)
    assert spline.dxf.end_tangent == (2, 0, 0)
    assert spline.dxf.extrusion == (3, 0, 0)


SPLINE2 = """  0
SPLINE
  5
95
330
1F
100
AcDbEntity
  8
0
100
AcDbSpline
210
0.0
220
0.0
230
1.0
 70
  1064
 71
     3
 72
    13
 73
     9
 74
     7
 42
0.000000001
 43
0.0000000001
 44
0.0
 40
0.0
 40
0.0
 40
0.0
 40
0.0
 40
127.1219886565656
 40
245.5280695814911
 40
411.2748644222964
 40
568.8185091687602
 40
643.1421258730084
 40
742.177473098128
 40
742.177473098128
 40
742.177473098128
 40
742.177473098128
 10
226.0
 20
276.0
 30
0.0
 10
175.2490432562881
 20
266.5994639691058
 30
0.0
 10
77.22678471247674
 20
248.4429240259472
 30
0.0
 10
139.5678769445405
 20
69.31979038269674
 30
0.0
 10
292.532981827299
 20
56.54395007082465
 30
0.0
 10
442.5199073432509
 20
34.24994434874142
 30
0.0
 10
505.7887841571028
 20
159.181589221269
 30
0.0
 10
446.0991144985865
 20
192.7966266652906
 30
0.0
 10
412.0
 20
212.0
 30
0.0
 11
226.0
 21
276.0
 31
0.0
 11
110.0
 21
224.0
 31
0.0
 11
142.0
 21
110.0
 31
0.0
 11
298.0
 21
54.0
 31
0.0
 11
454.0
 21
76.0
 31
0.0
 11
484.0
 21
144.0
 31
0.0
 11
412.0
 21
212.0
 31
0.0
"""
