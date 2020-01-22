# Purpose: test bbox module
# Created: 27.01.2019
# License: MIT License
from ezdxf.math.bbox import BoundingBox, BoundingBox2d


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

    def test_size(self):
        bbox = BoundingBox([(-2, -2, -2), (8, 8, 8)])
        assert bbox.size == (10, 10, 10)

    def test_center(self):
        bbox = BoundingBox([(-1, -1, -1), (9, 9, 9)])
        assert bbox.center == (4, 4, 4)


class TestBoundingBox2d:
    def test_init(self):
        bbox = BoundingBox2d([(0, 0), (10, 10)])
        assert bbox.extmin == (0, 0)
        assert bbox.extmax == (10, 10)

        bbox = BoundingBox2d([(7, -2), (-1, 8)])
        assert bbox.extmin == (-1, -2)
        assert bbox.extmax == (7, 8)

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
