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
            assert a.has_intersection(b) is True
            assert a.has_overlap(b) is True

    def test_do_not_intersect_or_overlap(self):
        bbox1 = BoundingBox([(0, 0, 0), (3, 3, 3)])
        bbox2 = BoundingBox([(4, 4, 4), (9, 9, 9)])
        bbox3 = BoundingBox([(-2, -2, -2), (-1, -1, -1)])
        for a, b in permutations([bbox1, bbox2, bbox3], 2):
            assert a.has_intersection(b) is False
            assert a.has_overlap(b) is False

    def test_do_not_intersect_or_overlap_empty(self):
        bbox = BoundingBox([(0, 0, 0), (3, 3, 3)])
        empty = BoundingBox()
        assert bbox.has_intersection(empty) is False
        assert bbox.has_overlap(empty) is False
        assert empty.has_intersection(bbox) is False
        assert empty.has_overlap(bbox) is False
        assert empty.has_intersection(empty) is False
        assert empty.has_overlap(empty) is False

    def test_crossing_2d_boxes(self):
        # bboxes do overlap, but do not contain corner points of the other bbox
        bbox1 = BoundingBox2d([(0, 1), (3, 2)])
        bbox2 = BoundingBox2d([(1, 0), (2, 3)])
        assert bbox1.has_intersection(bbox2) is True
        assert bbox1.has_overlap(bbox2) is True

    def test_crossing_3d_boxes(self):
        # bboxes do overlap, but do not contain corner points of the other bbox
        bbox1 = BoundingBox([(0, 1, 0), (3, 2, 1)])
        bbox2 = BoundingBox([(1, 0, 0), (2, 3, 1)])
        assert bbox1.has_intersection(bbox2) is True
        assert bbox1.has_overlap(bbox2) is True

    def test_touching_2d_boxes(self):
        bbox1 = BoundingBox2d([(0, 0), (1, 1)])
        bbox2 = BoundingBox2d([(1, 1), (2, 2)])
        bbox3 = BoundingBox2d([(-1, -1), (0, 0)])
        assert bbox1.has_intersection(bbox2) is False
        assert bbox1.has_overlap(bbox2) is True
        assert bbox2.has_intersection(bbox1) is False
        assert bbox2.has_overlap(bbox1) is True
        assert bbox1.has_intersection(bbox3) is False
        assert bbox1.has_overlap(bbox3) is True
        assert bbox3.has_intersection(bbox1) is False
        assert bbox3.has_overlap(bbox1) is True

    def test_touching_3d_boxes(self):
        bbox1 = BoundingBox([(0, 0, 0), (1, 1, 1)])
        bbox2 = BoundingBox([(1, 1, 1), (2, 2, 2)])
        bbox3 = BoundingBox([(-1, -1, -1), (0, 0, 0)])
        assert bbox1.has_intersection(bbox2) is False
        assert bbox1.has_overlap(bbox2) is True
        assert bbox2.has_intersection(bbox1) is False
        assert bbox2.has_overlap(bbox1) is True
        assert bbox1.has_intersection(bbox3) is False
        assert bbox1.has_overlap(bbox3) is True
        assert bbox3.has_intersection(bbox1) is False
        assert bbox3.has_overlap(bbox1) is True

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

    def test_contains_other_bounding_box(self):
        box_a = BoundingBox([(0, 0, 0), (10, 10, 10)])
        box_b = BoundingBox([(1, 1, 1), (9, 9, 9)])
        box_c = BoundingBox([(1, 1, 1), (11, 11, 11)])
        assert box_a.contains(box_b) is True
        assert box_a.contains(box_a) is True  # self contained
        assert box_b.contains(box_a) is False
        assert box_a.contains(box_c) is False

    def test_growing_empty_bounding_box_does_nothing(self):
        box = BoundingBox()
        box.grow(1)
        assert box.has_data is False

    def test_grow_bounding_box(self):
        box = BoundingBox([(0, 0, 0), (1, 1, 1)])
        box.grow(1)
        assert box.extmin.isclose((-1, -1, -1))
        assert box.extmax.isclose((2, 2, 2))

    def test_shrinking_to_zero_or_below_raises_exception(self):
        box = BoundingBox([(0, 0, 0), (1, 1, 1)])
        with pytest.raises(ValueError):
            box.grow(-0.5)


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

    def test_contains_other_bounding_box(self):
        box_a = BoundingBox2d([(0, 0), (10, 10)])
        box_b = BoundingBox2d([(1, 1), (9, 9)])
        box_c = BoundingBox2d([(1, 1), (11, 11)])
        assert box_a.contains(box_b) is True
        assert box_a.contains(box_a) is True  # self contained!
        assert box_b.contains(box_a) is False
        assert box_a.contains(box_c) is False

    def test_2d_box_contains_3d_box(self):
        box_a = BoundingBox2d(
            [(0, 0), (10, 10)]
        )  # this is flat-land, z-axis does not exist
        box_b = BoundingBox([(1, 1, 1), (9, 9, 9)])
        assert box_a.contains(box_b) is True, "z-axis should be ignored"

    def test_3d_box_contains_2d_box(self):
        box_a = BoundingBox2d(
            [(1, 1), (9, 9)]
        )  # lives in the xy-plane, z-axis is 0
        box_b = BoundingBox([(0, 0, 0), (10, 10, 10)])
        assert box_b.contains(box_a) is True, "xy-plane is included"
        box_c = BoundingBox([(0, 0, 1), (10, 10, 10)])
        assert box_c.contains(box_a) is False, "xy-plane is not included"

    def test_grow_bounding_box(self):
        box = BoundingBox2d([(0, 0), (1, 1)])
        box.grow(1)
        assert box.extmin.isclose((-1, -1))
        assert box.extmax.isclose((2, 2))


class Test2DIntersection:
    def test_type_check(self):
        with pytest.raises(TypeError):
            BoundingBox2d().intersection(BoundingBox())

    def test_empty_box_intersection(self):
        b = BoundingBox2d().intersection(BoundingBox2d())
        assert b.is_empty is True

    def test_no_intersection(self):
        b1 = BoundingBox2d([(0, 0), (1, 1)])
        b2 = BoundingBox2d([(2, 2), (3, 3)])
        b = b1.intersection(b2)
        assert b.is_empty is True

    def test_intersection_at_corner(self):
        b1 = BoundingBox2d([(0, 0), (1, 1)])
        b2 = BoundingBox2d([(1, 1), (2, 2)])
        b = b1.intersection(b2)
        assert b.is_empty is False
        assert b.size.isclose((0, 0))
        assert b.extmin.isclose((1, 1))
        assert b.extmax.isclose((1, 1))

    def test_half_intersection(self):
        b1 = BoundingBox2d([(0, 0), (2, 2)])
        b2 = BoundingBox2d([(1, 1), (3, 3)])
        b = b1.intersection(b2)
        assert b.size.isclose((1, 1))
        assert b.extmin.isclose((1, 1))
        assert b.extmax.isclose((2, 2))

    def test_full_intersection(self):
        b1 = BoundingBox2d([(0, 0), (2, 2)])
        b = b1.intersection(b1)
        assert b.size.isclose((2, 2))
        assert b.extmin.isclose((0, 0))
        assert b.extmax.isclose((2, 2))

    def test_smaller_inside_bigger_intersection(self):
        b1 = BoundingBox2d([(0, 0), (3, 3)])
        b2 = BoundingBox2d([(1, 1), (2, 2)])
        b = b1.intersection(b2)
        assert b.size.isclose((1, 1))
        assert b.extmin.isclose((1, 1))
        assert b.extmax.isclose((2, 2))


class Test3DIntersection:
    def test_type_check(self):
        with pytest.raises(TypeError):
            BoundingBox().intersection(BoundingBox2d())

    def test_empty_box_intersection(self):
        b = BoundingBox().intersection(BoundingBox())
        assert b.is_empty is True

    def test_no_intersection(self):
        b1 = BoundingBox([(0, 0, 0), (1, 1, 1)])
        b2 = BoundingBox([(2, 2, 2), (3, 3, 3)])
        b = b1.intersection(b2)
        assert b.is_empty is True

    def test_intersection_at_corner(self):
        b1 = BoundingBox([(0, 0, 0), (1, 1, 1)])
        b2 = BoundingBox([(1, 1, 1), (2, 2, 2)])
        b = b1.intersection(b2)
        assert b.is_empty is False
        assert b.size.isclose((0, 0, 0))
        assert b.extmin.isclose((1, 1, 1))
        assert b.extmax.isclose((1, 1, 1))

    def test_half_intersection(self):
        b1 = BoundingBox([(0, 0, 0), (2, 2, 2)])
        b2 = BoundingBox([(1, 1, 1), (3, 3, 3)])
        b = b1.intersection(b2)
        assert b.size.isclose((1, 1, 1))
        assert b.extmin.isclose((1, 1, 1))
        assert b.extmax.isclose((2, 2, 2))

    def test_full_intersection(self):
        b1 = BoundingBox([(0, 0, 0), (2, 2, 2)])
        b = b1.intersection(b1)
        assert b.size.isclose((2, 2, 2))
        assert b.extmin.isclose((0, 0, 0))
        assert b.extmax.isclose((2, 2, 2))

    def test_smaller_inside_bigger_intersection(self):
        b1 = BoundingBox([(0, 0, 0), (3, 3, 3)])
        b2 = BoundingBox([(1, 1, 1), (2, 2, 2)])
        b = b1.intersection(b2)
        assert b.size.isclose((1, 1, 1))
        assert b.extmin.isclose((1, 1, 1))
        assert b.extmax.isclose((2, 2, 2))
