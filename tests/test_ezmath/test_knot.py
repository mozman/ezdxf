# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.ezmath.bspline import knot_open_uniform, knot_uniform, required_knot_values
from ezdxf.ezmath.bspline import is_uniform_knots

open_uniform_order2 = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0]
open_uniform_order3 = [ 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0]
open_uniform_order4 = [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 6.0, 6.0, 6.0]


def test_open_uniform_knot_order_2():
    result = knot_open_uniform(5, 2)
    assert len(result) == required_knot_values(5, 2)
    assert result == open_uniform_order2


def test_open_uniform_knot_order_3():
    result = knot_open_uniform(7, 3)
    assert len(result) == required_knot_values(7, 3)
    assert result == open_uniform_order3


def test_open_uniform_knot_order_4():
    result = knot_open_uniform(9, 4)
    assert len(result) == required_knot_values(9, 4)
    assert result == open_uniform_order4


uniform_order2 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
uniform_order3 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
uniform_order4 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]


def test_uniform_knot_order_2():
    result = knot_uniform(5, 2)
    assert len(result) == required_knot_values(5, 2)
    assert result == uniform_order2


def test_uniform_knot_order_3():
    result = knot_uniform(7, 3)
    assert len(result) == required_knot_values(7, 3)
    assert result == uniform_order3


def test_uniform_knot_order_4():
    result = knot_uniform(9, 4)
    assert len(result) == required_knot_values(9, 4)
    assert result == uniform_order4


def test_is_uniform_knots():
    assert is_uniform_knots([0, 1, 2, 3, 4]) is True
    assert is_uniform_knots([0, .1, .2, .3, .4]) is True
    assert is_uniform_knots([0, 0, 0, 0, 0]) is True
    assert is_uniform_knots([0, 1, 3, 3, 3]) is False

