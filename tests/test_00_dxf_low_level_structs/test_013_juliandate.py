# Created: 21.03.2011, 2018 rewritten for pytest
# Copyright (C) 2011-2019, Manfred Moitzi
# License: MIT License
import pytest
from datetime import datetime, timedelta

from ezdxf.tools.juliandate import juliandate, calendardate


class TestJulianDate:
    def test_1582_10_15(self):
        assert 2299161.0 == pytest.approx(juliandate(datetime(1582, 10, 15)))

    def test_1990_01_01(self):
        assert 2447893.0 == pytest.approx(juliandate(datetime(1990, 1, 1)))

    def test_2000_01_01(self):
        assert 2451545.0 == pytest.approx(juliandate(datetime(2000, 1, 1)))

    def test_2011_03_21(self):
        assert 2455642.75 == pytest.approx(
            juliandate(datetime(2011, 3, 21, 18, 0, 0))
        )

    def test_1999_12_31(self):
        assert 2451544.91568287 == pytest.approx(
            juliandate(datetime(1999, 12, 31, 21, 58, 35))
        )


class TestCalendarDate:
    def test_1999_12_31(self):
        check = datetime(1999, 12, 31, 21, 58, 35)
        assert calendardate(2451544.91568288) == check

    def test_2011_03_21(self):
        check = datetime(2011, 3, 21, 18, 0, 0)
        assert calendardate(2455642.75) == check


class TestRoundTrip:
    # juliandate() and calendardate() are inverses (used to write/read the
    # $TDCREATE/$TDUPDATE header vars). The round-trip must not lose a second;
    # frac2time() previously truncated frac(jdate) * 86400 with int(), so float
    # imprecision dropped one second on ~50% of timestamps.
    @pytest.mark.parametrize("date", [
        datetime(2020, 1, 1, 0, 0, 1),
        datetime(2030, 2, 28, 6, 15, 7),
        datetime(1999, 12, 31, 23, 59, 59),
        datetime(2000, 2, 29, 12, 0, 0),
        datetime(2011, 3, 21, 18, 0, 0),
        datetime(1990, 1, 1, 0, 0, 0),
    ])
    def test_roundtrip_preserves_seconds(self, date):
        assert calendardate(juliandate(date)) == date

    def test_roundtrip_sweep_loses_nothing(self):
        # Every second over several days must survive the round-trip exactly.
        start = datetime(2020, 6, 1, 0, 0, 0)
        for i in range(0, 200000, 7):
            date = start + timedelta(seconds=i)
            assert calendardate(juliandate(date)) == date

    def test_near_midnight_does_not_overflow(self):
        # A fraction that rounds up toward a full day must clamp to 23:59:59
        # rather than yielding hour == 24 (which would raise ValueError).
        result = calendardate(2451545.0 + 0.99999999)
        assert (result.hour, result.minute, result.second) == (23, 59, 59)
