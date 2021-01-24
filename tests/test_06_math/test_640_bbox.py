# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License
from ezdxf.math import BoundingBox, BoundingBox2d


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
