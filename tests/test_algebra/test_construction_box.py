# Purpose: test ConstructionBox
# Created: 29.01.2019
# License: MIT License

from ezdxf.algebra import ConstructionBox, ConstructionLine


class TestTextBox:
    def test_defaults(self):
        box = ConstructionBox()
        assert box.center == (0, 0)
        assert box.width == 1
        assert box.height == 1
        assert box.angle == 0
        assert box[0] == (-.5, -.5)
        assert box[1] == (+.5, -.5)
        assert box[2] == (+.5, +.5)
        assert box[3] == (-.5, +.5)

    def test_init(self):
        box = ConstructionBox(center=(5, 0.5), width=10, height=1, angle=0)
        assert box.center == (5, .5)
        p1, p2, p3, p4 = box.corners
        assert p1 == (0, 0)
        assert p2 == (10, 0)
        assert p3 == (10, 1)
        assert p4 == (0, 1)

    def test_from_points(self):
        box = ConstructionBox.from_points((2, 1), (4, 5))
        assert box.center == (3, 3)
        assert box.width == 2
        assert box.height == 4
        assert box.angle == 0
        # reverse order, same result
        box = ConstructionBox.from_points((4, 5), (2, 1))
        assert box.center == (3, 3)
        assert box.width == 2
        assert box.height == 4
        assert box.angle == 0

    def test_init_angle_90(self):
        box = ConstructionBox(center=(.5, 5), width=10, height=1, angle=90)
        assert box.center == (.5, 5)
        p1, p2, p3, p4 = box.corners
        assert p1 == (1, 0)
        assert p2 == (1, 10)
        assert p3 == (0, 10)
        assert p4 == (0, 0)

    def test_set_center(self):
        box = ConstructionBox()
        box.center = (.5, .5)
        assert box.center == (.5, .5)
        assert box[0] == (0, 0)

    def test_set_width(self):
        box = ConstructionBox()
        box.width = -3
        assert box.width == 3
        assert box.center == (0, 0)
        assert box[0] == (-1.5, -.5)
        assert box[2] == (+1.5, +.5)

    def test_set_height(self):
        box = ConstructionBox()
        box.height = -4
        assert box.height == 4
        assert box.center == (0, 0)
        assert box[0] == (-0.5, -2)
        assert box[2] == (+0.5, +2)

    def test_set_angle(self):
        box = ConstructionBox()
        box.width = 3
        box.angle = 90
        assert box.angle == 90
        assert box.center == (0, 0)
        assert box[0] == (+0.5, -1.5)
        assert box[2] == (-0.5, +1.5)

    def test_move(self):
        box = ConstructionBox()
        box.move(3, 4)
        assert box.center == (3, 4)
        assert box[0] == (2.5, 3.5)
        assert box[2] == (3.5, 4.5)

    def test_expand(self):
        box = ConstructionBox()
        box.expand(2, 3)
        assert box.width == 3
        assert box.height == 4
        assert box[0] == (-1.5, -2)
        assert box[2] == (+1.5, +2)

    def test_scale(self):
        box = ConstructionBox(width=3, height=4)
        box.scale(1.5, 2.5)
        assert box.width == 4.5
        assert box.height == 10
        assert box[0] == (-2.25, -5)
        assert box[2] == (+2.25, +5)

    def test_intersect_0(self):
        box = ConstructionBox(center=(5, 0.5), width=10, height=1, angle=0)
        line = ConstructionLine((0, 2), (1, 2))  # above box
        assert len(box.intersect(line)) == 0

    def test_intersect_1(self):
        box = ConstructionBox(center=(5, 0.5), width=10, height=1, angle=0)
        line = ConstructionLine((10, 1), (11, 2))  # touch one corner
        result = box.intersect(line)
        assert len(result) == 1
        assert result[0] == (10, 1)

    def test_intersect_2(self):
        box = ConstructionBox(center=(5, 0.5), width=10, height=1, angle=0)
        line = ConstructionLine((5, -1), (5, 2))
        result = box.intersect(line)
        assert len(result) == 2
        assert result[0] == (5, 0)
        assert result[1] == (5, 1)

    def test_is_inside_horiz_box(self):
        box = ConstructionBox()
        assert box.is_inside((0, 0)) is True
        # on border is inside
        assert box.is_inside((0.5, 0.5)) is True
        assert box.is_inside(box[0]) is True
        assert box.is_inside(box[1]) is True
        assert box.is_inside(box[2]) is True
        assert box.is_inside(box[3]) is True

        # outside
        assert box.is_inside((1, 1)) is False
        assert box.is_inside((-1, -1)) is False
        assert box.is_inside((-1, +1)) is False
        assert box.is_inside((+1, -1)) is False

        # outside but on extension lines
        assert box.is_inside((1, .5)) is False
        assert box.is_inside((-1, -.5)) is False
        assert box.is_inside((-1, .5)) is False
        assert box.is_inside((+1, -.5)) is False

    def test_is_inside_rotated_box(self):
        box = ConstructionBox(angle=67)
        assert box.is_inside((0, 0)) is True
        # on border is inside
        assert box.is_inside(box[0]) is True
        assert box.is_inside(box[1]) is True
        assert box.is_inside(box[2]) is True
        assert box.is_inside(box[3]) is True

        # outside
        assert box.is_inside((1, 1)) is False
        assert box.is_inside((-1, -1)) is False
        assert box.is_inside((-1, +1)) is False
        assert box.is_inside((+1, -1)) is False

