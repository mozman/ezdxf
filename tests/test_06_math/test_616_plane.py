# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
from ezdxf.math import Plane, Vector


def test_init():
    p = Plane(Vector(1, 0, 0), 5)
    assert p.normal == (1, 0, 0)
    assert p.distance_from_origin == 5


def test_init_form_3p():
    p = Plane.from_3p(Vector(5, 0, 0), Vector(5, 1, 5), Vector(5, 0, 1))
    assert p.normal == (1, 0, 0)
    assert p.distance_from_origin == 5


def test_equal():
    p1 = Plane.from_vector((5, 0, 0))
    p2 = Plane.from_vector((5, 0, 0))
    assert p1 is not p2
    assert p1 == p1
    with pytest.raises(TypeError):
        p1 == Vector(5, 0, 0)
    with pytest.raises(TypeError):
        p1 != Vector(5, 0, 0)
    with pytest.raises(TypeError):
        p1 == 5
    with pytest.raises(TypeError):
        p1 != 5


def test_init_form_vector():
    p = Plane.from_vector((5, 0, 0))
    assert p.normal == (1, 0, 0)
    assert p.distance_from_origin == 5

    with pytest.raises(ZeroDivisionError):
        Plane.from_vector((0, 0, 0))


def test_signed_distance_to():
    p = Plane.from_vector((5, 0, 0))
    assert p.signed_distance_to(Vector(10, 0, 0)) == 5
    assert p.signed_distance_to(Vector(0, 0, 0)) == -5


def test_distance_to():
    p = Plane.from_vector((5, 0, 0))
    assert p.distance_to(Vector(10, 0, 0)) == 5
    assert p.distance_to(Vector(0, 0, 0)) == 5


def test_is_coplanar():
    p = Plane.from_vector((5, 0, 0))
    assert p.is_coplanar_vertex(Vector(5, 5, 0)) is True
    assert p.is_coplanar_vertex(Vector(5, 0, 5)) is True


def test_is_coplanar_plane():
    p1 = Plane.from_vector((5, 0, 0))
    p2 = Plane.from_vector((-1, 0, 0))
    assert p1.is_coplanar_plane(p2) is True


if __name__ == '__main__':
    pytest.main([__file__])
