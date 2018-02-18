# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.algebra.spline import knot

order2 = [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0]
order3 = [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0]
order4 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 6.0, 6.0, 6.0]


def test_knot_order_2():
    result = knot(5, 2)
    assert result == order2


def test_knot_order_3():
    result = knot(7, 3)
    assert result == order3


def test_knot_order_4():
    result = knot(9, 4)
    assert result == order4
