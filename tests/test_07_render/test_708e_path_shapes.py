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


def test_wedge():
    wedge = shapes.wedge(0, math.pi / 2)
    assert wedge.has_curves
    assert wedge.has_lines
    assert wedge.is_closed is True
    assert len(wedge) == 3, "expected 2 lines and 1 cubic Bèzier segment"
    assert wedge.start == (0, 0, 0), "has to start at the center"
    assert wedge.end == (0, 0, 0), "has to end at the center"
    extends = bbox([wedge])
    assert extends.extmin == (0.0, 0.0)
    assert extends.extmax == (1.0, 1.0)


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


def test_ngon():
    # basic ngon tool is tested here: test_702_render_forms.py
    square = shapes.ngon(4, length=1.0)
    # first vertex is on th x-axis => square is rotated about 45 deg:
    extends = bbox([square])
    d = math.sin(math.pi / 4)
    assert extends.extmin == (-d, -d)
    assert extends.extmax == (d, d)
    assert square.is_closed is True


def test_star():
    # basic star tool is tested here: test_702_render_forms.py
    star4 = shapes.star(4, r1=1, r2=0.5)
    # first vertex is on th x-axis!
    extends = bbox([star4])

    assert extends.extmin == (-1, -1)
    assert extends.extmax == (1, 1)
    assert star4.is_closed is True


def test_gear():
    # basic gear tool is tested here: test_702_render_forms.py
    gear = shapes.gear(16, 0.1, 0.3, 0.2, 1.0)
    # first vertex is on th x-axis!
    extends = bbox([gear])
    assert extends.extmin.isclose((-0.999, -0.999), abs_tol=1e-3)
    assert extends.extmax.isclose((0.999, 0.999), abs_tol=1e-3)
    assert gear.is_closed is True


if __name__ == '__main__':
    pytest.main([__file__])
