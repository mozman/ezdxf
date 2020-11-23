# Copyright (c) 2019-2020, Manfred Moitzi
# License: MIT License
from ezdxf.math import ConstructionLine, Vec2


class TestConstructionLine:
    def test_is_vertical(self):
        assert ConstructionLine((0, 0), (10, 0)).is_vertical is False
        assert ConstructionLine((5, -5), (5, 5)).is_vertical is True

    def test_left_of_line(self):
        line = ConstructionLine((0, 0), (0.1, 1))
        assert line.is_point_left_of_line(Vec2(-1, 0)) is True
        assert line.is_point_left_of_line(Vec2(1, 0)) is False
        assert line.is_point_left_of_line(Vec2(-1, -1)) is True

        line = ConstructionLine((0, 0), (0, -1))
        assert line.is_point_left_of_line(Vec2(1, 0)) is True

        line = ConstructionLine((0, 0), (-1, .1))
        assert line.is_point_left_of_line(Vec2(-1, 0)) is True

        line = ConstructionLine((0, 0), (10, 0))
        assert line.is_point_left_of_line(Vec2(0, 0)) is False
        assert line.is_point_left_of_line(Vec2(10, 0)) is False
        assert line.is_point_left_of_line(Vec2(10, 1)) is True
        assert line.is_point_left_of_line(Vec2(10, -1)) is False

        line = ConstructionLine((10, 0), (0, 0))
        assert line.is_point_left_of_line(Vec2(0, 0)) is False
        assert line.is_point_left_of_line(Vec2(10, 0)) is False
        assert line.is_point_left_of_line(Vec2(10, 1)) is False
        assert line.is_point_left_of_line(Vec2(10, -1)) is True

        line = ConstructionLine((0, 0), (0, 10))
        assert line.is_point_left_of_line(Vec2(0, 0)) is False
        assert line.is_point_left_of_line(Vec2(0, 10)) is False
        assert line.is_point_left_of_line(Vec2(1, 10)) is False
        assert line.is_point_left_of_line(Vec2(-1, 10)) is True

        line = ConstructionLine((0, 10), (0, 0))
        assert line.is_point_left_of_line(Vec2(0, 0)) is False
        assert line.is_point_left_of_line(Vec2(0, 10)) is False
        assert line.is_point_left_of_line(Vec2(1, 10)) is True
        assert line.is_point_left_of_line(Vec2(-1, 10)) is False

    def test_intersect_horizontal_line(self):
        line = ConstructionLine((0, 0), (10, 0))
        assert line.intersect(ConstructionLine((0, 0), (10, 0))) is None
        assert line.intersect(ConstructionLine((0, 1), (10, 1))) is None
        assert line.intersect(ConstructionLine((0, -1), (10, 1))) == (5, 0)
        assert line.intersect(ConstructionLine((5, 5), (5, -5))) == (5, 0)
        assert line.intersect(ConstructionLine((5, 5), (5, 1))) is None
        assert line.intersect(ConstructionLine((0, 0), (5, 5))) == (0, 0)

    def test_intersect_vertical_line(self):
        line = ConstructionLine((0, 0), (0, 10))
        assert line.intersect(ConstructionLine((0, 0), (0, 10))) is None
        assert line.intersect(ConstructionLine((1, 0), (1, 10))) is None
        assert line.intersect(ConstructionLine((-1, 0), (1, 10))) == (0, 5)
        assert line.intersect(ConstructionLine((-1, 0), (1, 0))) == (0, 0)
        assert line.intersect(ConstructionLine((-1, 10), (1, 10))) == (0, 10)
        assert line.intersect(ConstructionLine((-1, 11), (1, 11))) is None

    def test_bounding_box(self):
        line = ConstructionLine((0, 0), (7, 10))
        bbox = line.bounding_box
        assert bbox.extmin == (0, 0)
        assert bbox.extmax == (7, 10)

    def test_translate(self):
        line = ConstructionLine((0, 0), (0, 10))
        line.translate(3, 7)
        assert line.start == (3, 7)
        assert line.end == (3, 17)
        bbox = line.bounding_box
        assert bbox.extmin == (3, 7)
        assert bbox.extmax == (3, 17)
