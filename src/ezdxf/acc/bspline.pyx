# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
# Cython implementation of the B-spline basis function.

from typing import List, Iterable, Sequence
import cython
from .vector cimport Vec3, isclose, v3_add, v3_mul

__all__ = ['Basis', 'Evaluator']

# factorial from 0 to 18
FACTORIAL = [
    1., 1., 2., 6., 24., 120., 720., 5040., 40320., 362880., 3628800.,
    39916800., 479001600., 6227020800., 87178291200., 1307674368000.,
    20922789888000., 355687428096000., 6402373705728000.
]

NULL_LIST = [0.0]
ONE_LIST = [1.0]

cdef Vec3 NULLVEC = Vec3()
DEF ABS_TOL = 1e-12

cdef double binomial_coefficient(int k, int i):
    cdef double k_fact = FACTORIAL[k]
    cdef double i_fact = FACTORIAL[i]
    cdef double k_i_fact
    if i > k:
        return 0.0
    k_i_fact = FACTORIAL[k - i]
    return k_fact / (k_i_fact * i_fact)

@cython.boundscheck(False)
cdef int bisect_right(a, double x, int lo, int hi):
    cdef int mid
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo

cdef class Basis:
    """ Immutable Basis function class. """
    cdef readonly int order
    cdef readonly int count
    cdef readonly double max_t
    cdef list _knots
    cdef list _weights

    def __cinit__(self, knots: Iterable[float], int order, int count,
                  weights: Sequence[float] = None):
        self.order = order
        self.count = count
        self._knots = list(knots)
        self._weights = list(weights) if weights else []
        self.max_t = self._knots[-1]

        # validation checks:
        cdef int len_weights = len(self._weights)
        if len_weights != 0 and len_weights != self.count:
            raise ValueError('invalid weight count')
        if len(self._knots) != self.order + self.count:
            raise ValueError('invalid knot count')

    @property
    def degree(self) -> int:
        return self.order - 1

    @property
    def knots(self) -> List[float]:
        return list(self._knots)  # do not return mutable array!

    @property
    def weights(self) -> List[float]:
        return list(self._weights)  # do not return mutable array!

    @property
    def is_rational(self) -> bool:
        """ Returns ``True`` if curve is a rational B-spline. (has weights) """
        return bool(self._weights)

    cpdef list basis_vector(self, double t):
        """ Returns the expanded basis vector. """

        cdef int span = self.find_span(t)
        cdef int p = self.order - 1
        cdef int front = span - p
        cdef int back = self.count - span - 1
        cdef list result
        if front > 0:
            result = NULL_LIST * front
            result.extend(self.basis_funcs(span, t))
        else:
            result = self.basis_funcs(span, t)
        if back > 0:
            result.extend(NULL_LIST * back)
        return result

    cpdef int find_span(self, double u):
        """ Determine the knot span index. """
        # Linear search is more reliable than binary search of the Algorithm A2.1
        # from The NURBS Book by Piegl & Tiller.
        cdef list knots = self._knots
        cdef int count = self.count
        cdef int p = self.order - 1
        cdef int span
        # if it is a standard clamped spline
        if knots[p] == 0.0:  # use binary search
            # This is fast and works most of the time,
            # but Test 621 : test_weired_closed_spline()
            # goes into an infinity loop, because of
            # a weird knot configuration.
            return bisect_right(knots, u, p, count) - 1
        else:  # use linear search
            for span in range(count):
                if knots[span] > u:
                    return span - 1
            return count - 1


    @cython.boundscheck(False)
    cpdef list basis_funcs(self, int span, double u):
        # Source: The NURBS Book: Algorithm A2.2
        cdef int order = self.order
        cdef list knots = self._knots
        cdef list N = NULL_LIST * order
        cdef left = list.copy(N)
        cdef right = list.copy(N)

        # Using memory views is slower!
        cdef int j, r
        cdef double temp, saved, temp_r, temp_l
        N[0] = 1.0
        for j in range(1, order):
            left[j] = u - knots[span + 1 - j]
            right[j] = knots[span + j] - u
            saved = 0.0
            for r in range(j):
                temp_r = right[r + 1]
                temp_l = left[j - r]
                temp = N[r] / (temp_r + temp_l)
                N[r] = saved + temp_r * temp
                saved = temp_l * temp
            N[j] = saved
        if self.is_rational:
            return self.span_weighting(N, span)
        else:
            return N

    cpdef list span_weighting(self, nbasis: List[float], int span):
        cdef list products = [
            nb * w for nb, w in zip(
                nbasis,
                self._weights[span - self.order + 1: span + 1]
            )
        ]
        s = sum(products)
        if s != 0:
            return [p / s for p in products]
        else:
            return NULL_LIST * len(nbasis)

    cpdef list basis_funcs_derivatives(self, int span, double u, int n = 1):
        # Source: The NURBS Book: Algorithm A2.3
        cdef int order = self.order
        cdef int p = order - 1
        if n > p:
            n = p

        cdef list knots = self._knots
        cdef list left = ONE_LIST * order
        cdef list right = ONE_LIST * order
        cdef list ndu = [ONE_LIST * order for _ in range(order)]
        cdef int j, r
        cdef double temp, saved
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
        cdef list derivatives = [NULL_LIST * order for _ in range(order)]
        for j in range(order):
            derivatives[0][j] = ndu[j][p]

        # loop over function index
        cdef list a = [ONE_LIST * order, ONE_LIST * order]
        cdef int s1, s2, k, rk, pk, j1, j2, t
        cdef double d
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
                t = s1
                s1 = s2
                s2 = t

        # Multiply through by the the correct factors
        cdef double rr = p
        for k in range(1, n + 1):
            for j in range(order):
                derivatives[k][j] *= rr
            rr *= (p - k)
        return derivatives[:n + 1]

cdef class Evaluator:
    """ B-spline curve point and curve derivative evaluator. """
    cdef Basis _basis
    cdef tuple _control_points

    def __cinit__(self, basis: Basis, control_points: Sequence[Vec3]):
        self._basis = basis
        self._control_points = Vec3.tuple(control_points)

    cpdef Vec3 point(self, double u):
        # Source: The NURBS Book: Algorithm A3.1
        cdef Basis basis = self._basis
        cdef tuple control_points = self._control_points
        cdef int p = basis.order - 1
        if isclose(u, basis.max_t, ABS_TOL):
            u = basis.max_t

        cdef Vec3 sum = NULLVEC
        cdef int span = basis.find_span(u)
        cdef Vec3 cpoint
        cdef list N = basis.basis_funcs(span, u)
        cdef double func
        cdef int i
        for i in range(p + 1):
            cpoint = <Vec3> control_points[span - p + i]
            func = N[i]
            sum = v3_add(sum, v3_mul(cpoint, func))
        return sum

    def points(self, t: Iterable[float]) -> Iterable[Vec3]:
        for u in t:
            yield self.point(u)

    cpdef list derivative(self, double u, int n = 1):
        """ Return point and derivatives up to n <= degree for parameter u. """
        # Source: The NURBS Book: Algorithm A3.2
        cdef Vec3 s, v
        cdef list CK, CKw, wders, weights
        cdef Basis basis = self._basis
        cdef tuple control_points = self._control_points

        if isclose(u, basis.max_t, ABS_TOL):
            u = basis.max_t

        cdef int p = basis.degree
        cdef int span = basis.find_span(u)
        cdef list basis_funcs_ders = basis.basis_funcs_derivatives(span, u, n)
        cdef int k, j, i, index
        cdef double wder, bas_func_weight
        if basis.is_rational:
            # Homogeneous point representation required:
            # (x*w, y*w, z*w, w)
            CKw = []
            wders = []
            weights = basis._weights
            for k in range(n + 1):
                v = NULLVEC
                wder = 0.0
                for j in range(p + 1):
                    index = span - p + j
                    bas_func_weight = basis_funcs_ders[k][j] * weights[index]
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
            CK = []
            s = NULLVEC
            for k in range(n + 1):
                s = NULLVEC
                for j in range(p + 1):
                    s = v3_add(s, basis_funcs_ders[k][j] * control_points[span - p + j])
                CK.append(s)
        return CK

    def derivatives(
            self, t: Iterable[float], int n = 1) -> Iterable[List[Vec3]]:
        cdef double u
        for u in t:
            yield self.derivative(u, n)
