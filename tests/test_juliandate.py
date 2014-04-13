#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test julian date
# Created: 21.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals

import unittest

from datetime import datetime
from ezdxf.juliandate import juliandate, calendardate


class TestJulianDate(unittest.TestCase):
    def test_1582_10_15(self):
        self.assertAlmostEqual(2299161., juliandate(datetime(1582, 10, 15)))

    def test_1990_01_01(self):
        self.assertAlmostEqual(2447893., juliandate(datetime(1990, 1, 1)))

    def test_2000_01_01(self):
        self.assertAlmostEqual(2451545., juliandate(datetime(2000, 1, 1)))

    def test_2011_03_21(self):
        self.assertAlmostEqual(2455642.75, juliandate(datetime(2011, 3, 21, 18, 0, 0)))

    def test_1999_12_31(self):
        self.assertAlmostEqual(2451544.91568287, juliandate(datetime(1999, 12, 31, 21, 58, 35)))


class TestCalendarDate(unittest.TestCase):
    def test_1999_12_31(self):
        self.assertEqual(calendardate(2451544.91568288), datetime(1999, 12, 31, 21, 58, 35))

    def test_2011_03_21(self):
        self.assertEqual(calendardate(2455642.75), datetime(2011, 3, 21, 18, 0, 0))


if __name__ == '__main__':
    unittest.main()