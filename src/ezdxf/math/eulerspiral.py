# Copyright (c) 2010-2021, Manfred Moitzi
# License: MIT License
from typing import Dict, Iterable
from ezdxf.math import Vec3
from ezdxf.math.bspline import global_bspline_interpolation, BSpline

__all__ = ["EulerSpiral"]


class EulerSpiral:
    """
    This class represents an euler spiral (clothoid) for `curvature` (Radius of
    curvature).

    This is a parametric curve, which always starts at the origin = ``(0, 0)``.

    Args:
        curvature: radius of curvature

    """

    def __init__(self, curvature: float = 1.0):
        self.curvature = curvature  # Radius of curvature
        self.curvature_powers = [curvature ** power for power in range(19)]
        self._cache = {}  # type: Dict[float, Vec3] # coordinates cache

    def radius(self, t: float) -> float:
        """Get radius of circle at distance `t`."""
        if t > 0.0:
            return self.curvature_powers[2] / t
        else:
            return 0.0  # radius = infinite

    def tangent(self, t: float) -> Vec3:
        """Get tangent at distance `t` as :class.`Vec3` object."""
        angle = t ** 2 / (2.0 * self.curvature_powers[2])
        return Vec3.from_angle(angle)

    def distance(self, radius: float) -> float:
        """Get distance L from origin for `radius`."""
        return self.curvature_powers[2] / float(radius)

    def point(self, t: float) -> Vec3:
        """Get point at distance `t` as :class.`Vec3`."""

        def term(length_power, curvature_power, const):
            return t ** length_power / (
                const * self.curvature_powers[curvature_power]
            )

        if t not in self._cache:
            y = (
                term(3, 2, 6.0)
                - term(7, 6, 336.0)
                + term(11, 10, 42240.0)
                - term(15, 14, 9676800.0)
                + term(19, 18, 3530096640.0)
            )
            x = (
                t
                - term(5, 4, 40.0)
                + term(9, 8, 3456.0)
                - term(13, 12, 599040.0)
                + term(17, 16, 175472640.0)
            )
            self._cache[t] = Vec3(x, y)
        return self._cache[t]

    def approximate(self, length: float, segments: int) -> Iterable[Vec3]:
        """Approximate curve of length with line segments.
        Generates segments+1 vertices as :class:`Vec3` objects.

        """
        delta_l = float(length) / float(segments)
        yield Vec3(0, 0)
        for index in range(1, segments + 1):
            yield self.point(delta_l * index)

    def circle_center(self, t: float) -> Vec3:
        """Get circle center at distance `t`."""
        p = self.point(t)
        r = self.radius(t)
        return p + self.tangent(t).normalize(r).orthogonal()

    def bspline(
        self,
        length: float,
        segments: int = 10,
        degree: int = 3,
        method: str = "uniform",
    ) -> BSpline:
        """Approximate euler spiral as B-spline.

        Args:
            length: length of euler spiral
            segments: count of fit points for B-spline calculation
            degree: degree of BSpline
            method: calculation method for parameter vector t

        Returns:
            :class:`BSpline`

        """
        fit_points = list(self.approximate(length, segments=segments))
        spline = global_bspline_interpolation(fit_points, degree, method=method)
        return BSpline(
            spline.control_points,
            spline.order,
            # Scale knot values to length:
            [v * length for v in spline.knots()],
        )
