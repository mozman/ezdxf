# Purpose: test TextBox
# Created: 27.01.2019
# License: MIT License

from ezdxf.render.dimension import TextBox, ConstructionLine


class TestTextBox:
    def test_init_no_gap(self):
        box = TextBox(center=(5, 0.5), width=10, height=1, angle=0)
        assert box.center == (5, .5)
        p1, p2, p3, p4 = box.corners
        assert p1 == (0, 0)
        assert p2 == (10, 0)
        assert p3 == (10, 1)
        assert p4 == (0, 1)

    def test_init_with_gap(self):
        box = TextBox(center=(5, 0.5), width=10, height=1, angle=0, gap=.5)
        assert box.center == (5, .5)
        p1, p2, p3, p4 = box.corners
        assert p1 == (-.5, -.5)
        assert p2 == (10.5, -.5)
        assert p3 == (10.5, 1.5)
        assert p4 == (-.5, 1.5)

    def test_init_angle_90(self):
        box = TextBox(center=(.5, 5), width=10, height=1, angle=90)
        assert box.center == (.5, 5)
        p1, p2, p3, p4 = box.corners
        assert p1 == (1, 0)
        assert p2 == (1, 10)
        assert p3 == (0, 10)
        assert p4 == (0, 0)

    def test_intersect_0(self):
        box = TextBox(center=(5, 0.5), width=10, height=1, angle=0)
        line = ConstructionLine((0, 2), (1, 2))  # above text box
        assert len(box.intersect(line)) == 0

    def test_intersect_1(self):
        box = TextBox(center=(5, 0.5), width=10, height=1, angle=0)
        line = ConstructionLine((10, 1), (11, 2))  # touch one corner
        result = box.intersect(line)
        assert len(result) == 1
        assert result[0] == (10, 1)

    def test_intersect_2(self):
        box = TextBox(center=(5, 0.5), width=10, height=1, angle=0)
        line = ConstructionLine((5, -1), (5, 2))
        result = box.intersect(line)
        assert len(result) == 2
        assert result[0] == (5, 0)
        assert result[1] == (5, 1)


