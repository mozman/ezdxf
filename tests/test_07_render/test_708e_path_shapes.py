#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import math
from ezdxf.math import basic_transformation
from ezdxf.path import shapes, bbox


def test_unit_circle():
    circle = shapes.unit_circle()
    assert circle.has_curves
    assert len(circle) == 4, "expected 4 cubic Bèzier segments"
    assert circle.start == (1, 0, 0)
    assert circle.end == (1, 0, 0)


def test_scale_circle():
    m = shapes.elliptic_transformation(radius=2)
    circle = shapes.unit_circle(transform=m)
    assert circle.start == (2, 0, 0)


def test_move_circle():
    m = shapes.elliptic_transformation(center=(-1, 0, 0))
    circle = shapes.unit_circle(transform=m)
    assert circle.start == (0, 0, 0)


def test_ellipse():
    m = shapes.elliptic_transformation(ratio=0.5)
    circle = shapes.unit_circle(transform=m)
    extends = bbox([circle])
    assert extends.extmin == (-1.0, -0.5)
    assert extends.extmax == (1.0, 0.5)


def test_rotated_ellipse():
    m = shapes.elliptic_transformation(ratio=0.5, rotation=math.pi / 2)
    circle = shapes.unit_circle(transform=m)
    extends = bbox([circle])
    assert extends.extmin == (-0.5, -1.0)
    assert extends.extmax == (0.5, 1.0)


@pytest.mark.parametrize("w,h", [
    (0, 0), (1, 0), (0, 1), (-1, 1), (1, -1),
])
def test_invalid_rect_dimensions(w, h):
    with pytest.raises(ValueError):
        shapes.rect(w, h)


def test_rectangle():
    rect = shapes.rect(3, 2)
    extends = bbox([rect])
    assert extends.extmin == (-1.5, -1.0)
    assert extends.extmax == (1.5, 1.0)
    assert rect.is_closed is True


def test_transformed_rectangle():
    m = basic_transformation(z_rotation=math.pi / 2)
    rect = shapes.rect(3, 2, transform=m)
    extends = bbox([rect])
    assert extends.extmin == (-1.0, -1.5)
    assert extends.extmax == (1.0, 1.5)


if __name__ == '__main__':
    pytest.main([__file__])
