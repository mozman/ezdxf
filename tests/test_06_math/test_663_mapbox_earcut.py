#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Sequence
import pytest
import math
from ezdxf.math.triangulation import mapbox_earcut_2d
from ezdxf.math import Vec2
from ezdxf.render import forms


def total_area(triangles: Iterable[Sequence[Vec2]]):
    area = 0.0
    sides = []
    for triangle in triangles:
        sides.clear()
        for i in range(3):
            pt = triangle[i]
            pt2 = triangle[(i + 1) % 3]
            sides.append(pt.distance(pt2))
        c, b, a = sides
        area += 0.25 * math.sqrt(
            abs((a + (b + c)) * (c - (a - b)) * (c + (a - b)) * (a + (b - c)))
        )
    return area


def test_triangulate_a_square():
    square = forms.square(2)
    triangles = list(mapbox_earcut_2d(square))
    assert len(triangles) == 2
    assert total_area(triangles) == pytest.approx(4.0)


if __name__ == '__main__':
    pytest.main([__file__])
