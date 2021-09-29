#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import pytest
import pickle
from ezdxf.math import Vec3, Vec2, Matrix44, close_vectors

# Import from 'ezdxf.math._bezier3p' to test Python implementation
from ezdxf.math._bezier3p import Bezier3P
from ezdxf.acc import USE_C_EXT

curve_classes = [Bezier3P]
if USE_C_EXT:
    from ezdxf.acc.bezier3p import Bezier3P as CBezier3P

    curve_classes.append(CBezier3P)

DEFPOINTS2D = [(0.0, 0.0), (5.0, 5.0), (10.0, 0.0)]
DEFPOINTS3D = [(0.0, 0.0, 0.0), (50.0, 50.0, 50.0), (100.0, 0.0, 0.0)]


@pytest.fixture(params=curve_classes)
def bezier(request):
    return request.param


def test_accepts_2d_points(bezier):
    curve = bezier(DEFPOINTS2D)
    for index, chk in enumerate(Vec2.generate(POINTS2D)):
        assert curve.point(index * 0.1).isclose(chk)


def test_objects_are_immutable(bezier):
    curve = bezier(DEFPOINTS3D)
    with pytest.raises(TypeError):
        curve.control_points[0] = (1, 2, 3)


def test_approximate(bezier):
    curve = bezier(DEFPOINTS2D)
    with pytest.raises(ValueError):
        list(curve.approximate(0))
    assert list(curve.approximate(1)) == [DEFPOINTS2D[0], DEFPOINTS2D[-1]]
    assert list(curve.approximate(2)) == [
        POINTS2D[0],
        POINTS2D[5],
        POINTS2D[-1],
    ]


def test_first_derivative(bezier):
    dbcurve = bezier(DEFPOINTS2D)
    for index, chk in enumerate(Vec2.generate(TANGENTS2D)):
        assert dbcurve.tangent(index * 0.1).isclose(chk)


def test_reverse_points(bezier):
    curve = bezier(DEFPOINTS2D)
    vertices = list(curve.approximate(10))
    rev_curve = curve.reverse()
    rev_vertices = list(rev_curve.approximate(10))
    assert close_vectors(reversed(vertices), rev_vertices)


def test_transformation_interface(bezier):
    curve = bezier(DEFPOINTS3D)
    new = curve.transform(Matrix44.translate(1, 2, 3))
    assert new.control_points[0] == Vec3(DEFPOINTS3D[0]) + (1, 2, 3)
    assert (
        new.control_points[0] != curve.control_points[0]
    ), "expected a new object"


def test_transformation_returns_always_3d_curves(bezier):
    curve = bezier(DEFPOINTS2D)
    new = curve.transform(Matrix44.translate(1, 2, 3))
    assert len(new.control_points[0]) == 3


def test_flattening(bezier):
    curve = bezier(DEFPOINTS2D)
    assert len(list(curve.flattening(1.0, segments=4))) == 5
    assert len(list(curve.flattening(0.1, segments=4))) == 9


def test_approximated_length(bezier):
    length = bezier(DEFPOINTS3D).approximated_length(64)
    assert length == pytest.approx(127.12269127455725)


def test_pickle_support(bezier):
    curve = bezier(DEFPOINTS3D)
    pickled_curve = pickle.loads(pickle.dumps(curve))
    for index in range(3):
        assert pickled_curve.control_points[index] == DEFPOINTS3D[index]


POINTS2D = [
    (0.0, 0.0),
    (1.0, 0.9),
    (2.0, 1.6),
    (3.0, 2.1),
    (4.0, 2.4),
    (5.0, 2.5),
    (6.0, 2.4),
    (7.0, 2.1),
    (8.0, 1.6),
    (9.00, 0.9),
    (10.0, 0.0),
]
TANGENTS2D = [
    (10.0, 10.0),
    (10.0, 8.0),
    (10.0, 6.0),
    (10.0, 4.0),
    (10.0, 2.0),
    (10.0, 0.0),
    (10.0, -2.0),
    (10.0, -4.0),
    (10.0, -6.0),
    (10.0, -8.0),
    (10.0, -10.0),
]

if __name__ == "__main__":
    pytest.main([__file__])
