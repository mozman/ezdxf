# Copyright (c) 2019-2020 Manfred Moitzi
# License: MIT License
import pytest
import math
# Import from 'ezdxf.math._vector' to test Python implementation
from ezdxf.math._vector import Vec2, Vec3

all_vec_classes = [Vec2, Vec3]
vec2_only = [Vec2]
try:
    from ezdxf.acc.vector import Vec2 as CVec2

    all_vec_classes.append(CVec2)
    vec2_only.append(CVec2)
except ImportError:
    pass


# Vec2 is a sub set of Vec3, Vec3 can do everything Vec2 can do, but not every
# operation has the same result for 2D and 3D.
@pytest.fixture(params=all_vec_classes)
def vcls(request):
    return request.param


@pytest.fixture(params=vec2_only)
def vec2(request):
    return request.param


def test_init_tuple(vcls):
    v = vcls((2, 3))
    assert v.x == 2
    assert v.y == 3


def test_init_vec2(vcls):
    v = Vec2(vcls(2, 3))
    assert v.x == 2
    assert v.y == 3


def test_compatible_to_vector():
    v = Vec3(Vec2(1, 2))
    assert v == (1, 2, 0)

    v = Vec2(Vec3(1, 2, 3))
    assert v.x == 1
    assert v.y == 2


def test_vec3(vec2):
    v = vec2(1, 2)
    assert len(v) == 2
    v3 = v.vec3
    assert len(v3) == 3
    assert v3 == (1, 2, 0)


def test_round(vec2):
    v = vec2(1.123, 2.123)
    v2 = v.round(1)
    assert v2 == (1.1, 2.1)


def test_from_angle(vcls):
    angle = math.radians(50)
    length = 3.
    assert vcls.from_angle(angle, length) == vcls(
        (math.cos(angle) * length, math.sin(angle) * length))


def test_vec2_as_tuple(vec2):
    v = vec2(1, 2)
    assert v[0] == 1
    assert v[1] == 2

    with pytest.raises(IndexError):
        _ = v[2]
    # negative indices not supported
    with pytest.raises(IndexError):
        _ = v[-1]


def test_iter(vcls):
    assert sum(vcls(1, 2)) == 3


def test_deep_copy():
    import copy

    v = Vec2(1, 2)
    l1 = [v, v, v]
    l2 = copy.copy(l1)
    assert l2[0] is l2[1]
    assert l2[1] is l2[2]
    assert l2[0] is v

    # Vec3, CVec2 and CVec3 are immutable and do not create copies of itself!
    l3 = copy.deepcopy(l1)
    assert l3[0] is l3[1]
    assert l3[1] is l3[2]
    assert l3[0] is not v


def test_get_angle(vcls):
    v = vcls(3, 3)
    assert math.isclose(v.angle_deg, 45)
    assert math.isclose(v.angle, math.radians(45))


def test_compare_vectors(vcls):
    v1 = vcls(1, 2)
    assert v1 == v1

    v2 = vcls(2, 3)
    assert v2 > v1
    assert v1 < v2


def test_is_close(vcls):
    v1 = vcls(421846.9857097387, -36908.41493252139)
    v2 = vcls(421846.9857097387, -36908.41493252141)
    assert v1.isclose(v2) is True


def test_is_null(vcls):
    v = vcls(0, 0)
    assert v.is_null is True

    v1 = vcls(23.56678, 56678.56778) * (1.0 / 14.5667)
    v2 = vcls(23.56678, 56678.56778) / 14.5667
    assert (v2 - v1).is_null


def test_bool(vcls):
    v = vcls((0, 0))
    assert bool(v) is False

    v1 = vcls(23.56678, 56678.56778) * (1.0 / 14.5667)
    v2 = vcls(23.56678, 56678.56778) / 14.5667
    result = v2 - v1
    assert bool(result) is False
    # current rel_tol=1e-9
    assert not vcls(1e-8, 0).is_null


def test_magnitude(vcls):
    v = vcls(3, 4)
    assert math.isclose(abs(v), 5)
    assert math.isclose(v.magnitude, 5)


def test_normalize(vcls):
    v = vcls(2, 0)
    assert v.normalize() == (1, 0)


def test_normalize_to_length(vcls):
    v = vcls(2, 0)
    assert v.normalize(4) == (4, 0)


def test_orthogonal_ccw(vcls):
    v = vcls(3, 4)
    assert v.orthogonal() == (-4, 3)


def test_orthogonal_cw(vcls):
    v = vcls(3, 4)
    assert v.orthogonal(False) == (4, -3)


def test_negative(vcls):
    v = vcls(2, 3)
    assert -v == (-2, -3)


def test_add_vector(vcls):
    assert vcls(2, 3) + vcls(7, 7) == (9, 10)


def test_add_vec3(vec2):
    assert vec2(2, 3) + Vec3(7, 7) == (9, 10)


def test_iadd_vector(vec2):
    v = Vec2(2, 3)
    v += Vec2(7, 7)
    assert v == (9, 10)


def test_add_scalar_type_erorr(vcls):
    with pytest.raises(TypeError):
        vcls(1, 1) + 1


def test_iadd_scalar_type_error(vcls):
    v = vcls(2, 3)
    with pytest.raises(TypeError):
        v += 1


def test_radd_scalar_type_error(vcls):
    with pytest.raises(TypeError):
        1 + vcls(1, 1)


def test_radd_tuple_type_error(vec2):
    with pytest.raises(TypeError):
        (1, 1) + vec2(1, 1)


def test_sub_vector(vcls):
    assert vcls(2, 3) - vcls(7, 7) == (-5, -4)


def test_isub_vector(vec2):
    v = Vec2(2, 3)
    v -= Vec2(7, 7)
    assert v == (-5, -4)


def test_sub_vec3(vec2):
    assert vec2(2, 3) - Vec3(7, 7) == (-5, -4)


def test_sub_scalar_type_error(vcls):
    with pytest.raises(TypeError):
        vcls(1, 1) - 1


def test_isub_scalar_type_erorr(vcls):
    v = vcls(2, 3)
    with pytest.raises(TypeError):
        v -= 1


def test_rsub_tuple(vec2):
    with pytest.raises(TypeError):
        (2, 3) - vec2(7, 7)


def test_rsub_scalar_type_error(vcls):
    with pytest.raises(TypeError):
        1 - vcls(1, 1)


def test_mul_scalar(vcls):
    v = vcls(2, 3)
    assert v * 2 == (4, 6)


def test_imul_scalar(vcls):
    v = vcls(2, 3)
    v *= 2
    assert v == (4, 6)


def test_rmul_scalar(vcls):
    assert 2 * vcls(2, 3) == (4, 6)


def test_mul_tuple_type_error(vcls):
    with pytest.raises(TypeError):
        vcls(2, 3) * (2, 2)


def test_rmul_tuple_type_error(vcls):
    with pytest.raises(TypeError):
        (2, 2) * vcls(2, 3)


def test_imul_tuple_type_error(vcls):
    v = vcls(2, 3)
    with pytest.raises(TypeError):
        v *= (2, 2)


def test_div_scalar(vcls):
    v = vcls(2, 3)
    assert v / 2 == (1, 1.5)


def test_idiv_scalar(vcls):
    v = vcls(2, 3)
    v /= 2
    assert v == (1, 1.5)


def test_dot_product(vcls):
    v1 = vcls(2, 7)
    v2 = vcls(3, 9)
    assert math.isclose(v1.dot(v2), 69)


def test_angle_deg(vcls):
    assert math.isclose(vcls((0, 1)).angle_deg, 90)
    assert math.isclose(vcls((0, -1)).angle_deg, -90)
    assert math.isclose(vcls((1, 1)).angle_deg, 45)
    assert math.isclose(vcls((-1, 1)).angle_deg, 135)


def test_angle_between(vcls):
    v1 = vcls(0, 1)
    v2 = vcls(1, 1)
    angle = v1.angle_between(v2)
    assert math.isclose(angle, math.pi / 4)
    # reverse order, same result
    angle = v2.angle_between(v1)
    assert math.isclose(angle, math.pi / 4)


@pytest.mark.parametrize('v1, v2', [
    [(1, 0), (0, 0)],
    [(0, 0), (1, 0)],
    [(0, 0), (0, 0)],
])
def test_angle_between_null_vector(vcls, v1, v2):
    with pytest.raises(ZeroDivisionError):
        vcls(v1).angle_between(vcls(v2))


def test_angle_between_outside_domain():
    v1 = Vec3(721.046967113573, 721.0469671135688, 0.0)
    v2 = Vec3(-721.0469671135725, -721.0469671135688, 0.0)
    angle = v1.angle_between(v2)
    assert math.isclose(angle, math.pi)
    # reverse order, same result
    angle = v2.angle_between(v1)
    assert math.isclose(angle, math.pi)


def test_rotate(vcls):
    assert vcls(2, 2).rotate_deg(90) == (-2, 2)


def test_lerp(vcls):
    v1 = vcls(1, 1)
    v2 = vcls(4, 4)
    assert v1.lerp(v2, .5) == (2.5, 2.5)
    assert v1.lerp(v2, 0) == (1, 1)
    assert v1.lerp(v2, 1) == (4, 4)


def test_project(vcls):
    v = vcls(10, 0)
    assert v.project(vcls(5, 0)) == (5, 0)
    assert v.project(vcls(5, 5)) == (5, 0)
    assert v.project(vcls(5, 5)) == (5, 0)

    v = vcls(10, 10)
    assert v.project(vcls(10, 0)) == (5, 5)


def test_det(vec2):
    assert vec2(1, 0).det(vec2(0, 1)) == 1
    assert vec2(0, 1).det(vec2(1, 0)) == -1


def test_sum(vcls):
    assert vcls.sum([]).is_null is True
    assert vcls.sum([vcls(1, 1)]) == (1, 1)
    assert vcls.sum([vcls(1, 1), vcls(2, 2)]) == (3, 3)
