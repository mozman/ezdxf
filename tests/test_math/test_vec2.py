import math
from ezdxf.math.vec2 import Vec2


def V2(x, y):
    return Vec2((x, y))


def test_init_tuple():
    v = Vec2((2, 3))
    assert v.x == 2
    assert v.y == 3


def test_init_vec2():
    v = Vec2(V2(2, 3))
    assert v.x == 2
    assert v.y == 3


def test_compatible_to_vector():
    from ezdxf.math.vector import Vector
    v = Vector(Vec2((1, 2)))
    assert v == (1, 2, 0)

    v = Vec2(Vector(1, 2, 3))
    assert v.x == 1
    assert v.y == 2


def test_from_angle():
    angle = math.radians(50)
    length = 3.
    assert Vec2.from_angle(angle, length) == Vec2((math.cos(angle) * length, math.sin(angle) * length))


def test_vector_as_tuple():
    v = Vec2((1, 2))
    assert v[0] == 1
    assert v[1] == 2
    assert tuple(v) == (1, 2)

    assert isinstance(v[:2], tuple)
    assert v[:] == (1, 2)


def test_iter():
    assert sum(Vec2((1, 2))) == 3


def test_deep_copy():
    import copy

    v = Vec2((1, 2))
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
    v = Vec2((3, 3))
    assert math.isclose(v.angle_deg, 45)
    assert math.isclose(v.angle, math.radians(45))


def test_compare_vectors():
    v1 = Vec2((1, 2))
    assert v1 == v1

    v2 = Vec2((2, 3))
    assert v2 > v1
    assert v1 < v2


def test_is_null():
    v = Vec2((0, 0))
    assert v.is_null

    v1 = Vec2((23.56678, 56678.56778)) * (1.0 / 14.5667)
    v2 = Vec2((23.56678, 56678.56778)) / 14.5667
    assert (v2 - v1).is_null


def test_bool():
    v = Vec2((0, 0))
    assert bool(v) is False

    v1 = Vec2((23.56678, 56678.56778)) * (1.0 / 14.5667)
    v2 = Vec2((23.56678, 56678.56778)) / 14.5667
    result = v2 - v1
    assert bool(result) is False
    # actual precision is abs_tol=1e-9
    assert not Vec2((1e-8, 0)).is_null


def test_magnitude():
    v = Vec2((3, 4))
    assert math.isclose(abs(v), 5)
    assert math.isclose(v.magnitude, 5)


def test_normalize():
    v = Vec2((2, 0))
    assert v.normalize() == (1, 0)


def test_normalize_to_length():
    v = Vec2((2, 0))
    assert v.normalize(4) == (4, 0)


def test_orthogonal_ccw():
    v = Vec2((3, 4))
    assert v.orthogonal() == (-4, 3)


def test_orthogonal_cw():
    v = Vec2((3, 4))
    assert v.orthogonal(False) == (4, -3)


def test_negative():
    v = Vec2((2, 3))
    assert -v == (-2, -3)


def test_add_scalar():
    v = Vec2((2, 3))
    assert v + 3 == (5, 6)


def test_iadd_scalar():
    v = Vec2((2, 3))
    v1 = v
    v += 3
    assert v == (5, 6)
    assert v1 == (5, 6)
    assert v is v1


def test_sub_scalar():
    v = Vec2((2, 3))
    assert v - 3 == (-1, 0)


def test_isub_scalar():
    v = Vec2((2, 3))
    v1 = v
    v -= 3
    assert v == (-1, 0)
    assert v1 == (-1, 0)
    assert v1 is v


def test_add_vector():
    v = Vec2((2, 3))
    assert v + V2(7, 7) == (9, 10)


def test_iadd_vector():
    v = Vec2((2, 3))
    v1 = v
    v += V2(7, 7)
    assert v == (9, 10)
    assert v1 == (9, 10)
    assert v1 is v


def test_radd_vector():
    v = Vec2((2, 3))
    assert 7 + v == (9, 10)


def test_sub_vector():
    v = Vec2((2, 3))
    assert v - V2(7, 7) == (-5, -4)


def test_isub_vector():
    v = Vec2((2, 3))
    v1 = v
    v -= V2(7, 7)
    assert v == (-5, -4)
    assert v1 == (-5, -4)
    assert v1 is v


def test_rsub_vector():
    v = Vec2((2, 3))
    assert 7 - v == (5, 4)


def test_mul_scalar():
    v = Vec2((2, 3))
    assert v * 2 == (4, 6)


def test_imul_scalar():
    v = Vec2((2, 3))
    v1 = v
    v *= 2
    assert v == (4, 6)
    assert v1 == (4, 6)
    assert v1 is v


def test_rmul_scalar():
    v = Vec2((2, 3))
    assert 2 * v == (4, 6)


def test_div_scalar():
    v = Vec2((2, 3))
    assert v / 2 == (1, 1.5)


def test_idiv_scalar():
    v = Vec2((2, 3))
    v1 = v
    v /= 2
    assert v == (1, 1.5)
    assert v1 == (1, 1.5)
    assert v1 is v


def test_rdiv_scalar():
    v = Vec2((2, 3))
    assert 2 / v == (1, 0.66666666667)


def test_dot_product():
    v1 = Vec2((2, 7))
    v2 = Vec2((3, 9))
    assert math.isclose(v1.dot(v2), 69)


def test_angle_deg():
    assert math.isclose(V2(0, 1).angle_deg, 90)
    assert math.isclose(V2(0, -1).angle_deg, -90)
    assert math.isclose(V2(1, 1).angle_deg, 45)
    assert math.isclose(V2(-1, 1).angle_deg, 135)


def test_angle_between():
    v1 = V2(0, 1)
    v2 = V2(1, 1)
    angle = v1.angle_between(v2)
    assert math.isclose(angle, math.pi / 4)
    # reverse order, same result
    angle = v2.angle_between(v1)
    assert math.isclose(angle, math.pi / 4)


def test_rottate():
    assert V2(2, 2).rotate_deg(90) == (-2, 2)


def test_lerp():
    v1 = V2(1, 1)
    v2 = V2(4, 4)
    assert v1.lerp(v2, .5) == (2.5, 2.5)
    assert v1.lerp(v2, 0) == (1, 1)
    assert v1.lerp(v2, 1) == (4, 4)


def test_project():
    v = V2(10, 0)
    assert v.project(V2(5, 0)) == (5, 0)
    assert v.project(V2(5, 5)) == (5, 0)
    assert v.project(V2(5, 5)) == (5, 0)

    v = V2(10, 10)
    assert v.project(V2(10, 0)) == (5, 5)
