# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License
import pytest

from ezdxf.math import BoundingBox, BoundingBox2d, Vec2, Vec3
from itertools import permutations


class TestBoundingBox:
    def test_init(self):
        bbox = BoundingBox([(0, 0, 0), (10, 10, 10)])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

        bbox = BoundingBox([(10, 10, 10), (0, 0, 0)])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

        bbox = BoundingBox([(7, -2, 9), (-1, 8, -3)])
        assert bbox.extmin == (-1, -2, -3)
        assert bbox.extmax == (7, 8, 9)

    def test_init_none(self):
        bbox = BoundingBox()
        assert bbox.is_empty is True
        assert bbox.has_data is False
        bbox.extend([(0, 0, 0), (10, 10, 10)])
        assert bbox.size == (10, 10, 10)
        assert bbox.is_empty is False
        assert bbox.has_data is True

    def test_init_with_with_empty_list(self):
        assert BoundingBox([]).is_empty is True

    def test_inside(self):
        bbox = BoundingBox([(0, 0, 0), (10, 10, 10)])
        assert bbox.inside((0, 0, 0)) is True
        assert bbox.inside((-1, 0, 0)) is False
        assert bbox.inside((0, -1, 0)) is False
        assert bbox.inside((0, 0, -1)) is False

        assert bbox.inside((5, 5, 5)) is True

        assert bbox.inside((10, 10, 10)) is True
        assert bbox.inside((11, 10, 10)) is False
        assert bbox.inside((10, 11, 10)) is False
        assert bbox.inside((10, 10, 11)) is False

    def test_all_inside(self):
        bbox1 = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox2 = BoundingBox([(1, 1, 1), (9, 9, 9)])
        empty = BoundingBox()
        assert bbox1.all_inside(bbox2) is True
        assert bbox2.all_inside(bbox1) is False
        assert bbox1.all_inside(empty) is False
        assert empty.all_inside(bbox1) is False

    def test_any_inside(self):
        bbox1 = BoundingBox([(0, 0, 0), (7, 7, 7)])
        bbox2 = BoundingBox([(1, 1, 1), (9, 9, 9)])
        empty = BoundingBox()
        assert bbox1.any_inside(bbox2) is True
        assert bbox2.any_inside(bbox1) is True
        assert bbox1.any_inside(empty) is False
        assert empty.any_inside(bbox1) is False

    def test_do_intersect_and_overlap(self):
        bbox1 = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox2 = BoundingBox([(1, 1, 1), (9, 9, 9)])
        bbox3 = BoundingBox([(-1, -1, -1), (1.001, 1.001, 1.001)])
        for a, b in permutations([bbox1, bbox2, bbox3], 2):
            assert a.intersect(b) is True
            assert a.overlap(b) is True

    def test_do_not_intersect_or_overlap(self):
        bbox1 = BoundingBox([(0, 0, 0), (3, 3, 3)])
        bbox2 = BoundingBox([(4, 4, 4), (9, 9, 9)])
        bbox3 = BoundingBox([(-2, -2, -2), (-1, -1, -1)])
        for a, b in permutations([bbox1, bbox2, bbox3], 2):
            assert a.intersect(b) is False
            assert a.overlap(b) is False

    def test_do_not_intersect_or_overlap_empty(self):
        bbox = BoundingBox([(0, 0, 0), (3, 3, 3)])
        empty = BoundingBox()
        assert bbox.intersect(empty) is False
        assert bbox.overlap(empty) is False
        assert empty.intersect(bbox) is False
        assert empty.overlap(bbox) is False
        assert empty.intersect(empty) is False
        assert empty.overlap(empty) is False

    def test_crossing_2d_boxes(self):
        # bboxes do overlap, but do not contain corner points of the other bbox
        bbox1 = BoundingBox2d([(0, 1), (3, 2)])
        bbox2 = BoundingBox2d([(1, 0), (2, 3)])
        assert bbox1.intersect(bbox2) is True
        assert bbox1.overlap(bbox2) is True

    def test_crossing_3d_boxes(self):
        # bboxes do overlap, but do not contain corner points of the other bbox
        bbox1 = BoundingBox([(0, 1, 0), (3, 2, 1)])
        bbox2 = BoundingBox([(1, 0, 0), (2, 3, 1)])
        assert bbox1.intersect(bbox2) is True
        assert bbox1.overlap(bbox2) is True

    def test_touching_2d_boxes(self):
        bbox1 = BoundingBox2d([(0, 0), (1, 1)])
        bbox2 = BoundingBox2d([(1, 1), (2, 2)])
        bbox3 = BoundingBox2d([(-1, -1), (0, 0)])
        assert bbox1.intersect(bbox2) is False
        assert bbox1.overlap(bbox2) is True
        assert bbox2.intersect(bbox1) is False
        assert bbox2.overlap(bbox1) is True
        assert bbox1.intersect(bbox3) is False
        assert bbox1.overlap(bbox3) is True
        assert bbox3.intersect(bbox1) is False
        assert bbox3.overlap(bbox1) is True

    def test_touching_3d_boxes(self):
        bbox1 = BoundingBox([(0, 0, 0), (1, 1, 1)])
        bbox2 = BoundingBox([(1, 1, 1), (2, 2, 2)])
        bbox3 = BoundingBox([(-1, -1, -1), (0, 0, 0)])
        assert bbox1.intersect(bbox2) is False
        assert bbox1.overlap(bbox2) is True
        assert bbox2.intersect(bbox1) is False
        assert bbox2.overlap(bbox1) is True
        assert bbox1.intersect(bbox3) is False
        assert bbox1.overlap(bbox3) is True
        assert bbox3.intersect(bbox1) is False
        assert bbox3.overlap(bbox1) is True

    def test_extend(self):
        bbox = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox.extend([(5, 5, 5)])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

        bbox.extend([(15, 16, 17)])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (15, 16, 17)

        bbox.extend([(-15, -16, -17)])
        assert bbox.extmin == (-15, -16, -17)
        assert bbox.extmax == (15, 16, 17)

    def test_extend_by_empty_list(self):
        bbox = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox.extend([])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

    def test_extend_by_bbox(self):
        bbox = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox2 = BoundingBox([(5, 5, 5), (15, 16, 17)])
        bbox.extend(bbox2)
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (15, 16, 17)

    def test_size(self):
        bbox = BoundingBox([(-2, -2, -2), (8, 8, 8)])
        assert bbox.size == (10, 10, 10)

    def test_center(self):
        bbox = BoundingBox([(-1, -1, -1), (9, 9, 9)])
        assert bbox.center == (4, 4, 4)

    def test_union_of_two_bounding_boxes(self):
        bbox1 = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox2 = BoundingBox([(5, 5, 5), (15, 16, 17)])
        bbox = bbox1.union(bbox2)
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (15, 16, 17)

    def test_union_bbox_with_emtpy_bbox(self):
        bbox1 = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox = bbox1.union(BoundingBox())
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

    def test_union_empty_bbox_with_bbox(self):
        bbox1 = BoundingBox([(0, 0, 0), (10, 10, 10)])
        bbox = BoundingBox().union(bbox1)
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

    def test_union_empty_bounding_boxes(self):
        bbox = BoundingBox().union(BoundingBox())
        assert bbox.is_empty is True

    def test_rect_vertices_for_empty_bbox_raises_value_error(self):
        with pytest.raises(ValueError):
            BoundingBox().rect_vertices()

    def test_cube_vertices_for_empty_bbox_raises_value_error(self):
        with pytest.raises(ValueError):
            BoundingBox().cube_vertices()

    def test_rect_vertices_returns_vertices_in_counter_clockwise_order(self):
        bbox = BoundingBox([(0, 0, 0), (1, 2, 3)])
        assert bbox.rect_vertices() == Vec2.tuple(
            [(0, 0), (1, 0), (1, 2), (0, 2)]
        )

    def test_cube_vertices_returns_vertices_in_counter_clockwise_order(self):
        bbox = BoundingBox([(0, 0, 0), (1, 2, 3)])
        assert bbox.cube_vertices() == Vec3.tuple(
            [
                (0, 0, 0),  # bottom layer
                (1, 0, 0),
                (1, 2, 0),
                (0, 2, 0),
                (0, 0, 3),  # top layer
                (1, 0, 3),
                (1, 2, 3),
                (0, 2, 3),
            ]
        )


class TestBoundingBox2d:
    def test_init(self):
        bbox = BoundingBox2d([(0, 0), (10, 10)])
        assert bbox.extmin == (0, 0)
        assert bbox.extmax == (10, 10)

        bbox = BoundingBox2d([(7, -2), (-1, 8)])
        assert bbox.extmin == (-1, -2)
        assert bbox.extmax == (7, 8)

    def test_init_with_with_empty_list(self):
        assert BoundingBox2d([]).is_empty is True

    def test_init_none(self):
        bbox = BoundingBox2d()
        assert bbox.has_data is False
        bbox.extend([(0, 0), (10, 10)])
        assert bbox.size == (10, 10)
        assert bbox.has_data is True

    def test_inside(self):
        bbox = BoundingBox2d([(0, 0), (10, 10)])
        assert bbox.inside((0, 0)) is True
        assert bbox.inside((-1, 0)) is False
        assert bbox.inside((0, -1)) is False

        assert bbox.inside((5, 5)) is True

        assert bbox.inside((10, 10)) is True
        assert bbox.inside((11, 10)) is False
        assert bbox.inside((10, 11)) is False

    def test_extend(self):
        bbox = BoundingBox2d([(0, 0), (10, 10)])
        bbox.extend([(5, 5)])
        assert bbox.extmin == (0, 0)
        assert bbox.extmax == (10, 10)

        bbox.extend([(15, 16)])
        assert bbox.extmin == (0, 0)
        assert bbox.extmax == (15, 16)

        bbox.extend([(-15, -16)])
        assert bbox.extmin == (-15, -16)
        assert bbox.extmax == (15, 16)

    def test_size(self):
        bbox = BoundingBox2d([(-2, -2), (8, 8)])
        assert bbox.size == (10, 10)

    def test_center(self):
        bbox = BoundingBox2d([(-1, -1), (9, 9)])
        assert bbox.center == (4, 4)

    def test_rect_vertices_for_empty_bbox_raises_value_error(self):
        with pytest.raises(ValueError):
            BoundingBox2d().rect_vertices()

    def test_rect_vertices_returns_vertices_in_counter_clockwise_order(self):
        bbox = BoundingBox2d([(0, 0, 0), (1, 2, 3)])
        assert bbox.rect_vertices() == Vec2.tuple(
            [(0, 0), (1, 0), (1, 2), (0, 2)]
        )
