# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import pytest
import random

import ezdxf
from ezdxf.layouts import Modelspace
from ezdxf import bbox, select
from ezdxf.math import BoundingBox2d


@pytest.fixture(scope="module")
def msp():
    doc = ezdxf.new()
    msp_ = doc.modelspace()

    msp_.add_point((0, 1))
    msp_.add_circle((0, 0), radius=5)
    msp_.add_line((-1, -1), (1, 1))
    msp_.add_lwpolyline([(-2, -2), (2, -2), (2, 2), (-2, 2)], close=True)
    return msp_


class TestBoundingBoxVsWindow:
    """The selection functions are testing only the bounding boxes of entities.

    This is a design choice: performance and simplicity over accuracy
    """

    def test_all_inside(self, msp: Modelspace):
        window = select.Window((-5, -5), (5, 5))
        selection = select.bbox_inside(window, msp)
        assert len(selection) == 4

    def test_inside_select_point(self, msp: Modelspace):
        window = select.Window((-1, 0), (1, 2))
        selection = select.bbox_inside(window, msp)
        assert len(selection) == 1
        assert selection[0].dxftype() == "POINT"

    def test_inside_select_point_and_line(self, msp: Modelspace):
        window = select.Window((-1, -1), (1, 1))
        selection = select.bbox_inside(window, msp)
        assert len(selection) == 2
        assert selection[0].dxftype() == "POINT"
        assert selection[1].dxftype() == "LINE"

    def test_outside_none(self, msp: Modelspace):
        window = select.Window((-5, -5), (5, 5))
        selection = select.bbox_outside(window, msp)
        assert len(selection) == 0

    def test_outside_all(self, msp: Modelspace):
        window = select.Window((6, 6), (7, 7))
        selection = select.bbox_outside(window, msp)
        assert len(selection) == 4

    def test_overlaps_all(self, msp: Modelspace):
        """The window just overlaps the bounding boxes of the CIRCLE and the
        LWPOLYLINE not the geometry itself.
        """
        window = select.Window((0, 0), (2, 2))
        selection = select.bbox_overlap(window, msp)
        assert len(selection) == 4

    def test_overlap_selects_touching_entities(self, msp: Modelspace):
        """The window touches just the bounding box of the CIRCLE, not the curve itself."""
        window = select.Window((5, 5), (6, 6))
        selection = select.bbox_overlap(window, msp)
        assert len(selection) == 1
        assert selection[0].dxftype() == "CIRCLE"


class TestBoundingBoxVsCircle:
    """The selection functions are testing only the bounding boxes of selection.

    This is a design choice: performance and simplicity over accuracy
    """

    def test_all_inside(self, msp: Modelspace):
        circle = select.Circle((0, 0), 10)
        selection = select.bbox_inside(circle, msp)
        assert len(selection) == 4

    def test_all_outside(self, msp: Modelspace):
        circle = select.Circle((7, 7), 1)
        selection = select.bbox_outside(circle, msp)
        assert len(selection) == 4

    def test_none_outside(self, msp: Modelspace):
        circle = select.Circle((0, 0), 1)
        selection = select.bbox_outside(circle, msp)
        assert len(selection) == 0

    def test_outside_corner_case_point(self, msp: Modelspace):
        """Bounding boxes do overlap but point is outside circle.

        point = (0, 1)
        """
        circle = select.Circle((1, 0), 1)
        selection = select.bbox_outside(circle, msp.query("POINT"))
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
        selection = select.bbox_outside(circle, msp.query("LWPOLYLINE"))
        assert len(selection) == 0

    def test_overlap_all(self, msp: Modelspace):
        circle = select.Circle((0, 0), 1)
        selection = select.bbox_overlap(circle, msp)
        assert len(selection) == 4

    def test_overlap_none(self, msp: Modelspace):
        circle = select.Circle((7, 0), 1)
        selection = select.bbox_overlap(circle, msp)
        assert len(selection) == 0

    def test_is_overlapping_point(self, msp: Modelspace):
        circle = select.Circle((0, 0), 1)
        selection = select.bbox_overlap(circle, msp.query("POINT"))
        assert len(selection) == 1

    def test_is_overlapping_line(self, msp: Modelspace):
        """Bounding boxes do overlap but circle does not intersect line.
        overlap tests are performed on the bounding box of the line!

        CC.
        C#x
        .xx

        line = (-1, -1) (1, 1)
        """
        circle = select.Circle((-1, 1), 1)
        selection = select.bbox_overlap(circle, msp.query("LINE"))
        assert len(selection) == 1

    @pytest.mark.parametrize(
        "corners, overlaps",
        [
            (((-10, 0.5), (2, 0.5)), True),
            (((0.5, -10), (0.5, 2)), True),
            (((-10, -2), (2, 2)), True),
            (((-10, 1), (2, 1)), True),
            (((1, -10), (1, 2)), True),
            (((1, 0), (1, 0)), True),
            (((0.8, 0.8), (2, 2)), False),
            (((-10, 1.01), (2, 1.01)), False),
        ],
    )
    def test_circle_box_nearest_point(self, corners, overlaps):
        shape = select.Circle((0, 0), 1)
        box = BoundingBox2d(corners)
        assert shape.is_overlapping_bbox(box) is overlaps
        assert shape.is_outside_bbox(box) is not overlaps

    def test_crossing_line_is_selected_and_not_outside(self):
        line = ezdxf.new().modelspace().add_line((-10, 0.5), (2, 0.5))
        shape = select.Circle((0, 0), 1)
        assert list(select.bbox_overlap(shape, [line])) == [line]
        assert not select.bbox_outside(shape, [line])

    def test_zero_radius_selects_only_boxes_containing_center(self):
        shape = select.Circle((2, 3), 0)
        assert shape.is_overlapping_bbox(BoundingBox2d([(1, 2), (10, 20)]))
        assert not shape.is_overlapping_bbox(BoundingBox2d([(3, 3), (4, 4)]))


class TestBoundingBoxVsPolygon:
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
        selection = select.bbox_inside(polygon, msp)
        assert len(selection) == 4

    def test_circle_not_inside(self, msp: Modelspace):
        """Bounding boxes do overlap but all corner vertices of the CIRCLE bbox are
        outside.
        """
        polygon = select.Polygon([(-2, -2), (2, -2), (2, 2), (-2, 2)])
        selection = select.bbox_inside(polygon, msp.query("CIRCLE"))
        assert len(selection) == 0

    def test_circle_is_not_inside_concave_polygon(self, msp: Modelspace):
        """Bounding box of CIRCLE is completely inside the polygon, all edge vertices
        are inside the polygon but some edges do intersect with the polygon.
        CIRCLE is not complete inside!
        """
        polygon = select.Polygon([(-10, -10), (10, -10), (10, 10), (0, 0), (-10, 10)])
        selection = select.bbox_inside(polygon, msp.query("CIRCLE"))
        assert len(selection) == 0

        selection = select.bbox_outside(polygon, msp.query("CIRCLE"))
        assert len(selection) == 0

    def test_all_outside(self, msp: Modelspace):
        polygon = select.Polygon([(6, 6), (7, 6), (7, 7), (6, 7)])
        selection = select.bbox_outside(polygon, msp)
        assert len(selection) == 4

    def test_point_is_outside(self, msp: Modelspace):
        """Bounding boxes do overlap, all corner vertices of the POINT bbox are
        outside and POINT is outside the polygon.

        point: (0, 1)
        """
        polygon = select.Polygon([(0, 0), (1, 0), (1, 1)])
        selection = select.bbox_outside(polygon, msp.query("POINT"))
        assert len(selection) == 1

    def test_line_is_not_outside(self, msp: Modelspace):
        """Bounding boxes do overlap all corner vertices of the LINE bbox are
        outside but the LINE is overlap the polygon.

        line: (-2, -2) (2, 2)
        """
        polygon = select.Polygon([(-1, -3), (1, -3), (0, 3)])
        selection = select.bbox_outside(polygon, msp.query("LINE"))
        assert len(selection) == 0

    def test_all_overlap(self, msp: Modelspace):
        """All inside is also all overlap."""
        polygon = select.Polygon([(-5, -5), (5, -5), (5, 5), (-5, 5)])
        selection = select.bbox_overlap(polygon, msp)
        assert len(selection) == 4

    def test_point_not_overlaps(self, msp: Modelspace):
        """Bounding boxes do overlap, all corner vertices of the POINT bbox are
        outside and POINT is outside the polygon.

        point: (0, 1)
        """
        polygon = select.Polygon([(0, 0), (1, 0), (1, 1)])
        selection = select.bbox_overlap(polygon, msp.query("POINT"))
        assert len(selection) == 0

    def test_line_overlaps(self, msp: Modelspace):
        """Bounding boxes do overlap, all corner vertices of the LINE bbox are
        outside and the LINE is overlap the polygon.

        line: (-2, -2) (2, 2)
        """
        polygon = select.Polygon([(-1, -3), (1, -3), (0, 3)])
        selection = select.bbox_overlap(polygon, msp.query("LINE"))
        assert len(selection) == 1

    def test_circle_overlaps(self, msp: Modelspace):
        """All corner vertices of the CIRCLE bbox are outside and CIRCLE does overlap
        with polygon.  This is different to overlap selection in CAD applications!

        circle: (0, 0) radius=5
        """
        polygon = select.Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1)])
        selection = select.bbox_overlap(polygon, msp.query("CIRCLE"))
        assert len(selection) == 1

    def test_concave(self, msp: Modelspace):
        polygon = select.Polygon(
            [(-10, -10), (-10, -20), (20, -20), (20, 20), (10, 20), (10, -10)]
        )
        # ...PP
        # .O.PP
        # ...PP
        # PPPPP
        # PPPPP
        selection = select.bbox_inside(polygon, msp.query("CIRCLE"))
        assert len(selection) == 0

        selection = select.bbox_outside(polygon, msp.query("CIRCLE"))
        assert len(selection) == 1

        selection = select.bbox_overlap(polygon, msp.query("CIRCLE"))
        assert len(selection) == 0


class TestBoundingBoxIntersectsFence:
    @pytest.mark.parametrize("vertices", [[], [(0, 0)]])
    def test_invalid_vertex_count(self, vertices, msp: Modelspace):
        with pytest.raises(ValueError):
            select.bbox_crosses_fence(vertices, msp)

    def test_overlap_all_except_point(self, msp: Modelspace):
        selection = select.bbox_crosses_fence([(-5, 0), (5, 0)], msp)
        assert len(selection) == 3

    def test_can_not_select_point(self, msp: Modelspace):
        """Fence cannot select POINT entities by definition.

        point: (0, 1)
        """
        selection = select.bbox_crosses_fence([(-5, 1), (5, 1)], msp.query("POINT"))
        assert len(selection) == 0

    def test_select_nothing_inside_a_closed_fence(self, msp: Modelspace):
        """A closed fence does NOT work like a polygon selection!"""
        selection = select.bbox_crosses_fence(
            [(-9, -9), (-9, 9), (9, 9), (-9, 9), (-9, -9)], msp
        )
        assert len(selection) == 0

    def test_select_by_touching_bbox_corner(self, msp: Modelspace):
        """CIRCLE is selected by fence touching the CIRCLE bbox at one corner point.
        Does not cross the curve itself!

        circle: (0, 0), radius = 5
        """
        selection = select.bbox_crosses_fence([(0, 10), (10, 0)], msp)
        assert len(selection) == 1


def test_point_selects_all(msp: Modelspace):
    """The point is inside of all entity bounding boxes."""
    selection = select.point_in_bbox((0, 1), msp)
    assert len(selection) == 4


def test_all_entities_chained_by_bounding_boxes():
    doc = ezdxf.new()
    msp = doc.modelspace()
    for x in range(10):
        msp.add_line((x, 0), (x + 1.01, 1))

    start = msp[-1]
    selected = select.bbox_chained(start, msp)
    assert len(selected) == 10


def test_selection_cache_does_not_change_precise_measurements():
    spline = (
        ezdxf.new()
        .modelspace()
        .add_open_spline([(0, 0), (1, 30), (2, 30), (3, 0)], degree=3)
    )
    cache = bbox.Cache()
    select.bbox_overlap(select.Window((-1, -1), (4, 31)), [spline], cache=cache)
    assert bbox.extents([spline], cache=cache).extmax.y == pytest.approx(22.5)


def reference_bbox_chained(start, entities):
    """Original input-order scanning behavior, including discovery order."""
    boxes = {e: BoundingBox2d(bbox.extents([e], fast=True)) for e in entities}
    selected = {start: BoundingBox2d(bbox.extents([start], fast=True))}
    restart = True
    while restart:
        restart = False
        for entity in entities:
            if entity not in selected and any(
                boxes[entity].has_overlap(box) for box in selected.values()
            ):
                selected[entity] = boxes[entity]
                restart = True
    return list(selected)


def test_chained_selection_preserves_discovery_order_with_duplicate_inputs():
    rng = random.Random(543)
    for _ in range(50):
        layout = ezdxf.new().modelspace()
        for _ in range(20):
            x, y = rng.randrange(10), rng.randrange(10)
            layout.add_line((x, y, rng.randrange(10)), (x + 2, y + 2, 100))
        entities = list(layout)
        start = rng.choice(entities)
        entities.extend(rng.choices(entities, k=8))
        rng.shuffle(entities)
        expected = reference_bbox_chained(start, entities)
        assert list(select.bbox_chained(start, iter(entities))) == expected


def test_chained_selection_empty_start_and_unsupported_entities():
    layout = ezdxf.new().modelspace()
    line = layout.add_line((0, 0), (1, 1))
    ray = layout.add_ray((0, 0), (1, 0))
    assert list(select.bbox_chained(ray, [line, ray])) == [ray]
    assert list(select.bbox_chained(line, [ray])) == [line]


def test_chained_selection_ignores_z_and_includes_start_outside_input():
    layout = ezdxf.new().modelspace()
    start = layout.add_line((0, 0, -50), (1, 0, -50))
    near = layout.add_line((1, 0, 50), (2, 0, 50))
    far = layout.add_line((10, 0), (11, 0))
    assert list(select.bbox_chained(start, [far, near, near])) == [start, near]


def test_reversed_chain_checks_each_pair_at_most_once(monkeypatch):
    layout = ezdxf.new().modelspace()
    for x in range(40):
        layout.add_line((x, 0), (x + 1, 0))
    calls = 0
    original = BoundingBox2d.has_overlap

    def count_overlap(self, other):
        nonlocal calls
        calls += 1
        return original(self, other)

    monkeypatch.setattr(BoundingBox2d, "has_overlap", count_overlap)
    assert len(select.bbox_chained(layout[-1], layout)) == 40
    assert calls <= 40 * 39 // 2


class TestPlanarSearchIndex:
    def test_circle_select_radius_1(self, msp: Modelspace):
        psi = select.PlanarSearchIndex(msp)
        result = psi.detection_point_in_circle((0, 0), 1)
        assert len(result) == 1
        assert result[0].dxftype() == "POINT"
        # CIRCLE is not selected because, none of the bounding box vertices of the
        # CIRCLE is inside the section circle

    def test_circle_select_radius_2(self, msp: Modelspace):
        psi = select.PlanarSearchIndex(msp)
        result = psi.detection_point_in_circle((0, 0), 2)
        assert len(result) == 2
        types = {e.dxftype() for e in result}
        assert "POINT" in types
        assert "LINE" in types

    def test_circle_select_all(self, msp: Modelspace):
        psi = select.PlanarSearchIndex(msp)
        result = psi.detection_point_in_circle((0, 0), 8)
        assert len(result) == 4

    def test_rect_select(self, msp: Modelspace):
        psi = select.PlanarSearchIndex(msp)
        result = psi.detection_point_in_rect((-1, -1), (1, 1))
        assert len(result) == 2
        types = {e.dxftype() for e in result}
        assert "POINT" in types
        assert "LINE" in types

    def test_rect_select_all(self, msp: Modelspace):
        psi = select.PlanarSearchIndex(msp)
        result = psi.detection_point_in_rect((-5, -5), (5, 5))
        assert len(result) == 4


if __name__ == "__main__":
    pytest.main([__file__])
