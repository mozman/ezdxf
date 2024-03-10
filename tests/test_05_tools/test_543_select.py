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

    def test_inside_all(self, msp: Modelspace):
        window = select.Window((-5, -5), (5, 5))
        entities = select.inside(msp, window)
        assert len(entities) == 4

    def test_inside_select_point(self, msp: Modelspace):
        window = select.Window((-1, 0), (1, 2))
        entities = select.inside(msp, window)
        assert len(entities) == 1
        assert entities[0].dxftype() == "POINT"

    def test_inside_select_point_and_line(self, msp: Modelspace):
        window = select.Window((-1, -1), (1, 1))
        entities = select.inside(msp, window)
        assert len(entities) == 2
        assert entities[0].dxftype() == "POINT"
        assert entities[1].dxftype() == "LINE"

    def test_outside_none(self, msp: Modelspace):
        window = select.Window((-5, -5), (5, 5))
        entities = select.outside(msp, window)
        assert len(entities) == 0

    def test_outside_all(self, msp: Modelspace):
        window = select.Window((6, 6), (7, 7))
        entities = select.outside(msp, window)
        assert len(entities) == 4

    def test_crossing_all(self, msp: Modelspace):
        """The window just overlaps the bounding boxes of the CIRCLE and the
        LWPOLYLINE not the geometry itself.
        """
        window = select.Window((0, 0), (2, 2))
        entities = select.crossing(msp, window)
        assert len(entities) == 4

    def test_crossing_selects_touching_entities(self, msp: Modelspace):
        """The window touches just the bounding box of the CIRCLE, not the curve itself."""
        window = select.Window((5, 5), (6, 6))
        entities = select.crossing(msp, window)
        assert len(entities) == 1
        assert entities[0].dxftype() == "CIRCLE"


class TestPoint:
    """The selection functions are testing only the bounding boxes of entities.

    This is a design choice: performance and simplicity over accuracy
    """

    def test_none_inside_all(self, msp: Modelspace):
        """By definition, nothing can be inside a dimensionless point."""
        point = select.Point((0, 0))
        entities = select.inside(msp, point)
        assert len(entities) == 0

    def test_everything_is_outside(self, msp: Modelspace):
        """By definition, nothing can be inside a dimensionless point and therefore 
        everything is outside a point.
        """
        point = select.Point((0, 1))
        entities = select.outside(msp, point)
        assert len(entities) == 4

    def test_crossing_all(self, msp: Modelspace):
        """The point is inside of all entity bounding boxes."""
        point = select.Point((0, 1))
        entities = select.crossing(msp, point)
        assert len(entities) == 4


if __name__ == "__main__":
    pytest.main([__file__])
