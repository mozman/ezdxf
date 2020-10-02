#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.render.forms import square, translate
from ezdxf.render import Path, nesting

EXTERIOR = list(translate(square(10), (-5, -5)))
CENTER_HOLE1 = list(translate(square(8), (-4, -4)))
CENTER_HOLE2 = list(translate(square(6), (-3, -3)))
LEFT_HOLE = list(translate(square(2.1), (-3, -1)))
RIGHT_HOLE = list(translate(square(2.0), (3, -1)))


def test_one_path():
    square1 = Path.from_vertices(EXTERIOR)
    result = nesting.fast_bbox_detection([square1])
    assert len(result) == 1
    assert result == [[square1]], \
        "List of polygons and each polygon is a list of paths"


def test_two_separated_paths():
    square1 = Path.from_vertices(EXTERIOR)
    square2 = Path.from_vertices(translate(EXTERIOR, (11, 0)))

    result = nesting.fast_bbox_detection([square1, square2])
    assert len(result) == 2
    # returns the path sorted by area, and reversed if equal sized
    assert result == [[square2], [square1]]


def test_two_nested_patch():
    exterior = Path.from_vertices(EXTERIOR)
    hole = Path.from_vertices(CENTER_HOLE1)

    result = nesting.fast_bbox_detection([hole, exterior])
    assert result[0] == [exterior, [hole]]


def test_three_nested_paths():
    exterior = Path.from_vertices(EXTERIOR)
    hole_level1 = Path.from_vertices(CENTER_HOLE1)
    # hole in the hole
    hole_level2 = Path.from_vertices(CENTER_HOLE2)

    # input order does not matter:
    result = nesting.fast_bbox_detection([hole_level1, exterior, hole_level2])
    assert result[0] == [exterior, [hole_level1, [hole_level2]]]


def test_two_nested_but_separated_paths():
    exterior = Path.from_vertices(EXTERIOR)
    left_hole = Path.from_vertices(LEFT_HOLE)
    right_hole = Path.from_vertices(RIGHT_HOLE)

    result = nesting.fast_bbox_detection([right_hole,left_hole, exterior])
    assert result[0] == [exterior, [left_hole], [right_hole]]


if __name__ == '__main__':
    pytest.main([__file__])
