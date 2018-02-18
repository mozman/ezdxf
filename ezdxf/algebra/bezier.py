# Purpose: 2d bezier curve
# Created: 26.03.2010
# License: MIT License
from ezdxf.algebra.vector import Vector


class Bezier(object):
    """
    Calculate the points of a Bezier curve.

    Initialisation with 2D points is possible, but output ist always 3D (z-axis is 0)
    """

    def __init__(self, defpoints):
        self._defpoints = [Vector(p) for p in defpoints]

    @property
    def breakpoints(self):
        return self._defpoints

    def approximate(self, segments=20):
        step = 1.0 / float(segments)
        for point_index in range(segments + 1):
            yield self.get_point(point_index * step)

    def get_point(self, t):
        """
        Returns point at BezierCurve(t) as tuple (x, y, z)

        Args:
            t: parameter in range [0, 1]

        """
        if t < 0. or t > 1.:
            raise ValueError('parameter t in range [0, 1]')
        if (1.0 - t) < 5e-6:
            t = 1.0
        point = [0., 0., 0.]
        defpoints = self._defpoints
        len_defpoints = len(defpoints)

        for axis in (0, 1, 2):
            for i in range(len_defpoints):
                bsf = bernstein_basis(len_defpoints - 1, i, t)
                point[axis] += bsf * defpoints[i][axis]
        return Vector(point)


class DBezier(Bezier):
    """
    Calculate the Points and Derivative of a Bezier curve.

    """

    def get_point(self, t):
        """
        Returns (point, derivative1, derivative2) at BezierCurve(t)

        Args:
            t: parameter in range [0, 1]

        returns: (point, derivative1, derivative2)
            point -- Vector(x, y, z)
            derivative1 -- Vector(x, y, z)
            derivative2 -- Vector(x, y, z)

        """
        if t < 0. or t > 1.:
            raise ValueError('parameter t in range [0, 1]')

        if (1.0 - t) < 5e-6:
            t = 1.0
        defpoints = self._defpoints
        npts = len(defpoints)
        npts0 = npts - 1
        point = [0., 0., 0.]
        d1 = [0., 0., 0.]
        d2 = [0., 0., 0.]
        for axis in (0, 1, 2):
            if t == 0.0:
                d1[axis] = npts0 * (defpoints[1][axis] - defpoints[0][axis])
                d2[axis] = npts0 * (npts0 - 1) * (defpoints[0][axis] - 2. * defpoints[1][axis] + defpoints[2][axis])
            for i in range(len(defpoints)):
                tempbasis = bernstein_basis(npts0, i, t)
                point[axis] += tempbasis * defpoints[i][axis]
                if 0.0 < t < 1.0:
                    d1[axis] += ((i - npts0 * t) / (t * (1. - t))) * tempbasis * defpoints[i][axis]
                    temp1 = (i - npts0 * t) ** 2
                    temp2 = temp1 - npts0 * t ** 2 - i * (1. - 2. * t)
                    d2[axis] += (temp2 / (t ** 2 * (1. - t) ** 2)) * tempbasis * defpoints[i][axis]
                if t == 1.0:
                    d1[axis] = npts0 * (defpoints[npts0][axis] - defpoints[npts0 - 1][axis])
                    d2[axis] = npts0 * (npts0 - 1) * (defpoints[npts0][axis] - 2 * defpoints[npts0 - 1][axis] +
                                                      defpoints[npts0 - 2][axis])
        return Vector(point), Vector(d1), Vector(d2)


def bernstein_basis(n, i, t):
    # handle the special cases to avoid domain problem with pow */
    if t == 0.0 and i == 0:
        ti = 1.0
    else:
        ti = pow(t, i)
    if n == i and t == 1.0:
        tni = 1.0
    else:
        tni = pow((1.0 - t), (n - i))
    Ni = factorial(n) / (factorial(i) * factorial(n - i))
    return Ni * ti * tni


class _Factorial(object):
    _values = {0: 1.0}

    def __init__(self, maxvalue=33):
        value = 1.
        for i in range(1, maxvalue):
            value *= i
            self._values[i] = value

    def get(self, value):
        value = int(value)
        try:
            return self._values[value]
        except KeyError:
            result = self.get(value - 1) * value
            self._values[value] = result
            return result


_factorial = _Factorial()
factorial = _factorial.get
