# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pytest

import ezdxf
from ezdxf.layouts import Modelspace
from ezdxf import select


@pytest.fixture(scope="module")
def msp():
    doc = ezdxf.new()
    msp_ = doc.modelspace()

    msp_.add_point((0, 1))
    msp_.add_circle((0, 0), radius=5)
    msp_.add_line((-1, -1), (1, 1))
    msp_.add_lwpolyline([(-2, -2), (2, -2), (2, 2), (-2, 2)], close=True)
    return msp_


class TestWindow:
    """The selection functions are testing only the bounding boxes of entities.

    This is a design choice: performance and simplicity over accuracy
    """

    def test_all_inside(self, msp: Modelspace):
        window = select.Window((-5, -5), (5, 5))
        selection = select.inside(msp, window)
        assert len(selection) == 4

    def test_inside_select_point(self, msp: Modelspace):
        window = select.Window((-1, 0), (1, 2))
        selection = select.inside(msp, window)
        assert len(selection) == 1
        assert selection[0].dxftype() == "POINT"

    def test_inside_select_point_and_line(self, msp: Modelspace):
        window = select.Window((-1, -1), (1, 1))
        selection = select.inside(msp, window)
        assert len(selection) == 2
        assert selection[0].dxftype() == "POINT"
        assert selection[1].dxftype() == "LINE"

    def test_outside_none(self, msp: Modelspace):
        window = select.Window((-5, -5), (5, 5))
        selection = select.outside(msp, window)
        assert len(selection) == 0

    def test_outside_all(self, msp: Modelspace):
        window = select.Window((6, 6), (7, 7))
        selection = select.outside(msp, window)
        assert len(selection) == 4

    def test_crossing_all(self, msp: Modelspace):
        """The window just overlaps the bounding boxes of the CIRCLE and the
        LWPOLYLINE not the geometry itself.
        """
        window = select.Window((0, 0), (2, 2))
        selection = select.crossing(msp, window)
        assert len(selection) == 4

    def test_crossing_selects_touching_entities(self, msp: Modelspace):
        """The window touches just the bounding box of the CIRCLE, not the curve itself."""
        window = select.Window((5, 5), (6, 6))
        selection = select.crossing(msp, window)
        assert len(selection) == 1
        assert selection[0].dxftype() == "CIRCLE"


class TestPoint:
    """The selection functions are testing only the bounding boxes of entities.

    This is a design choice: performance and simplicity over accuracy
    """

    def test_none_inside(self, msp: Modelspace):
        """By definition, nothing can be inside a dimensionless point."""
        point = select.Point((0, 0))
        selection = select.inside(msp, point)
        assert len(selection) == 0

    def test_all_outside(self, msp: Modelspace):
        """By definition, nothing can be inside a dimensionless point and therefore
        everything is outside a point.
        """
        point = select.Point((0, 1))
        selection = select.outside(msp, point)
        assert len(selection) == 4

    def test_crossing_all(self, msp: Modelspace):
        """The point is inside of all entity bounding boxes."""
        point = select.Point((0, 1))
        selection = select.crossing(msp, point)
        assert len(selection) == 4


class TestCircle:
    """The selection functions are testing only the bounding boxes of selection.

    This is a design choice: performance and simplicity over accuracy
    """

    def test_all_inside(self, msp: Modelspace):
        circle = select.Circle((0, 0), 10)
        selection = select.inside(msp, circle)
        assert len(selection) == 4

    def test_all_outside(self, msp: Modelspace):
        circle = select.Circle((7, 7), 1)
        selection = select.outside(msp, circle)
        assert len(selection) == 4

    def test_none_outside(self, msp: Modelspace):
        circle = select.Circle((0, 0), 1)
        selection = select.outside(msp, circle)
        assert len(selection) == 0

    def test_outside_corner_case_point(self, msp: Modelspace):
        """Bounding boxes do overlap but point is outside circle.
        
        point = (0, 1)
        """
        circle = select.Circle((1, 0), 1)
        selection = select.outside(msp.query("POINT"), circle)
        assert len(selection) == 1

    def test_outside_corner_case_polyline(self, msp: Modelspace):
        """All vertices are outside circle but polyline is not outside.

        xCCx
        CCCC
        CCCC
        xCCx

        polyline corners = (-2, -2) ... (2, 2)
        """
        circle = select.Circle((0, 0), 2)
        selection = select.outside(msp.query("LWPOLYLINE"), circle)
        assert len(selection) == 0

    def test_crossing_all(self, msp: Modelspace):
        circle = select.Circle((0, 0), 1)
        selection = select.crossing(msp, circle)
        assert len(selection) == 4

    def test_crossing_none(self, msp: Modelspace):
        circle = select.Circle((7, 0), 1)
        selection = select.crossing(msp, circle)
        assert len(selection) == 0

    def test_is_crossing_point(self, msp: Modelspace):
        circle = select.Circle((0, 0), 1)
        selection = select.crossing(msp.query("POINT"), circle)
        assert len(selection) == 1

    def test_is_crossing_line(self, msp: Modelspace):
        """Bounding boxes do overlap but circle does not intersect line. 
        Crossing tests are performed on the bounding box of the line!

        CC.
        C#x
        .xx

        line = (-1, -1) (1, 1)
        """
        circle = select.Circle((-1, 1), 1)
        selection = select.crossing(msp.query("LINE"), circle)
        assert len(selection) == 1


if __name__ == "__main__":
    pytest.main([__file__])
