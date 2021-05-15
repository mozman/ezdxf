# cython: language_level=3
# distutils: language = c++
# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
# Cython implementation of the B-spline basis function.

from typing import List, Iterable, Sequence, Tuple
import cython
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from .vector cimport Vec3, isclose, v3_mul, v3_sub, v3_from_cpp_vec3
from ._cpp_vec3 cimport CppVec3

__all__ = ['Basis', 'Evaluator']

# factorial from 0 to 18
cdef double[19] FACTORIAL = [
    1., 1., 2., 6., 24., 120., 720., 5040., 40320., 362880., 3628800.,
    39916800., 479001600., 6227020800., 87178291200., 1307674368000.,
    20922789888000., 355687428096000., 6402373705728000.
]

NULL_LIST = [0.0]
ONE_LIST = [1.0]

cdef Vec3 NULLVEC = Vec3()
DEF ABS_TOL = 1e-12
DEF REL_TOL = 1e-9

# AutoCAD limits the degree to 11 or order = 12
DEF MAX_ORDER = 12

@cython.cdivision(True)
cdef double binomial_coefficient(int k, int i):
    cdef double k_fact = FACTORIAL[k]
    cdef double i_fact = FACTORIAL[i]
    cdef double k_i_fact
    if i > k:
        return 0.0
    k_i_fact = FACTORIAL[k - i]
    return k_fact / (k_i_fact * i_fact)

@cython.boundscheck(False)
cdef int bisect_right(double*a, double x, int lo, int hi):
    cdef int mid
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo

cdef reset_double_array(double *a, int count, double value=0.0):
    cdef int i
    for i in range(count):
        a[i] = value

cdef class Basis:
    """ Immutable Basis function class. """
    # public:
    cdef readonly int order
    cdef readonly int count
    cdef readonly double max_t
    cdef tuple weights_  # public attribute for Cython Evaluator
    # private:
    cdef double*_knots
    cdef int knot_count

    def __cinit__(self, knots: Iterable[float], int order, int count,
                  weights: Sequence[float] = None):
        if order < 2 or order >= MAX_ORDER:
            raise ValueError('invalid order')
        self.order = order
        if count < 2:
            raise ValueError('invalid count')
        self.count = count
        self.knot_count = self.order + self.count
        self.weights_ = tuple(float(x) for x in weights) if weights else tuple()

        cdef Py_ssize_t i = len(self.weights_)
        if i != 0 and i != self.count:
            raise ValueError('invalid weight count')

        knots = [float(x) for x in knots]
        if len(knots) != self.knot_count:
            raise ValueError('invalid knot count')

        self._knots = <double *> PyMem_Malloc(self.knot_count * sizeof(double))
        for i in range(self.knot_count):
            self._knots[i] = knots[i]
        self.max_t = self._knots[self.knot_count - 1]

    def __dealloc__(self):
        PyMem_Free(self._knots)

    @property
    def degree(self) -> int:
        return self.order - 1

    @property
    def knots(self) -> Tuple[float, ...]:
        return tuple(x for x in self._knots[:self.knot_count])

    @property
    def weights(self) -> Tuple[float, ...]:
        return self.weights_

    @property
    def is_rational(self) -> bool:
        """ Returns ``True`` if curve is a rational B-spline. (has weights) """
        return bool(self.weights_)

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
        cdef double*knots = self._knots
        cdef int count = self.count  # text book: n+1
        cdef int p = self.order - 1
        cdef int span
        if u >= knots[count]:  # special case
            return count - 1

        # common clamped spline:
        if knots[p] == 0.0:  # use binary search
            # This is fast and works most of the time,
            # but Test 621 : test_weired_closed_spline()
            # goes into an infinity loop, because of
            # a weird knot configuration.
            return bisect_right(knots, u, p, count) - 1
        else:  # use linear search
            span = 0
            while knots[span] <= u and span < count:
                span += 1
            return span - 1

    cpdef list basis_funcs(self, int span, double u):
        # Source: The NURBS Book: Algorithm A2.2
        cdef int order = self.order
        cdef double*knots = self._knots
        cdef double[MAX_ORDER] N, left, right
        cdef list result
        reset_double_array(N, order)
        reset_double_array(left, order)
        reset_double_array(right, order)

        cdef int j, r, i1
        cdef double temp, saved, temp_r, temp_l
        N[0] = 1.0
        for j in range(1, order):
            i1 = span + 1 - j
            if i1 < 0:
                i1 = 0
            left[j] = u - knots[i1]
            right[j] = knots[span + j] - u
            saved = 0.0
            for r in range(j):
                temp_r = right[r + 1]
                temp_l = left[j - r]
                temp = N[r] / (temp_r + temp_l)
                N[r] = saved + temp_r * temp
                saved = temp_l * temp
            N[j] = saved
        result = [x for x in N[:order]]
        if self.is_rational:
            return self.span_weighting(result, span)
        else:
            return result

    cpdef list span_weighting(self, nbasis: List[float], int span):
        cdef list products = [
            nb * w for nb, w in zip(
                nbasis,
                self.weights_[span - self.order + 1: span + 1]
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
        cdef double*knots = self._knots
        cdef double[MAX_ORDER] left, right
        reset_double_array(left, order, 1.0)
        reset_double_array(right, order, 1.0)

        cdef list ndu = [ONE_LIST * order for _ in range(order)]
        cdef int j, r, i1
        cdef double temp, saved, tmp_r, tmp_l
        for j in range(1, order):
            i1 = span + 1 - j
            if i1 < 0:
                i1 = 0
            left[j] = u - knots[i1]
            right[j] = knots[span + j] - u
            saved = 0.0
            for r in range(j):
                # lower triangle
                tmp_r = right[r + 1]
                tmp_l = left[j - r]
                ndu[j][r] = tmp_r + tmp_l
                temp = ndu[r][j - 1] / ndu[j][r]
                # upper triangle
                ndu[r][j] = saved + (tmp_r * temp)
                saved = tmp_l * temp
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

    cdef CppVec3 control_point(self, int index):
        cdef Vec3 v3 = <Vec3> self._control_points[index]
        return v3.to_cpp_vec3()

    cpdef Vec3 point(self, double u):
        # Source: The NURBS Book: Algorithm A3.1
        cdef Basis basis = self._basis
        cdef int p = basis.order - 1
        if isclose(u, basis.max_t, REL_TOL, ABS_TOL):
            u = basis.max_t

        cdef int span = basis.find_span(u)
        cdef list N = basis.basis_funcs(span, u)
        cdef int i
        cdef CppVec3 sum_ = CppVec3(), cpoint
        for i in range(p + 1):
            cpoint = self.control_point(span - p + i)
            sum_ = sum_ + (cpoint * <double> N[i])
        return v3_from_cpp_vec3(sum_)

    def points(self, t: Iterable[float]) -> Iterable[Vec3]:
        cdef double u
        for u in t:
            yield self.point(u)

    cpdef list derivative(self, double u, int n = 1):
        """ Return point and derivatives up to n <= degree for parameter u. """
        # Source: The NURBS Book: Algorithm A3.2
        cdef Vec3 vec3sum
        cdef CppVec3 cppsum
        cdef list CK = [], CKw = [], wders = []
        cdef tuple weights
        cdef Basis basis = self._basis
        if isclose(u, basis.max_t, REL_TOL, ABS_TOL):
            u = basis.max_t

        cdef int p = basis.degree
        cdef int span = basis.find_span(u)
        cdef list basis_funcs_ders = basis.basis_funcs_derivatives(span, u, n)
        cdef int k, j, i
        cdef double wder, bas_func_weight, bas_func
        if basis.is_rational:
            # Homogeneous point representation required:
            # (x*w, y*w, z*w, w)
            weights = basis.weights_
            for k in range(n + 1):
                cppsum = CppVec3()
                wder = 0.0
                for j in range(p + 1):
                    i = span - p + j
                    bas_func_weight = basis_funcs_ders[k][j] * weights[i]
                    # control_point * weight * bas_func_der = (x*w, y*w, z*w) * bas_func_der
                    cppsum = cppsum + (self.control_point(i) * bas_func_weight)
                    wder += bas_func_weight
                CKw.append(v3_from_cpp_vec3(cppsum))
                wders.append(wder)

            # Source: The NURBS Book: Algorithm A4.2
            for k in range(n + 1):
                vec3sum = CKw[k]
                for j in range(1, k + 1):
                    bas_func_weight = binomial_coefficient(k, j) * wders[j]
                    vec3sum = v3_sub(vec3sum,
                                     v3_mul(CK[k - j], bas_func_weight))
                CK.append(vec3sum / wders[0])
        else:
            for k in range(n + 1):
                cppsum = CppVec3()
                for j in range(p + 1):
                    bas_func = basis_funcs_ders[k][j]
                    cppsum = cppsum + (
                            self.control_point(span - p + j) * bas_func
                    )
                CK.append(v3_from_cpp_vec3(cppsum))
        return CK

    def derivatives(
            self, t: Iterable[float], int n = 1) -> Iterable[List[Vec3]]:
        cdef double u
        for u in t:
            yield self.derivative(u, n)
