#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
# Test only basic features of Cython implementation,
# Full testing and compatibility check with Python implementation
# is located in test suite 602.

import pytest
import array

cyvec = pytest.importorskip('ezdxf.acc.vector')
Vec3 = cyvec.Vec3


def test_default_constructor():
    v = Vec3()
    assert v.x == 0
    assert v.y == 0
    assert v.z == 0


def test_is_immutable():
    v = Vec3()
    with pytest.raises(AttributeError):
        v.x = 1
    with pytest.raises(AttributeError):
        v.y = 1
    with pytest.raises(AttributeError):
        v.z = 1


def test_init_x_y():
    v = Vec3(1, 2, 3)
    assert v.x == 1
    assert v.y == 2
    assert v.z == 3


def test_init_2_tuple():
    v = Vec3((1, 2))
    assert v.x == 1
    assert v.y == 2
    assert v.z == 0


def test_init_vec2():
    v = Vec3(cyvec.Vec2(1, 2))
    assert v.x == 1
    assert v.y == 2
    assert v.z == 0


def test_init_3_tuple():
    v = Vec3((1, 2, 3))
    assert v.x == 1
    assert v.y == 2
    assert v.z == 3


def test_init_vec3():
    v = Vec3(Vec3(1, 2, 3))
    assert v.x == 1
    assert v.y == 2
    assert v.z == 3


def test_init_type_error():
    with pytest.raises(TypeError):
        Vec3(1)
    with pytest.raises(TypeError):
        Vec3(1, 2, 3, 4)
    with pytest.raises(TypeError):
        Vec3('xyz')
    with pytest.raises(TypeError):
        Vec3('xyz', 'abc')


def test_is_null():
    assert Vec3().is_null is True


def test_bool():
    assert bool(Vec3(1, 0)) is True


def test_compare():
    assert Vec3(1, 2, 3) == Vec3(1, 2, 3)
    assert Vec3(1, 2, 3) == (1, 2, 3)
    # abs_tol is 1e-12
    assert Vec3(1, 2, 3) == (1, 2.0000000000001, 3)
    assert (1, 2) == Vec3(1, 2)
    assert Vec3(1, 2) != (2, 1)


def test_lower_than():
    assert Vec3(1, 2) < Vec3(2, 2)
    assert Vec3(2, 2) > Vec3(1, 2)


def test_does_not_support_slicing():
    with pytest.raises(TypeError):
        _ = Vec3(2, 1)[:]


def test_empty_array():
    a = Vec3.array([])
    assert a.typecode == 'd'
    assert len(a) == 0
    assert len(Vec3.array([], close=True)) == 0


def test_one_item_array():
    a = Vec3.array([(7, 8, 9)])
    assert len(a) == 3
    assert a == array.array('d', (7, 8, 9))


def test_closed_one_item_array():
    a = Vec3.array([(7, 8, 9)], close=True)
    assert len(a) == 3
    assert a == array.array('d', (7, 8, 9))


def test_two_items_array():
    a = Vec3.array([(7, 8, 9), (1, 2, 3)])
    assert len(a) == 6
    assert a == array.array('d', (7, 8, 9, 1, 2, 3))


def test_closed_two_items_array():
    a = Vec3.array([(7, 8, 9), (1, 2, 3)], close=True)
    assert len(a) == 9
    assert a == array.array('d', (7, 8, 9, 1, 2, 3, 7, 8, 9))


if __name__ == '__main__':
    pytest.main([__file__])
