# Purpose: 2d bezier curve
# module belongs to package: dxfwrite (ezdxf)
# Created: 26.03.2010
# License: MIT License
__author__ = "mozman <me@mozman.at>"


class CubicBezierCurve(object):
    """
    Implements the classic cubic bezier curve with 4 control points
    """

    def __init__(self, control_points):
        if len(control_points) == 4:
            self._cpoints = [vector2d(vector) for vector in control_points]
        else:
            raise ValueError("Four control points required.")
        self._points = {}
        self._tangents = {}

    def get_tangent(self, position):
        self._check(position)
        if position not in self._tangents:
            self._tangents[position] = self._get_curve_tangent(position)
        return self._tangents[position]

    def get_point(self, position):
        self._check(position)
        if position not in self._points:
            self._points[position] = self._get_curve_point(position)
        return self._points[position]

    def approximate(self, segments):
        delta_t = 1. / segments
        yield self._cpoints[0]
        for segment in range(1, segments):
            yield self.get_point(delta_t*segment)
        yield self._cpoints[3]

    def _check(self, position):
        if not(0 <= position <= 1.):
            raise ValueError("position not in range [0 to 1]")

    def _get_curve_point(self, t):
        """ classic, clear and slow implementation
        """
        b1, b2, b3, b4 = self._cpoints
        one_minus_t = 1. - t
        B = vmul_scalar(b1, one_minus_t**3)
        B = vadd(B, vmul_scalar(b2, 3. * one_minus_t**2 * t))
        B = vadd(B, vmul_scalar(b3, 3. * one_minus_t * t**2))
        B = vadd(B, vmul_scalar(b4, t**3))
        return B

    def _get_curve_tangent(self, t):
        """
        classic, clear and slow implementation

        Returns a vector T which defines the direction of the tangent.
        example: slope of tangent = (y) T[1]/ (x) T[0]
        position of tangent point is defined by the paramter t -> get_cuve_point_by_parameter()
        """
        b1, b2, b3, b4 = self._cpoints
        B = vmul_scalar(b1, -3. * (1. - t)**2)
        B = vadd(B, vmul_scalar(b2, 3. * (1. - 4. * t + 3. * t**2)))
        B = vadd(B, vmul_scalar(b3, 3. * t * (2. - 3. * t)))
        B = vadd(B, vmul_scalar(b4, 3. * t**2))
        return B


def vadd(vector1, vector2):
    """ add vectors """
    return vector1[0]+vector2[0], vector1[1]+vector2[1]


def vmul_scalar(vector, scalar):
    """ mul vector with scalar """
    return vector[0]*scalar, vector[1]*scalar


def vector2d(vector):
    """ return a 2d point """
    return float(vector[0]), float(vector[1])
