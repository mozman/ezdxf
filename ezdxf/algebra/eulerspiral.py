# Created: 26.03.2010
# License: MIT License
from ezdxf.algebra import Vector
from ezdxf.algebra.bspline import bspline_control_frame


class EulerSpiral(object):
    """
    This object represents an euler spiral (clothoid) for parameter A (Radius of curvature).
    This is a parametric curve, which always starts at the origin = (0, 0).

    """
    def __init__(self, A=1.0):
        self.A = A  # Radius of curvature
        self.powersA = [A ** power for power in range(19)]
        self._cache = {}  # coordinates cache

    def radius(self, t):
        """
        Get radius of circle at distance <L>.
        """
        if t > 0.:
            return self.powersA[2] / t
        else:
            return 0.  # radius = infinite

    def tangent(self, t):
        """
        Get tangent at distance t as Vector() object.

        """
        angle = t ** 2 / (2. * self.powersA[2])
        return Vector.from_rad_angle(angle)

    def distance(self, radius):
        """
        Get distance L from origin for radius.

        """
        return self.powersA[2] / float(radius)

    def point(self, t):
        """
        Get point at distance t as Vector().

        """
        def term(powerL, powerA, const):
            return t ** powerL / (const * self.powersA[powerA])

        if t not in self._cache:
            y = term(3, 2, 6.) - term(7, 6, 336.) + term(11, 10, 42240.) - \
                term(15, 14, 9676800.) + term(19, 18, 3530096640.)
            x = t - term(5, 4, 40.) + term(9, 8, 3456.) - term(13, 12, 599040.) + \
                term(17, 16, 175472640.)
            self._cache[t] = Vector(x, y)
        return self._cache[t]

    def approximate(self, length, segments):
        """
        Approximate curve of length with line segments.

        Generates segments+1 vertices as Vector() objects.

        """
        delta_l = float(length) / float(segments)
        yield Vector(0, 0)
        for index in range(1, segments + 1):
            yield self.point(delta_l * index)

    def circle_midpoint(self, t):
        """
        Get circle midpoint at distance t.

        """
        p = self.point(t)
        r = self.radius(t)
        return p + self.tangent(t).normalize(r).orthogonal()

    def bspline(self, length, segments=10, degree=3, method='uniform'):
        fit_points = list(self.approximate(length, segments=segments))
        spline = bspline_control_frame(fit_points, degree, method=method)
        knots = [v*length for v in spline.knot_values()]  # scale knot values to length
        spline.basis.knots = knots
        return spline
