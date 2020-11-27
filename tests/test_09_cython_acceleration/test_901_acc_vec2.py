#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite 603.

import pytest

fastmath = pytest.importorskip('ezdxf.acc.fastmath')
Vec2 = fastmath.Vec2


def test_default_constructor():
    v = Vec2()
    assert v.x == 0
    assert v.y == 0


def test_is_immutable():
    v = Vec2()
    with pytest.raises(AttributeError):
        v.x = 1
    with pytest.raises(AttributeError):
        v.y = 1


def test_init_x_y():
    v = Vec2(1, 2)
    assert v.x == 1
    assert v.y == 2


def test_init_2_tuple():
    v = Vec2((1, 2))
    assert v.x == 1
    assert v.y == 2


def test_init_vec2():
    v = Vec2(Vec2(1, 2))
    assert v.x == 1
    assert v.y == 2


def test_init_3_tuple():
    v = Vec2((1, 2, 3))
    assert v.x == 1
    assert v.y == 2


def test_init_vec3():
    v = Vec2(fastmath.Vec3(1, 2, 3))
    assert v.x == 1
    assert v.y == 2


def test_init_type_error():
    with pytest.raises(TypeError):
        Vec2(1)
    with pytest.raises(TypeError):
        Vec2(1, 2, 3, 4)
    with pytest.raises(TypeError):
        Vec2('xyz')
    with pytest.raises(TypeError):
        Vec2('xyz', 'abc')


def test_compare():
    assert Vec2(1, 2) == Vec2(1, 2)
    assert Vec2(1, 2) == (1, 2)
    # abs_tol is 1e-12
    assert Vec2(1, 2) == (1, 2.0000000000001)
    assert (1, 2) == Vec2(1, 2)
    assert Vec2(1, 2) != (2, 1)


def test_lower_than():
    assert Vec2(1, 2) < Vec2(2, 2)
    assert Vec2(2, 2) > Vec2(1, 2)


def test_is_null():
    assert Vec2().is_null is True


def test_bool():
    assert bool(Vec2()) is False


def test_does_not_support_slicing():
    with pytest.raises(TypeError):
        _ = Vec2(2, 1)[:]


if __name__ == '__main__':
    pytest.main([__file__])
