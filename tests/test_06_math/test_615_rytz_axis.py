# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import pytest
import math
from ezdxf.math import rytz_axis_construction, Vector


def test_exception():
    with pytest.raises(ArithmeticError):
        # orthogonal axis
        rytz_axis_construction(Vector(5, 0, 0), Vector(0, 3, 0))
    with pytest.raises(ArithmeticError):
        # colinear axis
        rytz_axis_construction(Vector(5, 0, 0), Vector(4, 0, 0))


def test_simple_case():
    a, b, ratio = rytz_axis_construction(Vector(3, 0, 0), Vector(-2, 2, 0))
    assert ratio < 1


if __name__ == '__main__':
    pytest.main([__file__])
