#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

import pytest
import math

from ezdxf.math import ellipse_param_span, arc_angle_span_deg, arc_angle_span_rad


class TestArcParamSpan:
    def span(self, s, e):
        return arc_angle_span_deg(s, e)

    @pytest.mark.parametrize(
        "start, end",
        [
            (0, 0),
            (90, 90),
            (-90, -90),
            (180, 180),
            (-180, -180),
            (270, 270),
            (-270, -270),
            (360, 360),
            (-360, -360),
            (720, 720),
            (-720, -720),
        ],
    )
    def test_no_curve(self, start, end):
        assert self.span(start, end) == pytest.approx(0)

    @pytest.mark.parametrize(
        "start, end",
        [
            # full circles:
            # Normalized start- and end angles are equal, but input values are
            # different:
            (0, 360),
            (360, 0),
            (-360, 0),
            (0, -360),
            (90, 450),
            (180, 540),
            (180, -180),
            (-180, 180),
            (90, -270),
            (-90, 270),
        ],
    )
    def test_closed_curve(self, start, end):
        assert self.span(start, end) == pytest.approx(360.0)

    @pytest.mark.parametrize(
        "start, end, expected",
        [
            (0, 90, 90),
            (0, -90, 270),
            (0, 180, 180),
            (0, -180, 180),
            (180, 360, 180),
            (-180, -360, 180),
            (-90, 360, 90),
            (90, -360, 270),
            (-90, -360, 90),
            (90, 360, 270),
            (360, 90, 90),  # start angle 360 is 0
            (360, -90, 270),  # start angle 360 is 0
            (-360, 90, 90),  # start angle -360 is 0
            (-360, -90, 270),  # start angle -360 is 0
            (30, -30, 300),  # crossing 0 deg
            (-30, 30, 60),  # crossing 0 deg
            (90, -90, 180),
            (-90, 90, 180),
            (360, 400, 40),
            (400, 360, 320),
        ],
    )
    def test_partial_arc(self, start, end, expected):
        assert self.span(start, end) == pytest.approx(expected)


class TestEllipseParamSpan(TestArcParamSpan):
    def span(self, s, e):
        return math.degrees(
            ellipse_param_span(math.radians(s), math.radians(e))
        )


class TestArcParamSpanRadians(TestArcParamSpan):
    def span(self, s, e):
        return math.degrees(
            arc_angle_span_rad(math.radians(s), math.radians(e))
        )


PI2 = math.pi / 2.0


class TestParamSpan:
    # Preserved old param span test.
    # This tests work without degrees-radians-degrees conversion
    @pytest.mark.parametrize(
        "start, end",
        [
            (0, 0),
            (math.pi, math.pi),
            (math.tau, math.tau),
            (0, 0),
            (-math.pi, -math.pi),
            (-math.tau, -math.tau),
        ],
    )
    def test_no_ellipse(self, start, end):
        assert ellipse_param_span(start, end) == 0.0

    @pytest.mark.parametrize(
        "start, end",
        [
            (0, math.tau),
            (math.tau, 0),
            (math.pi, -math.pi),
            (0, -math.tau),
            (-math.tau, 0),
            (-math.pi, math.pi),
        ],
    )
    def test_full_ellipse(self, start, end):
        assert ellipse_param_span(start, end) == pytest.approx(math.tau)

    @pytest.mark.parametrize(
        "start, end, expected",
        [
            (0, PI2, PI2),
            (PI2, 0, math.pi * 1.5),
            (PI2, math.pi, PI2),
            (PI2, -PI2, math.pi),
            (math.pi, 0, math.pi),
            (0, math.pi, math.pi),
            (0, -PI2, math.pi * 1.5),
            (-PI2, 0, PI2),
            (-PI2, -math.pi, math.pi * 1.5),
            (-PI2, PI2, math.pi),
            (-math.pi, 0, math.pi),
            (0, -math.pi, math.pi),
        ],
    )
    def test_elliptic_arc(self, start, end, expected):
        assert ellipse_param_span(start, end) == pytest.approx(expected)


if __name__ == "__main__":
    pytest.main([__file__])
