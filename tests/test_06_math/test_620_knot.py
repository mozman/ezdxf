# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.math.bspline import open_uniform_knot_vector, uniform_knot_vector, required_knot_values
from ezdxf.math.bspline import is_uniform_knots

open_uniform_order2 = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0]
open_uniform_order3 = [ 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0]
open_uniform_order4 = [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 6.0, 6.0, 6.0]


def test_open_uniform_knot_order_2():
    result = open_uniform_knot_vector(5, 2)
    assert len(result) == required_knot_values(5, 2)
    assert result == open_uniform_order2


def test_open_uniform_knot_order_3():
    result = open_uniform_knot_vector(7, 3)
    assert len(result) == required_knot_values(7, 3)
    assert result == open_uniform_order3


def test_open_uniform_knot_order_4():
    result = open_uniform_knot_vector(9, 4)
    assert len(result) == required_knot_values(9, 4)
    assert result == open_uniform_order4


uniform_order2 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
uniform_order3 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
uniform_order4 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]


def test_uniform_knot_order_2():
    result = uniform_knot_vector(5, 2)
    assert len(result) == required_knot_values(5, 2)
    assert result == uniform_order2


def test_uniform_knot_order_3():
    result = uniform_knot_vector(7, 3)
    assert len(result) == required_knot_values(7, 3)
    assert result == uniform_order3


def test_uniform_knot_order_4():
    result = uniform_knot_vector(9, 4)
    assert len(result) == required_knot_values(9, 4)
    assert result == uniform_order4


def test_is_uniform_knots():
    assert is_uniform_knots([0, 1, 2, 3, 4]) is True
    assert is_uniform_knots([0, .1, .2, .3, .4]) is True
    assert is_uniform_knots([0, 0, 0, 0, 0]) is True
    assert is_uniform_knots([0, 1, 3, 3, 3]) is False

