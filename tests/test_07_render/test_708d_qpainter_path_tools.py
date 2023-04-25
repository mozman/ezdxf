#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import sys

pytest.importorskip("PySide6")

from ezdxf.addons.xqt import QPainterPath, QPointF
from ezdxf import path
from ezdxf.math import quadratic_to_cubic_bezier, Bezier3P


class TestToQPainterPath:
    def test_no_paths(self):
        with pytest.raises(ValueError):
            path.to_qpainter_path([])

    def test_line_to(self):
        p = path.Path()
        p.line_to((4, 5, 6))
        p.line_to((7, 8, 6))
        qpath = path.to_qpainter_path([p])
        assert qpath.elementCount() == 3

        m = qpath.elementAt(0)
        assert m.isMoveTo() is True
        assert (m.x, m.y) == (0, 0)

        l1 = qpath.elementAt(1)
        assert l1.isLineTo() is True
        assert (l1.x, l1.y) == (4, 5)

        l2 = qpath.elementAt(2)
        assert l2.isLineTo() is True
        assert (l2.x, l2.y) == (7, 8)

    def test_curve3_to(self):
        bez3 = Bezier3P([(0, 0), (2, 1), (4, 0)])
        p = path.Path()
        p.curve3_to(bez3.control_points[2], bez3.control_points[1])
        qpath = path.to_qpainter_path([p])
        # Qt converts quadratic bezier curves unto cubic bezier curves
        assert qpath.elementCount() == 4
        bez4 = quadratic_to_cubic_bezier(bez3)

        q1 = qpath.elementAt(1)
        assert q1.isCurveTo()  # start of cure
        assert q1.x, q1.y == bez4.control_points[1]

        q2 = qpath.elementAt(2)
        assert q2.x, q2.y == bez4.control_points[2]

        q3 = qpath.elementAt(3)
        assert q3.x, q3.y == bez4.control_points[2]

    def test_curve4_to(self):
        bez4 = [(4, 0, 2), (1, 1, 7), (3, 1, 5)]
        p = path.Path()
        p.curve4_to(*bez4)
        qpath = path.to_qpainter_path([p])
        assert qpath.elementCount() == 4
        q1 = qpath.elementAt(1)
        assert q1.isCurveTo()  # start of cure
        assert q1.x, q1.y == bez4[1]

        q2 = qpath.elementAt(2)
        assert q2.x, q2.y == bez4[2]

        q3 = qpath.elementAt(3)
        assert q3.x, q3.y == bez4[0]

    def test_two_single_paths(self):
        p1 = path.Path()
        p1.line_to((4, 5, 6))
        p2 = path.Path()
        p2.line_to((7, 8, 6))
        qpath = path.to_qpainter_path([p1, p2])
        assert qpath.elementCount() == 4
        assert qpath.elementAt(0).isMoveTo() is True
        assert qpath.elementAt(1).isLineTo() is True
        assert qpath.elementAt(2).isMoveTo() is True
        assert qpath.elementAt(3).isLineTo() is True

    def test_one_multi_paths(self):
        p = path.Path()
        p.line_to((4, 5, 6))
        p.move_to((0, 0, 0))
        p.line_to((7, 8, 6))
        qpath = path.to_qpainter_path([p])
        assert qpath.elementCount() == 4
        assert qpath.elementAt(0).isMoveTo() is True
        assert qpath.elementAt(1).isLineTo() is True
        assert qpath.elementAt(2).isMoveTo() is True
        assert qpath.elementAt(3).isLineTo() is True

if __name__ == "__main__":
    pytest.main([__file__])
