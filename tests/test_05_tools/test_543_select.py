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


class TestPolygon:
    """The selection functions are testing only the bounding boxes of selection.

    This is a design choice: performance and simplicity over accuracy
    """

    @pytest.mark.parametrize(
        "vertices",
        [
            [],
            [(0, 0)],
            [(0, 0), (0, 0)],
            [(0, 0), (0, 0), (0, 0)],
        ],
    )
    def test_invalid_vertex_count(self, vertices):
        with pytest.raises(ValueError):
            select.Polygon(vertices)

    def test_all_inside(self, msp: Modelspace):
        polygon = select.Polygon([(-5, -5), (5, -5), (5, 5), (-5, 5)])
        selection = select.inside(msp, polygon)
        assert len(selection) == 4

    def test_circle_not_inside(self, msp: Modelspace):
        """Bounding boxes do overlap but all corner vertices of the CIRCLE bbox are
        outside.
        """
        polygon = select.Polygon([(-2, -2), (2, -2), (2, 2), (-2, 2)])
        selection = select.inside(msp.query("CIRCLE"), polygon)
        assert len(selection) == 0

    def test_all_outside(self, msp: Modelspace):
        polygon = select.Polygon([(6, 6), (7, 6), (7, 7), (6, 7)])
        selection = select.outside(msp, polygon)
        assert len(selection) == 4

    def test_point_is_outside(self, msp: Modelspace):
        """Bounding boxes do overlap, all corner vertices of the POINT bbox are
        outside and POINT is outside the polygon.

        point: (0, 1)
        """
        polygon = select.Polygon([(0, 0), (1, 0), (1, 1)])
        selection = select.outside(msp.query("POINT"), polygon)
        assert len(selection) == 1

    def test_line_is_not_outside(self, msp: Modelspace):
        """Bounding boxes do overlap all corner vertices of the LINE bbox are
        outside but the LINE is crossing the polygon.

        line: (-2, -2) (2, 2)
        """
        polygon = select.Polygon([(-1, -3), (1, -3), (0, 3)])
        selection = select.outside(msp.query("LINE"), polygon)
        assert len(selection) == 0

    def test_all_crossing(self, msp: Modelspace):
        """All inside is also all crossing."""
        polygon = select.Polygon([(-5, -5), (5, -5), (5, 5), (-5, 5)])
        selection = select.crossing(msp, polygon)
        assert len(selection) == 4

    def test_point_is_not_crossing(self, msp: Modelspace):
        """Bounding boxes do overlap, all corner vertices of the POINT bbox are
        outside and POINT is outside the polygon.

        point: (0, 1)
        """
        polygon = select.Polygon([(0, 0), (1, 0), (1, 1)])
        selection = select.crossing(msp.query("POINT"), polygon)
        assert len(selection) == 0

    def test_line_is_crossing(self, msp: Modelspace):
        """Bounding boxes do overlap, all corner vertices of the LINE bbox are
        outside and the LINE is crossing the polygon.

        line: (-2, -2) (2, 2)
        """
        polygon = select.Polygon([(-1, -3), (1, -3), (0, 3)])
        selection = select.crossing(msp.query("LINE"), polygon)
        assert len(selection) == 1

    def test_circle_is_crossing(self, msp: Modelspace):
        """All corner vertices of the CIRCLE bbox are outside and CIRCLE does overlap
        with polygon.  This is different to crossing selection in CAD applications!

        circle: (0, 0) radius=5
        """
        polygon = select.Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        selection = select.crossing(msp.query("CIRCLE"), polygon)
        assert len(selection) == 1


class TestFence:
    """The selection functions are testing only the bounding boxes of selection.

    This is a design choice: performance and simplicity over accuracy
    """

    @pytest.mark.parametrize("vertices", [[], [(0, 0)]])
    def test_invalid_vertex_count(self, vertices):
        with pytest.raises(ValueError):
            select.Fence(vertices)

    def test_crossing_all_except_point(self, msp: Modelspace):
        fence = select.Fence([(-5, 0), (5, 0)])
        selection = select.crossing(msp, fence)
        assert len(selection) == 3

    def test_none_inside_by_definition(self, msp: Modelspace):
        fence = select.Fence([(-5, 0), (5, 0)])
        selection = select.inside(msp, fence)
        assert len(selection) == 0

    def test_outside_when_not_crossing(self, msp: Modelspace):
        fence = select.Fence([(-5, 0), (5, 0)])
        selection = select.outside(msp, fence)
        assert len(selection) == 1
        assert selection[0].dxftype() == "POINT"

    def test_can_not_select_point(self, msp: Modelspace):
        """Fence cannot select POINT entities by definition.

        point: (0, 1)
        """
        fence = select.Fence([(-5, 1), (5, 1)])
        selection = select.crossing(msp.query("POINT"), fence)
        assert len(selection) == 0

    def test_select_nothing_inside_a_closed_fence(self, msp: Modelspace):
        """A closed fence does NOT work like a polygon selection!"""
        fence = select.Fence([(-9, -9), (-9, 9), (9, 9), (-9, 9), (-9, -9)])
        selection = select.crossing(msp, fence)
        assert len(selection) == 0

    def test_select_by_touching_bbox_corner(self, msp: Modelspace):
        """CIRCLE is selected by fence touching the CIRCLE bbox at one corner point.
        Does not cross the curve itself!

        circle: (0, 0), radius = 5
        """
        fence = select.Fence([(0, 10), (10, 0)])
        selection = select.crossing(msp, fence)
        assert len(selection) == 1


if __name__ == "__main__":
    pytest.main([__file__])
