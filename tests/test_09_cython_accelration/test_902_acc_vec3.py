#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
import pytest

fastmath = pytest.importorskip('ezdxf.acc.fastmath')
Vec3 = fastmath.Vec3


def test_default_constructor():
    v = Vec3()
    assert v.x == 0
    assert v.y == 0
    assert v.z == 0


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
    v = Vec3(fastmath.Vec2(1, 2))
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


if __name__ == '__main__':
    pytest.main([__file__])
