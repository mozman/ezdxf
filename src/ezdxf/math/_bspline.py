#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#
# Pure Python implementation of the B-spline basis function.

from typing import List, Iterable, Sequence
import bisect
from array import array
from ezdxf.math import Vec3, NULLVEC, binomial_coefficient


class Basis:
    __slots__ = ['_knots', '_weights', 'order', 'count']

    def __init__(self, knots: Iterable[float], order: int, count: int,
                 weights: Sequence[float] = None):
        self._knots = array('d', knots)
        if weights is None:
            weights = []
        self._weights = array('d', weights)
        self.order: int = order
        self.count: int = count

    @property
    def max_t(self) -> float:
        return self._knots[-1]

    @property
    def knots(self) -> array:
        return self._knots

    @knots.setter
    def knots(self, values) -> None:
        self._knots = array('d', values)

    @property
    def weights(self) -> array:
        return self._weights

    @property
    def is_rational(self) -> bool:
        """ Returns ``True`` if curve is a rational B-spline. (has weights) """
        return bool(self._weights)

    def basis_vector(self, t: float) -> List[float]:
        """ Returns the expanded basis vector. """
        span = self.find_span(t)
        p = self.order - 1
        front = span - p
        back = self.count - span - 1
        basis = self.basis_funcs(span, t)
        return ([0.0] * front) + basis + ([0.0] * back)

    def find_span(self, u: float) -> int:
        """ Determine the knot span index. """
        # Linear search is more reliable than binary search of the Algorithm A2.1
        # from The NURBS Book by Piegl & Tiller.
        knots = self._knots
        count = self.count
        p = self.order - 1
        # if it is a standard clamped spline
        if knots[p] == 0.0:  # use binary search
            # This is fast and works most of the time,
            # but Test 621 : test_weired_closed_spline()
            # goes into an infinity loop, because of
            # a weird knot configuration.
            return bisect.bisect_right(knots, u, p, count) - 1
        else:  # use linear search
            for span in range(count):
                if knots[span] > u:
                    return span - 1
            return count - 1

    def basis_funcs(self, span: int, u: float) -> List[float]:
        # Source: The NURBS Book: Algorithm A2.2
        degree = self.order - 1
        knots = self._knots
        N = [0.0] * (degree + 1)
        left = list(N)
        right = list(N)
        N[0] = 1.0
        for j in range(1, degree + 1):
            left[j] = u - knots[span + 1 - j]
            right[j] = knots[span + j] - u
            saved = 0.0
            for r in range(j):
                temp = N[r] / (right[r + 1] + left[j - r])
                N[r] = saved + right[r + 1] * temp
                saved = left[j - r] * temp
            N[j] = saved
        if self.is_rational:
            return self.span_weighting(N, span)
        else:
            return N

    def span_weighting(self, nbasis: List[float], span: int) -> List[float]:
        weights = self._weights[span - self.order + 1: span + 1]
        products = [nb * w for nb, w in zip(nbasis, weights)]
        s = sum(products)
        return [0.0] * self.order if s == 0.0 else [p / s for p in products]

    def basis_funcs_derivatives(self, span: int, u: float, n: int = 1):
        # Source: The NURBS Book: Algorithm A2.3
        order = self.order
        p = order - 1
        n = min(n, p)

        knots = self._knots
        left = [1.0] * order
        right = [1.0] * order
        ndu = [[1.0] * order for _ in range(order)]

        for j in range(1, order):
            left[j] = u - knots[span + 1 - j]
            right[j] = knots[span + j] - u
            saved = 0.0
            for r in range(j):
                # lower triangle
                ndu[j][r] = right[r + 1] + left[j - r]
                temp = ndu[r][j - 1] / ndu[j][r]
                # upper triangle
                ndu[r][j] = saved + (right[r + 1] * temp)
                saved = left[j - r] * temp
            ndu[j][j] = saved

        # load the basis_vector functions
        derivatives = [[0.0] * order for _ in range(order)]
        for j in range(order):
            derivatives[0][j] = ndu[j][p]

        # loop over function index
        a = [[1.0] * order, [1.0] * order]
        for r in range(order):
            s1 = 0
            s2 = 1
            # alternate rows in array a
            a[0][0] = 1.0

            # loop to compute kth derivative
            for k in range(1, n + 1):
                d = 0.0
                rk = r - k
                pk = p - k
                if r >= k:
                    a[s2][0] = a[s1][0] / ndu[pk + 1][rk]
                    d = a[s2][0] * ndu[rk][pk]
                if rk >= -1:
                    j1 = 1
                else:
                    j1 = -rk
                if (r - 1) <= pk:
                    j2 = k - 1
                else:
                    j2 = p - r
                for j in range(j1, j2 + 1):
                    a[s2][j] = (a[s1][j] - a[s1][j - 1]) / ndu[pk + 1][rk + j]
                    d += (a[s2][j] * ndu[rk + j][pk])
                if r <= pk:
                    a[s2][k] = -a[s1][k - 1] / ndu[pk + 1][r]
                    d += (a[s2][k] * ndu[r][pk])
                derivatives[k][r] = d

                # Switch rows
                s1, s2 = s2, s1

        # Multiply through by the the correct factors
        r = float(p)
        for k in range(1, n + 1):
            for j in range(order):
                derivatives[k][j] *= r
            r *= (p - k)
        return derivatives[:n + 1]

    def curve_point(self, u: float, control_points: Sequence[Vec3]) -> Vec3:
        # Source: The NURBS Book: Algorithm A3.1
        p = self.order - 1
        span = self.find_span(u)
        N = self.basis_funcs(span, u)
        return Vec3.sum(
            N[i] * control_points[span - p + i] for i in range(p + 1))

    def curve_derivatives(self, u: float, control_points: Sequence[Vec3],
                          n: int = 1) -> List[Vec3]:
        # Source: The NURBS Book: Algorithm A3.2
        p = self.order - 1
        span = self.find_span(u)
        basis_funcs_derivatives = self.basis_funcs_derivatives(span, u, n)
        if self.is_rational:
            # Homogeneous point representation required:
            # (x*w, y*w, z*w, w)
            CKw = []
            wders = []
            for k in range(n + 1):
                v = NULLVEC
                wder = 0.0
                for j in range(p + 1):
                    index = span - p + j
                    bas_func_weight = basis_funcs_derivatives[k][j] * \
                                      self._weights[index]
                    # control_point * weight * bas_func_der = (x*w, y*w, z*w) * bas_func_der
                    v += control_points[index] * bas_func_weight
                    wder += bas_func_weight
                CKw.append(v)
                wders.append(wder)

            # Source: The NURBS Book: Algorithm A4.2
            CK = []
            for k in range(n + 1):
                v = CKw[k]
                for i in range(1, k + 1):
                    v -= binomial_coefficient(k, i) * wders[i] * CK[k - i]
                CK.append(v / wders[0])
        else:
            CK = [
                Vec3.sum(
                    basis_funcs_derivatives[k][j] * control_points[span - p + j]
                    for j in range(p + 1))
                for k in range(n + 1)
            ]
        return CK
