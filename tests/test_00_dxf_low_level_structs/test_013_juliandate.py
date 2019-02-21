# Created: 21.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from datetime import datetime

from ezdxf.tools.juliandate import juliandate, calendardate


class TestJulianDate:
    def test_1582_10_15(self):
        assert 2299161. == pytest.approx(juliandate(datetime(1582, 10, 15)))

    def test_1990_01_01(self):
        assert 2447893. == pytest.approx(juliandate(datetime(1990, 1, 1)))

    def test_2000_01_01(self):
        assert 2451545. == pytest.approx(juliandate(datetime(2000, 1, 1)))

    def test_2011_03_21(self):
        assert 2455642.75 == pytest.approx(juliandate(datetime(2011, 3, 21, 18, 0, 0)))

    def test_1999_12_31(self):
        assert 2451544.91568287 == pytest.approx(juliandate(datetime(1999, 12, 31, 21, 58, 35)))


class TestCalendarDate:
    def test_1999_12_31(self):
        check = datetime(1999, 12, 31, 21, 58, 35)
        assert calendardate(2451544.91568288) == check

    def test_2011_03_21(self):
        check = datetime(2011, 3, 21, 18, 0, 0)
        assert calendardate(2455642.75) == check
