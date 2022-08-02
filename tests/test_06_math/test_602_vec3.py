# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
import pickle

# Import from 'ezdxf.math._vector' to test Python implementation
from ezdxf.math._vector import Vec3
from ezdxf.acc import USE_C_EXT

vec3_classes = [Vec3]

if USE_C_EXT:
    from ezdxf.acc.vector import Vec3 as CVec3

    vec3_classes.append(CVec3)


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
        vec3((0,))


def test_invalid_param_count(vec3):
    with pytest.raises(TypeError):
        vec3(1, 2, 3, 4)
    with pytest.raises(TypeError):
        vec3((1, 2, 3, 4))


def test_init_two_params(vec3):
    assert vec3(1, 2) == (1, 2, 0)


def test_init_three_params(vec3):
    assert vec3(1, 2, 3) == (1, 2, 3)


def test_immutable_attributes(vec3):
    v = vec3()
    with pytest.raises(AttributeError):
        v.x = 1.0
    with pytest.raises(AttributeError):
        v.y = 1.0
    with pytest.raises(AttributeError):
        v.z = 1.0


def test_from_angle(vec3):
    angle = math.radians(50)
    length = 3.0
    assert vec3.from_angle(angle, length) == (
        math.cos(angle) * length,
        math.sin(angle) * length,
        0,
    )

    length, angle = 7, 45
    v = vec3.from_deg_angle(angle, length)
    x = math.cos(math.radians(angle)) * length
    y = math.sin(math.radians(angle)) * length
    assert v == (x, y)


def test_usage_as_tuple(vec3):
    v = vec3(1, 2, 3)
    assert tuple(v) == (1, 2, 3)
    assert isinstance(v.xyz, tuple)
    assert v.xyz == (1, 2, 3)


def test_get_item_positive_index(vec3):
    v = vec3(1, 2, 3)
    assert v[0] == 1
    assert v[1] == 2
    assert v[2] == 3
    with pytest.raises(IndexError):
        _ = v[3]


@pytest.mark.parametrize("index", [-1, -2, -3])
def test_get_item_negative_index(index, vec3):
    with pytest.raises(IndexError):
        _ = vec3()[index]  # negative indices not supported


def test_get_item_does_not_support_slicing(vec3):
    with pytest.raises(TypeError):
        _ = vec3()[:2]  # slicing is not supported


def test_vec2(vec3):
    v2 = vec3(1, 2, 3).vec2
    assert len(v2) == 2
    assert v2 == (1, 2)


def test_round(vec3):
    v = vec3(1.123, 2.123, 3.123)
    v2 = v.round(1)
    assert v2 == (1.1, 2.1, 3.1)


def test_iter(vec3):
    assert sum(vec3(1, 2, 3)) == 6


def test_deep_copy(vec3):
    import copy

    v = vec3(1, 2, 3)
    l1 = [v, v, v]

    l2 = copy.copy(l1)
    assert l2[0] is l1[0], "Vec3 is immutable"

    l3 = copy.deepcopy(l1)
    assert l3[0] is l1[0], "Vec3 is immutable"


def test_get_angle(vec3):
    v = vec3(3, 3)
    assert math.isclose(v.angle_deg, 45)
    assert math.isclose(v.angle, math.radians(45))


def test_spatial_angle(vec3):
    v = vec3(3, 3, 0)
    assert math.isclose(v.spatial_angle_deg, 45)
    assert math.isclose(v.spatial_angle, math.radians(45))


def test_compare_vectors(vec3):
    v1 = vec3(1, 2, 3)
    assert v1 == (1, 2, 3)
    assert (1, 2, 3) == v1

    v2 = vec3(2, 3, 4)
    assert v2 > v1
    assert v1 < v2


def test_xy(vec3):
    assert vec3(1, 2, 3).xy == vec3(1, 2)


def test_is_null(vec3):
    v = vec3()
    assert v.is_null

    v1 = vec3(23.56678, 56678.56778, 2.56677) * (1.0 / 14.5667)
    v2 = vec3(23.56678, 56678.56778, 2.56677) / 14.5667
    assert (v2 - v1).is_null

    assert vec3(0, 0, 0).is_null


def test_is_not_null_default_abs_tol(vec3):
    assert vec3(1e-11, 0, 0).is_null is False


def test_is_null_default_abs_tol(vec3):
    assert vec3(1e-12, 0, 0).is_null is True


def test_bool(vec3):
    v = vec3()
    assert bool(v) is False

    v1 = vec3(23.56678, 56678.56778, 2.56677) * (1.0 / 14.5667)
    v2 = vec3(23.56678, 56678.56778, 2.56677) / 14.5667
    result = v2 - v1
    assert bool(result) is False
    # current rel_tol=1e-9
    assert not vec3(1e-8, 0, 0).is_null


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


def test_add_vector(vec3):
    assert vec3(2, 3, 4) + (7, 7, 7) == (9, 10, 11)


def test_iadd_vector(vec3):
    v = vec3(2, 3, 4)
    v += (7, 7, 7)
    assert v == (9, 10, 11)


def test_radd_vector(vec3):
    assert (7, 7, 7) + vec3(2, 3, 4) == (9, 10, 11)


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


def test_sub_vector(vec3):
    assert vec3(2, 3, 4) - (7, 7, 7) == (-5, -4, -3)


def test_isub_vector(vec3):
    v = vec3(2, 3, 4)
    v -= (7, 7, 7)
    assert v == (-5, -4, -3)


def test_rsub_vector(vec3):
    assert (7, 7, 7) - vec3(2, 3, 4) == (5, 4, 3)


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


def test_mul_scalar(vec3):
    assert vec3(2, 3, 4) * 2 == (4, 6, 8)


def test_mul_tuple_type_error(vec3):
    with pytest.raises(TypeError):
        vec3(1, 0) * (1, 9)


def test_imul_scalar(vec3):
    v = vec3(2, 3, 4)
    v *= 2
    assert v == (4, 6, 8)


def test_imul_tuple_type_error(vec3):
    v = vec3(2, 3, 4)
    with pytest.raises(TypeError):
        v *= (1, 0)


def test_rmul_scalar(vec3):
    assert 2 * vec3(2, 3, 4) == (4, 6, 8)


def test_rmul_tuple_type_error(vec3):
    with pytest.raises(TypeError):
        (1, 9) * vec3(1, 0)


def test_div_scalar(vec3):
    assert vec3(2, 3, 4) / 2 == (1, 1.5, 2)
    with pytest.raises(ZeroDivisionError):
        vec3(1, 0) / 0


def test_idiv_scalar(vec3):
    v = vec3(2, 3, 4)
    v /= 2
    assert v == (1, 1.5, 2)


def test_div_tuple_type_error(vec3):
    with pytest.raises(TypeError):
        vec3(1, 0) / (1, 0)


def test_rdiv_scalar_type_error(vec3):
    with pytest.raises(TypeError):
        1 / vec3(1, 0)


def test_rdiv_tuple_type_error(vec3):
    with pytest.raises(TypeError):
        (1, 0) / vec3(1, 0)


def test_inplace_operations_do_not_mutate_vec3_inplace():
    v = Vec3(2, 3)
    v_check = v
    v += Vec3(7, 7)
    assert v_check is not v, "__iadd__ should not operate inplace"

    v_check = v
    v -= Vec3(7, 7)
    assert v_check is not v, "__isub__ should not operate inplace"

    v_check = v
    v *= 1
    assert v_check is not v, "__imul__ should not operate inplace"

    v_check = v
    v /= 1
    assert v_check is not v, "__itruediv__ should not operate inplace"


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
    angle = v1.angle_between(vec3(0, -1))
    assert math.isclose(angle, math.pi)


@pytest.mark.parametrize(
    "v1, v2",
    [
        [(1, 0), (0, 0)],
        [(0, 0), (1, 0)],
        [(0, 0), (0, 0)],
    ],
)
def test_angle_between_null_vector(vec3, v1, v2):
    with pytest.raises(ZeroDivisionError):
        vec3(v1).angle_between(vec3(v2))


def test_angle_about(vec3):
    extrusion = vec3(0, 0, 1)
    a = vec3(1, 0, 0)
    b = vec3(1, 1, 0)
    assert math.isclose(a.angle_between(b), math.pi / 4)
    assert math.isclose(extrusion.angle_about(a, b), math.pi / 4)

    extrusion = vec3(0, 0, -1)
    assert math.isclose(a.angle_between(b), math.pi / 4)
    assert math.isclose(extrusion.angle_about(a, b), -math.pi / 4 % math.tau)

    extrusion = vec3(0, 0, 1)
    a = vec3(1, 1, 0)
    b = vec3(1, 1, 0)
    assert math.isclose(a.angle_between(b), 0, abs_tol=1e-5)
    assert math.isclose(extrusion.angle_about(a, b), 0)

    extrusion = vec3(0, 1, 0)
    a = vec3(1, 1, 0)
    b = vec3(0, 1, -1)
    assert math.isclose(a.angle_between(b), math.pi / 3, abs_tol=1e-5)
    c = a.cross(b)
    assert math.isclose(a.angle_between(b), c.angle_about(a, b))
    assert math.isclose(extrusion.angle_about(a, b), math.pi / 2)


def test_cross_product(vec3):
    v1 = vec3(2, 7, 9)
    v2 = vec3(3, 9, 1)
    assert v1.cross(v2) == (-74, 25, -3)


def test_rot_z(vec3):
    assert vec3(2, 2, 7).rotate_deg(90).isclose((-2, 2, 7))


def test_lerp(vec3):
    v1 = vec3(1, 1, 1)
    v2 = vec3(4, 4, 4)
    assert v1.lerp(v2, 0.5) == (2.5, 2.5, 2.5)
    assert v1.lerp(v2, 0) == (1, 1, 1)
    assert v1.lerp(v2, 1) == (4, 4, 4)


def test_replace(vec3):
    v = vec3(1, 2, 3)
    assert v.replace(x=7) == (7, 2, 3)
    assert v.replace(y=7) == (1, 7, 3)
    assert v.replace(z=7) == (1, 2, 7)
    assert v.replace(x=7, z=7) == (7, 2, 7)


def test_project(vec3):
    v = vec3(10, 0, 0)
    assert v.project((5, 0, 0)) == (5, 0, 0)
    assert v.project((5, 5, 0)) == (5, 0, 0)
    assert v.project((5, 5, 5)) == (5, 0, 0)

    v = vec3(10, 10, 0)
    assert v.project((10, 0, 0)).isclose((5, 5, 0))


def test_vec3_sum(vec3):
    assert vec3.sum([]).is_null is True
    assert vec3.sum([vec3(1, 1, 1)]) == (1, 1, 1)
    assert vec3.sum([vec3(1, 1, 1), (2, 2, 2)]) == (3, 3, 3)


def test_picklable(vec3):
    for v in [vec3(), vec3((1, 2.5, 3)), vec3(1, 2.5, 3)]:
        pickled_v = pickle.loads(pickle.dumps(v))
        assert v == pickled_v
        assert type(v) is type(pickled_v)


def test_is_equal(vec3):
    v1 = 1.23456789
    assert vec3(v1, v1, v1) == vec3(v1, v1, v1)
    assert vec3(v1, v1, v1) == (v1, v1, v1)
    assert vec3(v1, v1, 0) == vec3(v1, v1)
    assert vec3(v1, v1, 0) == (v1, v1)


def test_is_not_equal(vec3):
    v1 = 1.23456789
    v2 = 1.234567891
    assert vec3(v1, v1, v1) != vec3(v2, v2, v2)
    assert vec3(v1, v1, v1) != (v2, v2, v2)
    assert vec3(v1, v1, 0) != vec3(v2, v2)
    assert vec3(v1, v1, 0) != (v2, v2)
    assert vec3(v1, v1, 1) != vec3(v1, v1)
    assert vec3(v1, v1, 1) != (v1, v1)


@pytest.mark.parametrize(
    "a,b,rel_tol",
    [
        # maximum relative tolerance to be close
        (1.000001, 1.0000019, 1e-6),
        (10.000001, 10.0000019, 1e-7),
        (100.000001, 100.0000019, 1e-8),
        (1000.000001, 1000.0000019, 1e-9),
        (10000.000001, 10000.0000019, 1e-10),
        (100000.000001, 100000.0000019, 1e-11),
        (1000000.000001, 1000000.0000019, 1e-12),
    ],
)
def test_is_close_relative_tolerance(vec3, a, b, rel_tol):
    va = vec3(a, a, a)
    vb = vec3(b, b, b)
    assert va.isclose(vb, rel_tol=rel_tol)


@pytest.mark.parametrize(
    "a,b,rel_tol",
    [
        (1.000001, 1.0000019, 1e-7),
        (10.000001, 10.0000019, 1e-8),
        (100.000001, 100.0000019, 1e-9),
        (1000.000001, 1000.0000019, 1e-10),
        (10000.000001, 10000.0000019, 1e-11),
        (100000.000001, 100000.0000019, 1e-12),
        (1000000.000001, 1000000.0000019, 1e-13),
    ],
)
def test_is_not_close_relative_tolerance(vec3, a, b, rel_tol):
    va = vec3(a, a, a)
    vb = vec3(b, b, b)
    assert not va.isclose(vb, rel_tol=rel_tol)


@pytest.mark.parametrize(
    "a,b",
    [
        # default relative tolerance is 1e-9
        (10.00000001, 10.000000019),  # 1e-8
        (100.0000001, 100.00000019),  # 1e-7
        (1000.000001, 1000.0000019),  # 1e-6
        (10000.00001, 10000.000019),  # 1e-5
        (100000.0001, 100000.00019),  # 1e-4
    ],
)
def test_is_close_for_fixed_relative_tolerance(vec3, a, b):
    va = vec3(a, a, a)
    vb = vec3(b, b, b)
    assert va.isclose(vb, rel_tol=1e-9)


VALUES = [
    (10.000001, 10.0000019),
    (100.000001, 100.0000019),
    (1000.000001, 1000.0000019),
    (10000.000001, 10000.0000019),
    (100000.000001, 100000.0000019),
    (1000000.000001, 1000000.0000019),
]


@pytest.mark.parametrize("a,b", VALUES)
def test_is_close_absolute_tolerance(vec3, a, b):
    va = vec3(a, a, a)
    vb = vec3(b, b, b)
    assert va.isclose(vb, rel_tol=0, abs_tol=1e-6)


@pytest.mark.parametrize("a,b", VALUES)
def test_is_not_close_absolute_tolerance(vec3, a, b):
    va = vec3(a, a, a)
    vb = vec3(b, b, b)
    assert not va.isclose(vb, rel_tol=0, abs_tol=1e-7)


def test_loosing_floating_point_precision_for_big_values():
    # This values can be represented by a double without loss of precision
    assert not math.isclose(
        1_000_000_000.000001, 1_000_000_000.0000019, rel_tol=0, abs_tol=1e-7
    )

    # multiply by 10 and loose precision in the fractional part,
    # now the values are close enough to be equal:
    assert math.isclose(
        10_000_000_000.000001, 10_000_000_000.0000019, rel_tol=0, abs_tol=1e-7
    )
