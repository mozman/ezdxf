# Copyright (c) 2010 Manfred Moitzi
# License: MIT License

import unittest

from ezdxf.algebra.bezier4p import Bezier4P

points = [(0.000, 0.000),
          (0.928, 0.280),
          (1.904, 1.040),
          (2.916, 2.160),
          (3.952, 3.520),
          (5.000, 5.000),
          (6.048, 6.480),
          (7.084, 7.840),
          (8.096, 8.960),
          (9.072, 9.720),
          (10.00, 10.00)]

tangents = [(9.0, 0.0),
            (9.5400000000000009, 5.3999999999999995),
            (9.9600000000000009, 9.6000000000000014),
            (10.26, 12.600000000000001),
            (10.440000000000001, 14.4),
            (10.5, 15.0),
            (10.44, 14.399999999999999),
            (10.260000000000002, 12.600000000000001),
            (9.9599999999999973, 9.5999999999999925),
            (9.5399999999999974, 5.399999999999995),
            (9.0, 0.0)]


class TestCubicBezierCurve(unittest.TestCase):
    def test_points(self):
        bcurve = Bezier4P([(0.,0.), (3.,0.), (7., 10.), (10.,10.)])
        for index, epoint in enumerate(points):
            epx, epy = epoint
            rpx, rpy = bcurve.get_point(index*.1)
            self.assertAlmostEqual(epx, rpx, places=3)
            self.assertAlmostEqual(epy, rpy, places=3)

    def test_tangents(self):
        bcurve = Bezier4P([(0.,0.), (3.,0.), (7., 10.), (10.,10.)])
        for index, epoint in enumerate(tangents):
            etx, ety = epoint
            rtx, rty = bcurve.get_tangent(index*.1)
            self.assertAlmostEqual(etx, rtx, places=3)
            self.assertAlmostEqual(ety, rty, places=3)

