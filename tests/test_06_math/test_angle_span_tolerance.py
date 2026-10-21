import math

import pytest

from ezdxf.math import arc_angle_span_deg, arc_angle_span_rad


@pytest.mark.parametrize(
    "span_function,period,width",
    [
        (arc_angle_span_rad, math.tau, 4e-9),
        (arc_angle_span_deg, 360.0, math.degrees(4e-9)),
    ],
)
@pytest.mark.parametrize("fraction", [0.0, 0.25, 0.75, 0.9])
def test_short_span_does_not_depend_on_angular_origin(
    span_function, period, width, fraction
):
    start = fraction * period
    end = start + width
    assert span_function(start, end) == pytest.approx(end - start, rel=0, abs=1e-15)


@pytest.mark.parametrize(
    "span_function,period",
    [(arc_angle_span_rad, math.tau), (arc_angle_span_deg, 360.0)],
)
@pytest.mark.parametrize(
    "start,end,expected",
    [
        (0, 0, 0),
        (0.25, 0.25, 0),
        (0, 1, 1),
        (1, 0, 1),
        (0, 2, 1),
        (0.25, 0.75, 0.5),
        (0.75, 0.25, 0.5),
    ],
)
def test_angle_span_zero_full_and_wrap_controls(
    span_function, period, start, end, expected
):
    assert span_function(start * period, end * period) == pytest.approx(
        expected * period
    )
