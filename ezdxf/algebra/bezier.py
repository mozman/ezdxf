# Purpose: general bezier curve
# Created: 26.03.2010
# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from ezdxf.algebra.vector import Vector
"""

Bezier curves
=============

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node3.html

A Bezier curve is a weighted sum of n+1 control points,  P0, P1, ..., Pn, where the weights are the Bernstein 
polynomials. 

The Bezier curve of order n+1 (degree n) has n+1 control points. These are the first three orders of Bezier curve 
definitions. 

(75) linear P(t) = (1-t)*P0 + t*P1
(76) quadratic P(t) = (1-t)^2*P0 + 2*(t-1)*t*P1 + t^2*P2
(77) cubic P(t) = (1-t)^3*P0 + 3*(t-1)^2*t*P1 + 3*(t-1)*t^2*P2 + t^3*P3

Ways of thinking about Bezier curves
------------------------------------

There are several useful ways in which you can think about Bezier curves. Here are the ones that I use.

Linear interpolation
~~~~~~~~~~~~~~~~~~~~

Equation (75) is obviously a linear interpolation between two points. Equation (76) can be rewritten as a linear 
interpolation between linear interpolations between points.

Weighted average
~~~~~~~~~~~~~~~~

A Bezier curve can be seen as a weighted average of all of its control points. Because all of the weights are 
positive, and because the weights sum to one, the Bezier curve is guaranteed to lie within the convex hull of its 
control points.
    
Refinement of the control polygon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Bezier curve can be seen as some sort of refinement of the polygon made by connecting its control points in order. 
The Bezier curve starts and ends at the two end points and its shape is determined by the relative positions of the 
n-1 other control points, although it will generally not pass through these other control points. The tangent vectors 
at the start and end of the curve pass through the end point and the immediately adjacent point.

Continuity
----------

You should note that each Bezier curve is independent of any other Bezier curve. If we wish two Bezier curves to join 
with any type of continuity, then we must explicitly position the control points of the second curve so that they bear 
the appropriate relationship with the control points in the first curve.

Any Bezier curve is infinitely differentiable within itself, and is therefore continuous to any degree.

"""


class Bezier(object):
    """
    A general Bezier curve.

    Accepts 2d points as definition points, but output ist always 3d (z-axis is 0).

    """
    def __init__(self, defpoints):
        self._defpoints = [Vector(p) for p in defpoints]

    @property
    def control_points(self):
        return self._defpoints

    def approximate(self, segments=20):
        step = 1.0 / float(segments)
        for point_index in range(segments + 1):
            yield self.point(point_index * step)

    def point(self, t):
        """
        Returns point at BezierCurve(t) as tuple (x, y, z)

        Args:
            t: parameter in range [0, 1]

        Returns: Vector(x, y, z)

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
    def point(self, t):
        """
        Returns (point, derivative1, derivative2) at BezierCurve(t)

        Args:
            t: parameter in range [0, 1]

        Returns: (point, derivative1, derivative2)
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
    # handle the special cases to avoid domain problem with pow
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
