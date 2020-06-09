# Purpose: general bezier curve
# Created: 26.03.2010
# Copyright (c) 2010-2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable, Tuple, Dict
from ezdxf.math.vector import Vector

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

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
(77) cubic P(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3

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


class Bezier:
    """
    A `Bézier curve`_ is a parametric curve used in computer graphics and related fields. Bézier curves are used to
    model smooth curves that can be scaled indefinitely. "Paths", as they are commonly referred to in image
    manipulation programs, are combinations of linked Bézier curves. Paths are not bound by the limits of
    rasterized images and are intuitive to modify. (Source: Wikipedia)

    This is a general implementation which works with any count of definition points greater than ``2``, but it is a
    simple and slow implementation. For more performance look at the specialized :class:`Bezier4P` class.

    Args:
        defpoints: iterable of definition points as :class:`Vector` compatible objects.

    """

    def __init__(self, defpoints: Iterable['Vertex']):
        self._defpoints = [Vector(p) for p in defpoints]  # type: List[Vector]

    @property
    def control_points(self) -> List[Vector]:
        """ control points as list of :class:`Vector` objects. """
        return self._defpoints

    def approximate(self, segments: int = 20) -> Iterable[Vector]:
        """
        Approximate `Bézier curve`_ by vertices, yields `segments` + 1 vertices as :class:`Vector` objects.

        Args:
            segments: count of segments for approximation

        """
        step = 1.0 / float(segments)
        for point_index in range(segments + 1):
            yield self.point(point_index * step)

    def point(self, t: float) -> Vector:
        """
        Returns a point for location `t` at the `Bézier curve`_ as :class:`Vector` object.

        A `Bézier curve`_ is a parametric curve, parameter `t` goes from ``0`` to ``1``, where ``0`` is the first
        definition point anf ``1`` is the last definition point.

        Args:
            t: parameter in range ``[0, 1]``

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
    Subclass of :class:`Bezier`.

    Calculate vertices and derivative of a `Bézier curve`_.

    """

    def point(self, t: float) -> Tuple[Vector, Vector, Vector]:
        """
        Returns (point, 1st derivative, 2nd derivative) tuple for location `t` at the `Bézier curve`_,
        all values  as :class:`Vector` objects.

        Args:
            t: parameter in range ``[0, 1]``

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


def bernstein_basis(n: int, i: int, t: float) -> float:
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


class _Factorial:
    _values: Dict[int, float] = {0: 1.0}

    def __init__(self, maxvalue: int = 33):
        value = 1.
        for i in range(1, maxvalue):
            value *= i
            self._values[i] = value

    def get(self, value: int) -> float:
        value = int(value)
        try:
            return self._values[value]
        except KeyError:
            result = self.get(value - 1) * value
            self._values[value] = result
            return result


_factorial = _Factorial()
factorial = _factorial.get
