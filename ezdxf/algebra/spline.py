# Created: 2012.01.03
# Copyright (c) 2012 Manfred Moitzi
# License: MIT License
from .vector import Vector
__all__ = ['BSpline', 'BSplineU', 'DBSpline', 'DBSplineU', 'RBSpline', 'RBSplineU']


def one_based_array(values, decor=lambda x: x):
    newlist = [0.0]
    newlist.extend(decor(value) for value in values)
    return newlist


def knot(n, order):
    nplusc = n + order
    nplus2 = n + 2
    x = [0.0, 0.0]
    for i in range(2, nplusc+1):
        if (i > order) and (i < nplus2):
            x.append(x[i-1] + 1.0)
        else:
            x.append(x[i-1])
    return x


def knotu(n, order):
    nplusc = n + order
    x = [0.0, 0.0]
    x.extend(float(i) for i in range(1, nplusc))
    return x


def dist3d(p1, p2):
    return sum((v2-v1) ** 2 for v1, v2 in zip(p1, p2)) ** .5


def knotc(defpoints, order):
    # defpoints is a 1 based array
    n = len(defpoints) - 1
    dist = list(dist3d(defpoints[i-1], defpoints[i]) for i in range(2, n+1))

    maxc = sum(dist)
    x = [0.0] * (order + 1)
    for i in range(1, n - order + 2):
        csum = sum(dist[:i])
        numerator = float(i) / float(n - order + 2) * dist[i] + csum
        x.append(numerator / maxc * float(n - order + 2))
    x.extend([n - order + 2] * (order - 1))
    return x


class BSpline(object):
    """
    Calculate the points of a B-Spline curve, using an uniform open knot vector.

    Initialisation with 2D points is possible, but output ist always 3D (z-axis is 0)

    """
    def __init__(self, defpoints, order=3):
        self._defpoints = one_based_array(defpoints, Vector)
        self.npts = len(defpoints)
        self.order = order
        self.nplusc = self.npts + self.order
        self.knots = self.get_knots()

    @property
    def breakpoints(self):
        return self._defpoints[1:]

    @property
    def count(self):
        return self.npts

    def get_knots(self):
        return knot(self.npts, self.order)

    def get_max_t(self):
        return self.knots[self.nplusc]

    def get_step(self, segments):
        return self.get_max_t() / float(segments)

    def approximate(self, segments=20):
        step = self.get_step(segments)
        for point_index in range(segments+1):
            yield self.get_point(point_index * step)

    def get_point(self, t):
        """ Get point at SplineCurve(t) as tuple (x, y, z)

        :param float t: parameter in range [0, max_t]
        """

        max_t = self.get_max_t()
        if (max_t - t) < 5e-6:
            t = max_t

        nbasis = self.basis(t)
        defpoints = self._defpoints
        npts1 = self.npts + 1

        def get_axis_value(axis):
            return sum(nbasis[i] * defpoints[i][axis] for i in range(1, npts1))

        return tuple(get_axis_value(axis) for axis in (0, 1, 2))

    def create_nbasis(self, t):
        x = self.knots
        nbasis = [0.0]  # [0] is a dummy value, 1-based array
        # calculate the first order basis functions n[i][1]
        nbasis.extend(1.0 if x[i] <= t < x[i+1] else 0.0 for i in range(1, self.nplusc))
        return nbasis

    def basis(self, t):
        x = self.knots
        nbasis = self.create_nbasis(t)
        # calculate the higher order basis functions
        for k in range(2, self.order+1):
            for i in range(1, self.nplusc-k+1):
                d = ((t - x[i]) * nbasis[i]) / (x[i+k-1] - x[i]) if nbasis[i] != 0.0 else 0.0
                e = ((x[i+k] - t) * nbasis[i+1]) / (x[i+k] - x[i+1]) if nbasis[i+1] != 0.0 else 0.0
                nbasis[i] = d + e
        if t == x[self.nplusc]:  # pick up last point
            nbasis[self.npts] = 1.0
        return nbasis


class BSplineU(BSpline):
    """
    Calculate the points of a B-Spline curve, uniform (periodic) knot vector.

    """
    def get_knots(self):
        return knotu(self.npts, self.order)

    def get_step(self, segments):
        return float(self.npts - self.order + 1) / segments

    def get_max_t(self):
        return float(self.npts)

    def approximate(self, segments=20):
        step = self.get_step(segments)
        base = float(self.order - 1)
        for point_index in range(segments + 1):
            yield self.get_point(base + point_index * step)


class DBSplineMixin(object):
    # Mixin for DBSpline and DBSplineU
    def get_point(self, t):
        """
        Get point, 1st and 2nd derivative at B-Spline(t) as tuple (p, d1, d3),
        where p, d1 nad d2 is a tuple (x, y, z).

        Args:
            t: parameter in range [0, max_t]
        """
        max_t = self.get_max_t()
        if (max_t - t) < 5e-6:
            t = max_t

        nbasis, d1nbasis, d2nbasis = self.dbasis(t)
        point = [0.0, 0.0, 0.0]
        d1 = [0.0, 0.0, 0.0]
        d2 = [0.0, 0.0, 0.0]
        for axis in (0, 1, 2):
            for i in range(1, self.npts + 1):
                defpoint_value = self._defpoints[i][axis]
                point[axis] += nbasis[i] * defpoint_value
                d1[axis] += d1nbasis[i] * defpoint_value
                d2[axis] += d2nbasis[i] * defpoint_value
        return tuple(point), tuple(d1), tuple(d2)

    def dbasis(self, t):
        x = self.knots
        nbasis = self.create_nbasis2(t)
        d1nbasis = [0.0] * (self.nplusc + 1)  # [0] is a dummy value, 1-based array
        d2nbasis = d1nbasis[:]

        for k in range(2, self.order + 1):
            for i in range(1, self.nplusc - k + 1):
                # calculate basis functions
                b1 = ((t - x[i]) * nbasis[i]) / (x[i + k - 1] - x[i]) if nbasis[i] != 0.0 else 0.0
                b2 = ((x[i + k] - t) * nbasis[i + 1]) / (x[i + k] - x[i + 1]) if nbasis[i + 1] != 0.0 else 0.0

                # calculate first derivative
                f1 = nbasis[i] / (x[i + k - 1] - x[i]) if nbasis[i] != 0.0 else 0.0
                f2 = -nbasis[i + 1] / (x[i + k] - x[i + 1]) if nbasis[i + 1] != 0.0 else 0.0
                f3 = ((t - x[i]) * d1nbasis[i]) / (x[i + k - 1] - x[i]) if d1nbasis[i] != 0.0 else 0.0
                f4 = ((x[i + k] - t) * d1nbasis[i + 1]) / (x[i + k] - x[i + 1]) if d1nbasis[i + 1] != 0.0 else 0.0

                # calculate second derivative
                s1 = (2 * d1nbasis[i]) / (x[i + k - 1] - x[i]) if d1nbasis[i] != 0.0 else 0.0
                s2 = (-2 * d1nbasis[i + 1]) / (x[i + k] - x[i + 1]) if d1nbasis[i + 1] != 0.0 else 0.0
                s3 = ((t - x[i]) * d2nbasis[i]) / (x[i + k - 1] - x[i]) if d2nbasis[i] != 0.0 else 0.0
                s4 = ((x[i + k] - t) * d2nbasis[i + 1]) / (x[i + k] - x[i + 1]) if d2nbasis[i + 1] != 0.0 else 0.0

                nbasis[i] = b1 + b2
                d1nbasis[i] = f1 + f2 + f3 + f4
                d2nbasis[i] = s1 + s2 + s3 + s4

        return nbasis, d1nbasis, d2nbasis


class DBSpline(DBSplineMixin, BSpline):
    """
    Calculate the Points and Derivative of a B-Spline curve.

    """
    def create_nbasis2(self, t):
        nbasis = self.create_nbasis(t)
        if t == self.knots[self.nplusc]:
            nbasis[self.npts] = 1.0
        return nbasis


class DBSplineU(DBSplineMixin, BSplineU):
    """
    Calculate the Points and Derivative of a B-SplineU curve.

    """
    def create_nbasis2(self, t):
        npts = self.npts
        nbasis = self.create_nbasis(t)
        if t == self.knots[npts + 1]:
            nbasis[npts] = 1.0
            nbasis[npts + 1] = 0.0
        return nbasis


def weighting(nbasis, weights, npts):
    s = sum(nbasis[i] * weights[i] for i in range(1, npts + 1))
    if s == 0.0:
        r = [0.0] * (npts + 1)
    else:
        r = one_based_array(nbasis[i] * weights[i] / s for i in range(1, npts + 1))
    return r


class RBSpline(BSpline):
    """
    Calculate the points of a rational B-Spline curve, using an uniform open knot vector.

    """
    def __init__(self, defpoints, weights, order=3):
        if len(defpoints) != len(weights):
            raise ValueError("Item count of 'defpoints and 'weights' is different.")
        super(RBSpline, self).__init__(defpoints, order)
        self.weights = one_based_array(weights, float)

    def basis(self, t):
        nbasis = super(RBSpline, self).basis(t)
        return weighting(nbasis, self.weights, self.npts)


class RBSplineU(BSplineU):
    """
    Calculate the points of a rational B-Spline curve, using an uniform open knot vector.

    """
    def __init__(self, defpoints, weights, order=3):
        super(RBSplineU, self).__init__(defpoints, order)
        self.weights = one_based_array(weights, float)

    def basis(self, t):
        nbasis = super(RBSplineU, self).basis(t)
        return weighting(nbasis, self.weights, self.npts)
