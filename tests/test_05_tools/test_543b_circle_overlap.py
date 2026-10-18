from __future__ import annotations


import pytest


import ezdxf


from ezdxf import select


from ezdxf.math import BoundingBox2d


class TestBoundingBoxVsCircle:
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
