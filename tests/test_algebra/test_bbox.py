# Purpose: test bbox module
# Created: 27.01.2019
# License: MIT License
from ezdxf.algebra.bbox import BoundingBox


class TestBoundingBox:
    def test_init(self):
        bbox = BoundingBox((0, 0, 0), (10, 10, 10))
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

        bbox = BoundingBox((10, 10, 10), (0, 0, 0))
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

        bbox = BoundingBox((7, -2, 9), (-1, 8, -3))
        assert bbox.extmin == (-1, -2, -3)
        assert bbox.extmax == (7, 8, 9)

    def test_inside(self):
        bbox = BoundingBox((0, 0, 0), (10, 10, 10))
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
        bbox = BoundingBox((0, 0, 0), (10, 10, 10))
        bbox.extend([(5, 5, 5)])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (10, 10, 10)

        bbox.extend([(15, 16, 17)])
        assert bbox.extmin == (0, 0, 0)
        assert bbox.extmax == (15, 16, 17)

        bbox.extend([(-15, -16, -17)])
        assert bbox.extmin == (-15, -16, -17)
        assert bbox.extmax == (15, 16, 17)
