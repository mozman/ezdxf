# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
# Import from 'ezdxf.math.vector' to test Python implementation
from ezdxf.math.vector import Vec3

vec3_classes = [Vec3]


@pytest.fixture(params=vec3_classes)
def vec3(request):
    return request.param


def test_default_constructor(vec3):
    assert vec3() == (0, 0, 0)


def test_init_one_param(vec3):
    assert vec3((2, 3)) == (2, 3, 0)
    assert vec3((2, 3, 4)) == (2, 3, 4)


def test_invalid_one_param_init(vec3):
    with pytest.raises(TypeError):
        vec3(0)
    with pytest.raises(TypeError):
        vec3((0, ))


def test_invalid_param_count(vec3):
    with pytest.raises(TypeError):
        vec3(1, 2, 3, 4)
    with pytest.raises(TypeError):
        vec3((1, 2, 3, 4))


def test_init_two_params(vec3):
    assert vec3(1, 2) == (1, 2, 0)


def test_init_three_params(vec3):
    assert Vec3(1, 2, 3) == (1, 2, 3)


def test_immutable_attributes(vec3):
    v = vec3()
    with pytest.raises(AttributeError):
        v.x = 1.0
    with pytest.raises(AttributeError):
        v.y = 1.0
    with pytest.raises(AttributeError):
        v.z = 1.0


def test_from_angle():
    angle = math.radians(50)
    length = 3.
    assert Vec3.from_angle(angle, length) == (
        math.cos(angle) * length, math.sin(angle) * length, 0)

    length, angle = 7, 45
    v = Vec3.from_deg_angle(angle, length)
    x = math.cos(math.radians(angle)) * length
    y = math.sin(math.radians(angle)) * length
    assert v == (x, y)


def test_usage_as_tuple():
    v = Vec3(1, 2, 3)
    assert tuple(v) == (1, 2, 3)
    assert isinstance(v.xyz, tuple)
    assert v.xyz == (1, 2, 3)


def test_get_item_positive_index():
    v = Vec3(1, 2, 3)
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3
    with pytest.raises(IndexError):
        _ = v[3]


@pytest.mark.parametrize('index', [-1, -2, -3])
def test_get_item_negative_index(index):
    with pytest.raises(IndexError):
        _ = Vec3()[index]  # negative indices not supported


def test_get_item_does_not_support_slicing():
    with pytest.raises(TypeError):
        _ = Vec3()[:2]  # slicing is not supported


def test_vec2():
    v2 = Vec3(1, 2, 3).vec2
    assert len(v2) == 2
    assert v2 == (1, 2)


def test_round():
    v = Vec3(1.123, 2.123, 3.123)
    v2 = v.round(1)
    assert v2 == (1.1, 2.1, 3.1)


def test_iter():
    assert sum(Vec3(1, 2, 3)) == 6


def test_deep_copy():
    import copy

    v = Vec3(1, 2, 3)
    l1 = [v, v, v]

    l2 = copy.copy(l1)
    assert l2[0] is l1[0], 'Vec3 is immutable'

    l3 = copy.deepcopy(l1)
    assert l3[0] is l1[0], 'Vec3 is immutable'


def test_get_angle():
    v = Vec3(3, 3)
    assert math.isclose(v.angle_deg, 45)
    assert math.isclose(v.angle, math.radians(45))


def test_spatial_angle():
    v = Vec3(3, 3, 0)
    assert math.isclose(v.spatial_angle_deg, 45)
    assert math.isclose(v.spatial_angle, math.radians(45))


def test_compare_vectors():
    v1 = Vec3(1, 2, 3)
    assert v1 == (1, 2, 3)
    assert (1, 2, 3) == v1

    v2 = Vec3(2, 3, 4)
    assert v2 > v1
    assert v1 < v2


def test_xy():
    assert Vec3(1, 2, 3).xy == Vec3(1, 2)


def test_is_null():
    v = Vec3()
    assert v.is_null

    v1 = Vec3(23.56678, 56678.56778, 2.56677) * (1.0 / 14.5667)
    v2 = Vec3(23.56678, 56678.56778, 2.56677) / 14.5667
    assert (v2 - v1).is_null

    assert Vec3(0, 0, 0).is_null


def test_bool():
    v = Vec3()
    assert bool(v) is False

    v1 = Vec3(23.56678, 56678.56778, 2.56677) * (1.0 / 14.5667)
    v2 = Vec3(23.56678, 56678.56778, 2.56677) / 14.5667
    result = v2 - v1
    assert bool(result) is False
    # actual precision is abs_tol=1e-9
    assert not Vec3(1e-8, 0, 0).is_null


def test_magnitude(vec3):
    v = vec3(3, 4, 5)
    assert math.isclose(abs(v), 7.0710678118654755)
    assert math.isclose(v.magnitude, 7.0710678118654755)
    assert vec3().magnitude == 0


def test_magnitude_square(vec3):
    v = vec3(3, 4, 5)
    assert math.isclose(v.magnitude_square, 50)
    assert vec3().magnitude_square == 0


def test_normalize(vec3):
    v = vec3(2, 0, 0)
    assert v.normalize() == (1, 0, 0)


def test_normalize_to_length(vec3):
    v = vec3(2, 0, 0)
    assert v.normalize(4) == (4, 0, 0)


def test_normalize_error(vec3):
    with pytest.raises(ZeroDivisionError):
        vec3().normalize()


def test_orthogonal_ccw(vec3):
    v = vec3(3, 4)
    assert v.orthogonal() == (-4, 3)


def test_orthogonal_cw(vec3):
    v = vec3(3, 4)
    assert v.orthogonal(False) == (4, -3)


def test_negative(vec3):
    v = vec3(2, 3, 4)
    assert -v == (-2, -3, -4)
    assert (-vec3()).is_null is True


def test_add_scalar_type_error(vec3):
    with pytest.raises(TypeError):
        vec3(2, 3, 4) + 3


def test_radd_scalar_type_error(vec3):
    with pytest.raises(TypeError):
        3 + vec3(2, 3, 4)


def test_iadd_scalar_type_error(vec3):
    v = vec3(2, 3, 4)
    with pytest.raises(TypeError):
        v += 3


def test_sub_scalar_type_error(vec3):
    with pytest.raises(TypeError):
        vec3(2, 3, 4) - 3


def test_rsub_scalar_vector_type_error(vec3):
    with pytest.raises(TypeError):
        7 - vec3(2, 3, 4)


def test_isub_scalar_type_error(vec3):
    v = vec3(2, 3, 4)
    with pytest.raises(TypeError):
        v -= 3


def test_add_vector(vec3):
    v = vec3(2, 3, 4)
    assert v + (7, 7, 7) == (9, 10, 11)


def test_iadd_vector(vec3):
    v = vec3(2, 3, 4)
    v += (7, 7, 7)
    assert v == (9, 10, 11)


def test_radd_vector(vec3):
    v = vec3(2, 3, 4)
    assert (7, 7, 7) + v == (9, 10, 11)


def test_sub_vector():
    v = Vec3(2, 3, 4)
    assert v - (7, 7, 7) == (-5, -4, -3)


def test_isub_vector():
    v = Vec3(2, 3, 4)
    v -= (7, 7, 7)
    assert v == (-5, -4, -3)


def test_rsub_vector():
    v = Vec3(2, 3, 4)
    assert (7, 7, 7) - v == (5, 4, 3)


def test_mul_scalar():
    v = Vec3(2, 3, 4)
    assert v * 2 == (4, 6, 8)


def test_imul_scalar():
    v = Vec3(2, 3, 4)
    v *= 2
    assert v == (4, 6, 8)


def test_rmul_scalar():
    v = Vec3(2, 3, 4)
    assert 2 * v == (4, 6, 8)


def test_div_scalar():
    v = Vec3(2, 3, 4)
    assert v / 2 == (1, 1.5, 2)


def test_idiv_scalar():
    v = Vec3(2, 3, 4)
    v /= 2
    assert v == (1, 1.5, 2)


def test_dot_product(vec3):
    v1 = vec3(2, 7, 1)
    v2 = vec3(3, 9, 8)
    assert math.isclose(v1.dot(v2), 77)


def test_angle_deg(vec3):
    assert math.isclose(vec3(0, 1).angle_deg, 90)
    assert math.isclose(vec3(0, -1).angle_deg, -90)
    assert math.isclose(vec3(1, 1).angle_deg, 45)
    assert math.isclose(vec3(-1, 1).angle_deg, 135)


def test_angle_between(vec3):
    v1 = vec3(0, 1)
    v2 = vec3(1, 1)
    angle = v1.angle_between(v2)
    assert math.isclose(angle, math.pi / 4)
    # reverse order, same result
    angle = v2.angle_between(v1)
    assert math.isclose(angle, math.pi / 4)
    angle = v1.angle_between(Vec3(0, -1))
    assert math.isclose(angle, math.pi)


@pytest.mark.parametrize('v1, v2', [
    [(1, 0), (0, 0)],
    [(0, 0), (1, 0)],
    [(0, 0), (0, 0)],
])
def test_angle_between_null_vector(vec3, v1, v2):
    with pytest.raises(ZeroDivisionError):
        vec3(v1).angle_between(vec3(v2))


def test_angle_about():
    extrusion = Vec3(0, 0, 1)
    a = Vec3(1, 0, 0)
    b = Vec3(1, 1, 0)
    assert math.isclose(a.angle_between(b), math.pi / 4)
    assert math.isclose(extrusion.angle_about(a, b), math.pi / 4)

    extrusion = Vec3(0, 0, -1)
    assert math.isclose(a.angle_between(b), math.pi / 4)
    assert math.isclose(extrusion.angle_about(a, b), (-math.pi / 4) % math.tau)

    extrusion = Vec3(0, 0, 1)
    a = Vec3(1, 1, 0)
    b = Vec3(1, 1, 0)
    assert math.isclose(a.angle_between(b), 0, abs_tol=1e-5)
    assert math.isclose(extrusion.angle_about(a, b), 0)

    extrusion = Vec3(0, 1, 0)
    a = Vec3(1, 1, 0)
    b = Vec3(0, 1, -1)
    assert math.isclose(a.angle_between(b), math.pi / 3, abs_tol=1e-5)
    c = a.cross(b)
    assert math.isclose(a.angle_between(b), c.angle_about(a, b))
    assert math.isclose(extrusion.angle_about(a, b), math.pi / 2)


def test_cross_product():
    v1 = Vec3(2, 7, 9)
    v2 = Vec3(3, 9, 1)
    assert v1.cross(v2) == (-74, 25, -3)


def test_rot_z():
    assert Vec3(2, 2, 7).rotate_deg(90) == (-2, 2, 7)


def test_lerp():
    v1 = Vec3(1, 1, 1)
    v2 = Vec3(4, 4, 4)
    assert v1.lerp(v2, .5) == (2.5, 2.5, 2.5)
    assert v1.lerp(v2, 0) == (1, 1, 1)
    assert v1.lerp(v2, 1) == (4, 4, 4)


def test_replace():
    v = Vec3(1, 2, 3)
    assert v.replace(x=7) == (7, 2, 3)
    assert v.replace(y=7) == (1, 7, 3)
    assert v.replace(z=7) == (1, 2, 7)
    assert v.replace(x=7, z=7) == (7, 2, 7)


def test_project():
    v = Vec3(10, 0, 0)
    assert v.project((5, 0, 0)) == (5, 0, 0)
    assert v.project((5, 5, 0)) == (5, 0, 0)
    assert v.project((5, 5, 5)) == (5, 0, 0)

    v = Vec3(10, 10, 0)
    assert v.project((10, 0, 0)) == (5, 5, 0)


def test_vec3_sum(vec3):
    assert vec3.sum([]).is_null is True
    assert vec3.sum([Vec3(1, 1, 1)]) == (1, 1, 1)
    assert vec3.sum([Vec3(1, 1, 1), (2, 2, 2)]) == (3, 3, 3)
