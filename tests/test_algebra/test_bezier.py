
# Created: 28.03.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
import unittest
from ezdxf.algebra.bezier import CubicBezierCurve

expected_points = [
    (0.0, 0.0),
    (0.16462499999999999, 0.57737499999999997),
    (0.35700000000000004, 1.1090000000000002),
    (0.57487500000000002, 1.594125),
    (0.81600000000000028, 2.0320000000000005),
    (1.078125, 2.421875),
    (1.3590000000000002, 2.7629999999999999),
    (1.6563750000000002, 3.0546249999999997),
    (1.9680000000000002, 3.2960000000000003),
    (2.2916250000000007, 3.4863750000000007),
    (2.625, 3.625), (2.9658750000000005, 3.711125),
    (3.3120000000000007, 3.7440000000000002),
    (3.6611250000000002, 3.7228750000000002),
    (4.011000000000001, 3.6470000000000002),
    (4.359375, 3.515625),
    (4.7040000000000006, 3.3280000000000003),
    (5.042625000000001, 3.0833749999999993),
    (5.3730000000000002, 2.7809999999999997),
    (5.6928750000000008, 2.4201249999999996),
    (6.0, 2.0)
]


class TestAlgebraCubicBezier(unittest.TestCase):
    def test_base_curve(self):
        test_points = [(0, 0), (1, 4), (4, 5), (6, 2)]
        bezier = CubicBezierCurve(test_points)
        results = bezier.approximate(20)
        for expected, result in zip(expected_points, results):
            self.assertAlmostEqual(expected[0], result[0])
            self.assertAlmostEqual(expected[1], result[1])

    def test_init_three_points(self):
        test_points = [(0, 0), (1, 4), (4, 5)]
        self.assertRaises(ValueError, CubicBezierCurve, test_points)

    def test_get_tangent(self):
        bezier = CubicBezierCurve([(0, 0), (1, 4), (4, 5), (6, 2)])
        tangent = bezier.get_tangent(0.5)
        self.assertAlmostEqual(tangent[0], 6.75)
        self.assertAlmostEqual(tangent[1], 2.25)

    def test_get_tangent_error(self):
        bezier = CubicBezierCurve([(0, 0), (1, 4), (4, 5), (6, 2)])
        self.assertRaises(ValueError, bezier.get_tangent, 2.)
        self.assertRaises(ValueError, bezier.get_tangent, -2.)
