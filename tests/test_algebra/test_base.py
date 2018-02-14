# Created: 14.11.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License
import unittest
from ezdxf.algebra.base import *


class TestAlgebraBse(unittest.TestCase):
    def test_rotate_2s(self):
        result = rotate_2d((5, 0), HALF_PI)
        self.assertAlmostEqual(result[0], 0.)
        self.assertAlmostEqual(result[1], 5.)

    def test_normalize_angle(self):
        angle = 2
        huge_angle = angle + 16 * HALF_PI
        self.assertAlmostEqual(normalize_angle(huge_angle), 2.)

    def test_is_vertical_angle(self):
        self.assertTrue(is_vertical_angle(HALF_PI))
        self.assertFalse(is_vertical_angle(2 * HALF_PI))

    def test_get_angle(self):
        self.assertAlmostEqual(get_angle((0., 0.), (0., 1.)), HALF_PI)
        self.assertAlmostEqual(get_angle((0., 0.), (1., 1.)), HALF_PI / 2.)

    def test_right_of_line(self):
        self.assertTrue(right_of_line((1, 0), (0, 0), (0, 1)))
        self.assertFalse(left_of_line((1, 0), (0, 0), (0, 1)))
        self.assertTrue(right_of_line((1, 1), (0, 0), (-1, 0)))

    def test_left_of_line(self):
        self.assertTrue(left_of_line((-1, 0), (0, 0), (0.1, 1)))
        self.assertTrue(left_of_line((1, 0), (0, 0), (0, -1)))
        self.assertTrue(left_of_line((-1, -1), (0, 0), (0.1, 1)))
        self.assertFalse(right_of_line((-1, 0), (0, 0), (-1, .1)))
