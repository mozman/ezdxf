import sys
import pytest
import math

from ezdxf.algebra.vector import Vector, is_close
PY3 = sys.version_info.major > 2


def test_init_no_params():
    v = Vector()
    assert v == (0, 0, 0)
    assert v == Vector()


def test_init_one_param():
    v = Vector((2, 3))
    assert v == (2, 3)  # z is 0.

    v = Vector((2, 3, 4))
    assert v == (2, 3, 4)  # z is 0.


def test_init_two_params():
    v = Vector(1, 2)
    assert v == (1, 2)  # z is 0.

    v = Vector((1, 1, 1), (5, 6, 7))
    assert v == (4, 5, 6)

    v = Vector.from_deg_angle(0)
    assert v == (1, 0)

    length, angle = 7, 45
    v = Vector.from_deg_angle(angle, length)
    x = math.cos(math.radians(angle)) * length
    y = math.sin(math.radians(angle)) * length
    assert v == (x, y)


def test_init_three_params():
    v = Vector(1, 2, 3)
    assert v == (1, 2, 3)


def test_from_angle():
    angle = math.radians(50)
    length = 3.
    assert Vector.from_rad_angle(angle, length) == (math.cos(angle)*length, math.sin(angle)*length, 0)


def test_vector_as_tuple():
    v = Vector(1, 2, 3)
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3
    assert tuple(v) == (1, 2, 3)


def test_iter():
    assert sum(Vector(1, 2, 3)) == 6


def test_deep_copy():
    import copy

    v = Vector(1, 2, 3)
    l1 = [v, v, v]
    l2 = copy.copy(l1)
    assert l2[0] is l2[1]
    assert l2[1] is l2[2]
    assert l2[0] is v

    l3 = copy.deepcopy(l1)
    assert l3[0] is l3[1]
    assert l3[1] is l3[2]
    assert l3[0] is not v


def test_get_angle():
    v = Vector(3, 3)
    assert is_close(v.angle_deg, 45)
    assert is_close(v.angle_rad, math.radians(45))


def test_spatial_angle():
    v = Vector(3, 3, 0)
    assert is_close(v.spatial_angle_deg, 45)
    assert is_close(v.spatial_angle_rad, math.radians(45))


def test_compare_vectors():
    v1 = Vector(1, 2, 3)

    # compare to tuple
    assert v1 == (1, 2, 3)
    # compare tuple to vector
    assert (1, 2, 3) == v1

    v2 = Vector(2, 3, 4)
    assert v2 > v1
    assert v1 < v2


def test_xy():
    assert Vector(1, 2, 3).xy == Vector(1, 2)


def test_is_null():
    v = Vector()
    assert v.is_null

    v1 = Vector(23.56678, 56678.56778, 2.56677) * (1.0 / 14.5667)
    v2 = Vector(23.56678, 56678.56778, 2.56677) / 14.5667
    result = v2 - v1
    assert Vector(0, 0, 0).is_null


@pytest.mark.skipif(not PY3, reason="__bool__ not supported")
def test_bool():
    v = Vector()
    assert bool(v) is False

    v1 = Vector(23.56678, 56678.56778, 2.56677) * (1.0 / 14.5667)
    v2 = Vector(23.56678, 56678.56778, 2.56677) / 14.5667
    result = v2 - v1
    assert bool(result) is False
    # actual precision is abs_tol=1e-9
    assert not Vector(1e-8, 0, 0).is_null


def test_magnitude():
    v = Vector(3, 4, 5)
    assert is_close(abs(v), 7.0710678118654755)
    assert is_close(v.magnitude, 7.0710678118654755)


def test_magnitude_square():
    v = Vector(3, 4, 5)
    assert is_close(v.magnitude_square, 50)


def test_normalize():
    v = Vector(2, 0, 0)
    assert v.normalize() == (1, 0, 0)


def test_normalize_to_length():
    v = Vector(2, 0, 0)
    assert v.normalize(4) == (4, 0, 0)


def test_orthogonal_ccw():
    v = Vector(3, 4)
    assert v.orthogonal() == (-4, 3)


def test_orthogonal_cw():
    v = Vector(3, 4)
    assert v.orthogonal(False) == (4, -3)


def test_negative():
    v = Vector(2, 3, 4)
    assert -v == (-2, -3, -4)


def test_add_scalar():
    v = Vector(2, 3, 4)
    assert v + 3 == (5, 6, 7)


def test_iadd_scalar():
    v = Vector(2, 3, 4)
    v += 3
    assert v == (5, 6, 7)


def test_sub_scalar():
    v = Vector(2, 3, 4)
    assert v - 3 == (-1, 0, 1)


def test_isub_scalar():
    v = Vector(2, 3, 4)
    v -= 3
    assert v == (-1, 0, 1)


def test_add_vector():
    v = Vector(2, 3, 4)
    assert v + (7, 7, 7) == (9, 10, 11)


def test_iadd_vector():
    v = Vector(2, 3, 4)
    v += (7, 7, 7)
    assert v == (9, 10, 11)


def test_radd_vector():
    v = Vector(2, 3, 4)
    assert (7, 7, 7) + v == (9, 10, 11)


def test_sub_vector():
    v = Vector(2, 3, 4)
    assert v - (7, 7, 7) == (-5, -4, -3)


def test_isub_vector():
    v = Vector(2, 3, 4)
    v -= (7, 7, 7)
    assert v == (-5, -4, -3)


def test_rsub_vector():
    v = Vector(2, 3, 4)
    assert (7, 7, 7) - v == (5, 4, 3)


def test_mul_scalar():
    v = Vector(2, 3, 4)
    assert v * 2 == (4, 6, 8)


def test_imul_scalar():
    v = Vector(2, 3, 4)
    v *= 2
    assert v == (4, 6, 8)


def test_rmul_scalar():
    v = Vector(2, 3, 4)
    assert 2 * v == (4, 6, 8)


def test_div_scalar():
    v = Vector(2, 3, 4)
    assert v / 2 == (1, 1.5, 2)


def test_idiv_scalar():
    v = Vector(2, 3, 4)
    v /= 2
    assert v == (1, 1.5, 2)


def test_rdiv_scalar():
    v = Vector(2, 3, 4)
    assert 2 / v == (1, 0.66666666667, 0.5)


def test_dot_product():
    v1 = Vector(2, 7, 1)
    v2 = Vector(3, 9, 8)
    assert is_close(v1.dot(v2), 77)


def test_angle_deg():
    assert is_close(Vector(0, 1).angle_deg, 90)
    assert is_close(Vector(0, -1).angle_deg, -90)
    assert is_close(Vector(1, 1).angle_deg, 45)
    assert is_close(Vector(-1, 1).angle_deg, 135)


def test_angle_between():
    v1 = Vector(0, 1)
    v2 = Vector(1, 1)
    angle = v1.angle_between(v2)
    assert is_close(angle, math.pi/4)
    # reverse order, same result
    angle = v2.angle_between(v1)
    assert is_close(angle, math.pi/4)


def test_cross_product():
    v1 = Vector(2, 7, 9)
    v2 = Vector(3, 9, 1)
    assert v1.cross(v2) == (-74, 25, -3)


def test_rot_z():
    assert Vector(2, 2, 7).rot_z_deg(90) == (-2, 2, 7)


def test_lerp():
    v1 = Vector(1, 1, 1)
    v2 = Vector(4, 4, 4)
    assert v1.lerp(v2, .5) == (2.5, 2.5, 2.5)
    assert v1.lerp(v2, 0) == (1, 1, 1)
    assert v1.lerp(v2, 1) == (4, 4, 4)

