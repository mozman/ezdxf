# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math import is_planar_face, Vector, Vec2, subdivide_face, intersection_ray_ray_3d, normal_vector_3p
from ezdxf.math import X_AXIS, Y_AXIS, Z_AXIS
from ezdxf.render.forms import square

REGULAR_FACE = Vector.list([(0, 0, 0), (1, 0, 1), (1, 1, 1), (0, 1, 0)])
IRREGULAR_FACE = Vector.list([(0, 0, 0), (1, 0, 1), (1, 1, 0), (0, 1, 0)])
REGULAR_FACE_WRONG_ORDER = Vector.list([(0, 0, 0), (1, 1, 1), (1, 0, 1), (0, 1, 0)])


def test_face_count():
    assert is_planar_face(REGULAR_FACE[:3]) is True
    assert is_planar_face(REGULAR_FACE[:2]) is False


def test_regular_face():
    assert is_planar_face(REGULAR_FACE) is True


def test_irregular_face():
    assert is_planar_face(IRREGULAR_FACE) is False


def test_does_not_detect_wrong_order():
    assert is_planar_face(REGULAR_FACE_WRONG_ORDER) is True


def test_subdivide_square_in_quads():
    b = square(2)
    result = list(subdivide_face(b, quads=True))
    assert len(result) == 4
    assert result[0] == ((0, 0), (1, 0), (1, 1), (0, 1))


def test_subdivide_square_in_triangles():
    b = square(2)
    result = list(subdivide_face(b, quads=False))
    assert len(result) == 8
    assert result[0] == ((0, 1), (0, 0), (1, 1))
    assert result[1] == ((0, 0), (1, 0), (1, 1))


def test_subdivide_triangle():
    t = Vector.list([(0, 0), (2, 0), (1, 2)])
    assert len(list(subdivide_face(t, quads=True))) == 3
    assert len(list(subdivide_face(t, quads=False))) == 6


def test_subdivide_vec2_square_in_quads():
    b = Vec2.list(square(2))
    result = list(subdivide_face(b, quads=True))
    assert len(result) == 4
    assert result[0] == ((0, 0), (1, 0), (1, 1), (0, 1))


def test_intersection_ray_ray_3d():
    ray1 = (Vector(0, 0, 0), Vector(1, 0, 0))
    ray2 = (Vector(0, 0, 0), Vector(0, 0, 1))

    # parallel rays return a 0-tuple
    result = intersection_ray_ray_3d(ray1, ray1)
    assert len(result) == 0
    assert bool(result) is False

    # intersecting rays return a 1-tuple
    result = intersection_ray_ray_3d(ray1, ray2)
    assert len(result) == 1
    assert bool(result) is True
    assert result == (Vector(0, 0, 0),)

    # not intersecting and not parallel rays return a 2-tuple
    line3 = (Vector(0, 0, 1), Vector(0, 1, 1))
    result = intersection_ray_ray_3d(ray1, line3)
    assert len(result) == 2
    assert bool(result) is True
    # returns points of closest approach on each ray
    assert Vector(0, 0, 1) in result
    assert Vector(0, 0, 0) in result


def test_normal_vector_for_3_points():
    # normal_vector_3p(a, b, c)
    # a->b = v1
    # a->c = v2
    o = Vector(0, 0, 0)
    assert normal_vector_3p(o, X_AXIS, Y_AXIS) == Z_AXIS
    assert normal_vector_3p(o, Y_AXIS, X_AXIS) == -Z_AXIS
    assert normal_vector_3p(o, Z_AXIS, X_AXIS) == Y_AXIS
    assert normal_vector_3p(o, X_AXIS, Z_AXIS) == -Y_AXIS
    assert normal_vector_3p(o, Y_AXIS, Z_AXIS) == X_AXIS
    assert normal_vector_3p(o, Z_AXIS, Y_AXIS) == -X_AXIS


if __name__ == '__main__':
    pytest.main([__file__])
