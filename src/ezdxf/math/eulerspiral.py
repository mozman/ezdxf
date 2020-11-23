# Copyright (c) 2010-2020, Manfred Moitzi
# License: MIT License
from typing import Dict, Iterable
from ezdxf.math import Vec3
from ezdxf.math.bspline import global_bspline_interpolation, BSpline


class EulerSpiral:
    """
    This class represents an euler spiral (clothoid) for `curvature` (Radius of curvature).

    This is a parametric curve, which always starts at the origin = ``(0, 0)``.

    Args:
        curvature: radius of curvature

    """

    def __init__(self, curvature: float = 1.0):
        self.curvature = curvature  # Radius of curvature
        self.curvature_powers = [curvature ** power for power in range(19)]
        self._cache = {}  # type: Dict[float, Vec3] # coordinates cache

    def radius(self, t: float) -> float:
        """
        Get radius of circle at distance `t`.

        """
        if t > 0.:
            return self.curvature_powers[2] / t
        else:
            return 0.  # radius = infinite

    def tangent(self, t: float) -> Vec3:
        """
        Get tangent at distance `t` as :class.`Vec3` object.

        """
        angle = t ** 2 / (2. * self.curvature_powers[2])
        return Vec3.from_angle(angle)

    def distance(self, radius: float) -> float:
        """
        Get distance L from origin for `radius`.

        """
        return self.curvature_powers[2] / float(radius)

    def point(self, t: float) -> Vec3:
        """
        Get point at distance `t` as :class.`Vec3`.

        """

        def term(length_power, curvature_power, const):
            return t ** length_power / (const * self.curvature_powers[curvature_power])

        if t not in self._cache:
            y = term(3, 2, 6.) - term(7, 6, 336.) + term(11, 10, 42240.) - \
                term(15, 14, 9676800.) + term(19, 18, 3530096640.)
            x = t - term(5, 4, 40.) + term(9, 8, 3456.) - term(13, 12, 599040.) + \
                term(17, 16, 175472640.)
            self._cache[t] = Vec3(x, y)
        return self._cache[t]

    def approximate(self, length: float, segments: int) -> Iterable[Vec3]:
        """
        Approximate curve of length with line segments.

        Generates segments+1 vertices as :class:`Vec3` objects.

        """
        delta_l = float(length) / float(segments)
        yield Vec3(0, 0)
        for index in range(1, segments + 1):
            yield self.point(delta_l * index)

    def circle_center(self, t: float) -> Vec3:
        """
        Get circle center at distance `t`.

        .. versionchanged:: 0.10

                renamed from `circle_midpoint`

        """
        p = self.point(t)
        r = self.radius(t)
        return p + self.tangent(t).normalize(r).orthogonal()

    def bspline(self, length: float, segments: int = 10, degree: int = 3, method: str = 'uniform') -> BSpline:
        """
        Approximate euler spiral as B-spline.

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
        knots = [v * length for v in spline.knot_values()]  # scale knot values to length
        spline.basis.knots = knots
        return spline

    # backward compatibility
    circle_midpoint = circle_center
