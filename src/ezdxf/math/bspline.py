# Created: 2012.01.03
# Copyright (c) 2012-2018 Manfred Moitzi
# License: MIT License
"""
B-Splines
=========

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node4.html

Rational B-splines
==================

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node5.html:


"""
from typing import List, Iterable, Sequence, TYPE_CHECKING, Dict, Tuple, Optional, Union
import math
from .vector import Vector
from .parametrize import create_t_vector
from .linalg import (
    LUDecomposition, Matrix, BandedMatrixLU, compact_banded_matrix, detect_banded_matrix,
    quadratic_equation
)
from ezdxf.lldxf.const import DXFValueError
from ezdxf import PYPY

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
    from ezdxf.math import ConstructionArc, ConstructionEllipse, Matrix44

# Acceleration of banded diagonal matrix solver kicks in at:
# N=15 for CPython on Windows and Linux
# N=60 for pypy3 on Windows and Linux
USE_BANDED_MATRIX_SOLVER_CPYTHON_LIMIT = 15
USE_BANDED_MATRIX_SOLVER_PYPY_LIMIT = 60


def open_uniform_knot_vector(n: int, order: int, normalize=False) -> List[float]:
    """
    Returns an open (clamped) uniform knot vector for a B-spline of `order` and `n` control points.

    `order` = degree + 1

    Args:
        n: count of control points
        order: spline order
        normalize: normalize values in range [0, 1] if ``True``

    """
    count = n - order
    if normalize:
        max_value = float(n - order + 1)
        tail = [1.0] * order
    else:
        max_value = 1.0
        tail = [1.0 + count] * order

    knots = [0.0] * order
    knots.extend((1.0 + v) / max_value for v in range(count))
    knots.extend(tail)
    return knots


def uniform_knot_vector(n: int, order: int, normalize=False) -> List[float]:
    """
    Returns an uniform knot vector for a B-spline of `order` and `n` control points.

    `order` = degree + 1

    Args:
        n: count of control points
        order: spline order
        normalize: normalize values in range [0, 1] if ``True``

    """
    if normalize:
        max_value = float(n + order - 1)
    else:
        max_value = 1.0
    return [knot_value / max_value for knot_value in range(n + order)]


def required_knot_values(count: int, order: int) -> int:
    """
    Returns the count of required knot values for a B-spline of `order` and `count` control points.

    degree =  degree of B-spline, in math papers often called: `p`

    Args:
        count: count of control points, in math papers often called:  `n` + 1
        order: order of B-Spline, in math papers often called:  `k`

    Relationships:

    - `k` (order) = `p` (degree) + 1
    - 2 ≤ `k` (order) ≤ `n` + 1 (count)

    """
    k = order
    n = count - 1
    p = k - 1
    if not (2 <= k <= (n + 1)):
        raise DXFValueError('Invalid count/order combination')
    # n + p + 2 = count + order
    return n + p + 2


def global_bspline_interpolation(
        fit_points: Iterable['Vertex'], degree: int = 3,
        tangents: Tuple['Vertex', 'Vertex'] = None,
        method: str = 'chord') -> 'BSpline':
    """
    `B-spline`_ interpolation  by `Curve Global Interpolation`_.
    Given are the fit points and the degree of the B-spline.
    The function provides 3 methods for generating the parameter vector t:

    - "uniform": creates a uniform t vector, from 0 to 1 evenly spaced, see `uniform`_ method
    - "chord", "distance": creates a t vector with values proportional to the fit point distances,
      see `chord length`_ method
    - "centripetal", "sqrt_chord": creates a t vector with values proportional to the fit point sqrt(distances),
      see `centripetal`_ method

    Args:
        fit_points: fit points of B-spline, as list of :class:`Vector` compatible objects
        tangents: define start- and end tangent as 2-tuple of :class:`Vector` compatible objects (optional)
        degree: degree of B-spline
        method: calculation method for parameter vector t

    Returns:
        :class:`BSpline`

    """

    fit_points = Vector.list(fit_points)
    count = len(fit_points)
    order = degree + 1
    if order > count:
        raise DXFValueError('More fit points required for degree {}'.format(degree))

    t_vector = list(create_t_vector(fit_points, method))
    if bool(tangents):
        control_points, knots = _global_bspline_interpolation_end_tangents(
            fit_points, Vector(tangents[0]), Vector(tangents[1]), degree, t_vector)
    else:
        control_points, knots = _global_bspline_interpolation(fit_points, degree, t_vector)

    bspline = BSpline(control_points, order=order, knots=knots)
    bspline.t_array = t_vector
    return bspline


def bspline_control_frame_approx(
        fit_points: Iterable['Vertex'],
        count: int,
        degree: int = 3,
        method: str = 'chord') -> 'BSpline':
    """
    Approximate `B-spline`_ by a reduced count of control points, given are the fit points and the degree of
    the B-spline.

    Args:
        fit_points: all fit points of B-spline as :class:`Vector` compatible objects
        count: count of designated control points
        degree: degree of B-spline
        method: calculation method for parameter vector t, see :func:`global_bspline_interpolation`

    Returns:
        :class:`BSpline`

    """

    fit_points = Vector.list(fit_points)
    order = degree + 1
    if order > count:
        raise DXFValueError('More control points for degree {} required.'.format(degree))

    t_vector = list(create_t_vector(fit_points, method))
    knots = list(control_frame_knots(len(fit_points) - 1, degree, t_vector))
    control_points = global_bspline_approximation(fit_points, count, degree, t_vector, knots)
    bspline = BSpline(control_points, order=order)
    return bspline


def control_frame_knots(n: int, p: int, t_vector: Iterable[float]) -> Iterable[float]:
    """
    Generates a 'clamped' knot vector for control frame creation. All knot values in the range [0 .. 1].

    Args:
        n: count fit points - 1
        p: degree of spline
        t_vector: parameter vector, length(t_vector) == n+1

    Returns:
        Iterable[float]: n+p+2 knot values

    """
    order = int(p + 1)
    if order > (n + 1):
        raise DXFValueError('Invalid n/p combination')

    t_vector = [float(t) for t in t_vector]
    for _ in range(order):  # clamped spline has 'order' leading 0s
        yield t_vector[0]
    for j in range(1, n - p + 1):
        yield sum(t_vector[j: j + p]) / p
    for _ in range(order):  # clamped spline has 'order' appended 1s
        yield t_vector[-1]


def _get_best_solver(matrix: Union[List, Matrix], degree: int):
    """ Returns best suited linear equation solver depending on matrix
    configuration and python interpreter.
    """
    A = matrix if isinstance(matrix, Matrix) else Matrix(matrix=matrix)
    if PYPY:
        limit = USE_BANDED_MATRIX_SOLVER_PYPY_LIMIT
    else:
        limit = USE_BANDED_MATRIX_SOLVER_CPYTHON_LIMIT
    if A.nrows < limit:  # use default equation solver
        lu = LUDecomposition(A)
    else:
        # Theory: band parameters m1, m2 are at maximum degree-1, for
        # B-spline interpolation and approximation:
        # m1 = m2 = degree-1
        # But the speed gain is not that big and just to be sure:
        m1, m2 = detect_banded_matrix(A, check_all=False)
        A = compact_banded_matrix(A, m1, m2)
        lu = BandedMatrixLU(A, m1, m2)
    return lu


def _global_bspline_interpolation(
        fit_points: Sequence['Vertex'],
        degree: int,
        t_vector: Sequence[float]) -> Tuple[List[Vector], List[float]]:
    """ Algorithm: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html """

    knots = list(control_frame_knots(len(fit_points) - 1, degree, t_vector))
    spline = Basis(knots=knots, order=degree + 1, count=len(fit_points))
    solver = _get_best_solver([spline.basis(t) for t in t_vector], degree)
    control_points = solver.solve_matrix(fit_points)
    return Vector.list(control_points.rows()), knots


def _global_bspline_interpolation_end_tangents(
        fit_points: List[Vector],
        start_tangent: Vector,
        end_tangent: Vector,
        degree: int,
        t_vector: Sequence[float]) -> Tuple[List[Vector], List[float]]:
    # DOES NOT WORK!
    n = len(fit_points) - 1
    p = degree
    m = n + p + 3

    knots = [0.0] * (p + 1)
    knots.extend(sum(t_vector[j: j + p - 1]) / p for j in range(n - p + 2))
    knots.extend([1.0] * (p + 1))
    assert len(knots) == m + 1

    spline = Basis(knots=knots, order=p + 1, count=n + 3)
    rows = [spline.basis(u) for u in t_vector]
    space = [0.0] * (n + 1)
    rows.insert(1, [-1.0, +1.0] + space)
    rows.insert(-1, space + [-1.0, +1.0])
    solver = _get_best_solver(rows, degree)

    fit_points.insert(1, start_tangent * (knots[p + 1] / p))
    fit_points.insert(-1, end_tangent * ((1.0 - knots[m - p - 1]) / p))
    control_points = solver.solve_matrix(fit_points)
    return Vector.list(control_points.rows()), knots


def global_bspline_approximation(
        fit_points: Iterable['Vertex'],
        count: int,
        degree: int,
        t_vector: Iterable[float],
        knots: Iterable[float]) -> List[Vector]:
    """
    Approximate `B-spline`_ by a reduced count of control points, given are the fit points and the degree of the B-spline.

    Args:
        fit_points: all B-spline fit points as :class:`Vector` compatible objects
        count: count of designated control points
        degree: degree of B-spline
        t_vector: parameter vector
        knots: knot vector

    Returns:
        List[Vector]: control points

    """
    # source: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-APP-global.html
    fit_points = Vector.list(fit_points)  # data points D
    n = len(fit_points) - 1
    h = count - 1
    d0 = fit_points[0]
    dn = fit_points[n]
    spline = Basis(knots, order=degree + 1, count=len(fit_points))
    # matrix_N[0] == row 0
    N = [spline.basis(t) for t in t_vector]  # 0 .. n

    def get_Q(k):
        ntk = N[k]
        return fit_points[k] - d0 * ntk[0] - dn * ntk[h]

    # Q[0] == row 1
    Q = [sum(get_Q(k) * N[k][i] for k in range(1, n)) for i in range(1, h)]
    N = Matrix([row[1:h] for row in N[1:-1]])
    M = N.transpose() * N
    solver = _get_best_solver(M, degree)
    P = solver.solve_matrix(Q)
    control_points = [d0]
    control_points.extend(Vector.generate(P.rows()))
    control_points.append(dn)
    return control_points


def local_cubic_bspline_interpolation(
        fit_points: Iterable['Vertex'],
        method: str = '5-points',
        tangents: Iterable['Vertex'] = None) -> 'BSpline':
    """
    `B-spline`_ interpolation by 'Local Cubic Curve Interpolation', which creates
    B-spline from fit points and estimated tangent direction at start-, end- and
    passing points.

    Algorithm: "The NURBS Book" chapter 9.3.4 Local Cubic Curve Interpolation

    Available tangent estimation methods:


        - "3-points": 3 point interpolation
        - "5-points": 5 point interpolation
        - "cubic-bezier": interpolate a cubic bezier curve
        - "diff": finite difference

    or pass pre-calculated tangents, which overrides tangent estimation.

    Args:
        fit_points: all B-spline fit points as :class:`Vector` compatible objects
        method: tangent estimation method
        tangents: tangents as :class:`Vector` compatible objects (optional)

    Returns:
        :class:`BSpline`

    """
    from .parametrize import estimate_tangents
    fit_points = Vector.list(fit_points)
    if tangents:
        tangents = Vector.list(tangents)
    else:
        tangents = estimate_tangents(fit_points, method)
    control_points, knots = local_cubic_bspline_interpolation_from_tangents(fit_points, tangents)
    return BSpline(control_points, order=4, knots=knots)


def local_cubic_bspline_interpolation_from_tangents(fit_points: List[Vector], tangents: List[Vector]) -> Tuple[
    List[Vector], List[float]]:
    """ The NURBS Book: Chapter 9.3.4 Local Cubic Curve Interpolation

    Args:
        fit_points: curve definition points - curve has to pass all given fit points
        tangents: one tangent vector for each fit point as unit vectors

    Returns:
        list of control points and list of knots

    """
    assert len(fit_points) == len(tangents)
    assert len(fit_points) > 2

    degree = 3
    order = degree + 1
    control_points = [fit_points[0]]
    u = 0.0
    params = []
    for i in range(len(fit_points) - 1):
        p0 = fit_points[i]
        p3 = fit_points[i + 1]
        t0 = tangents[i]
        t3 = tangents[i + 1]
        a = 16.0 - (t0 + t3).magnitude_square
        b = 12.0 * (p3 - p0).dot(t0 + t3)
        c = -36.0 * (p3 - p0).magnitude_square
        alpha_plus, alpha_minus = quadratic_equation(a, b, c)
        p1 = p0 + alpha_plus * t0 / 3.0
        p2 = p3 - alpha_plus * t3 / 3.0
        control_points.extend((p1, p2))
        u += 3.0 * (p1 - p0).magnitude
        params.append(u)
    control_points.append(fit_points[-1])

    knots = [0.0] * order
    max_u = params[-1]
    for v in params[:-1]:
        knot = v / max_u
        knots.extend((knot, knot))
    knots.extend([1.0] * 4)

    assert len(knots) == required_knot_values(len(control_points), order)
    return control_points, knots


class Basis:
    def __init__(self, knots: Iterable[float], order: int, count: int, weights: Sequence[float] = None):
        self.knots: List[float] = list(knots)
        self.order: int = order
        self.count: int = count
        self.weights: Optional[Sequence[float]] = weights

    @property
    def max_t(self) -> float:
        return self.knots[-1]

    @property
    def nplusc(self) -> int:
        return self.count + self.order

    def create_nbasis(self, t: float) -> List[float]:
        """
        Calculate the first order basis functions N[i][1]

        Returns: list of basis values

        """
        return [1. if k1 <= t < k2 else 0. for k1, k2 in zip(self.knots, self.knots[1:])]

    def basis(self, t: float) -> List[float]:
        knots = self.knots
        nbasis = self.create_nbasis(t)
        # calculate the higher order basis functions
        for k in range(2, self.order + 1):
            for i in range(self.nplusc - k):
                i1 = i + 1
                ik = i + k
                d = ((t - knots[i]) * nbasis[i]) / (knots[ik - 1] - knots[i]) if nbasis[i] else 0.
                e = ((knots[ik] - t) * nbasis[i1]) / (knots[ik] - knots[i1]) if nbasis[i1] else 0.
                nbasis[i] = d + e
        if math.isclose(t, self.max_t):  # pick up last point
            nbasis[self.count - 1] = 1.
        if self.weights is None:
            return nbasis[:self.count]
        else:
            return self.weighting(nbasis[:self.count])

    def weighting(self, nbasis: Iterable[float]) -> List[float]:
        products = [nb * w for nb, w in zip(nbasis, self.weights)]
        s = sum(products)
        return [0.0] * self.count if s == 0.0 else [p / s for p in products]


class DBasis(Basis):
    def basis(self, t: float) -> Tuple[List[float], List[float], List[float]]:
        knots = self.knots
        nbasis = self.create_nbasis2(t)
        d1nbasis = [0.] * self.nplusc
        d2nbasis = d1nbasis[:]

        for k in range(2, self.order + 1):
            for i in range(self.nplusc - k):
                i1 = i + 1
                ik = i + k

                knot_ik_1__knot_i = knots[ik - 1] - knots[i]
                knot_ik__knot_i1 = knots[ik] - knots[i1]
                t__knot_i = t - knots[i]
                knot_ik__t = knots[ik] - t

                nbasis_i = nbasis[i]

                if nbasis_i:
                    b1 = t__knot_i * nbasis_i / knot_ik_1__knot_i
                    f1 = nbasis_i / knot_ik_1__knot_i
                else:
                    b1 = 0.0
                    f1 = 0.0

                nbasis_i1 = nbasis[i1]

                if nbasis_i1:
                    b2 = knot_ik__t * nbasis_i1 / knot_ik__knot_i1
                    f2 = -nbasis_i1 / knot_ik__knot_i1
                else:
                    b2 = 0.0
                    f2 = 0.0

                d1nbasis_i = d1nbasis[i]

                if d1nbasis_i:
                    f3 = t__knot_i * d1nbasis_i / knot_ik_1__knot_i
                    s1 = 2.0 * d1nbasis_i / knot_ik_1__knot_i
                else:
                    f3 = 0.0
                    s1 = 0.0

                d1nbasis_i1 = d1nbasis[i1]

                if d1nbasis_i1:
                    f4 = knot_ik__t * d1nbasis_i1 / knot_ik__knot_i1
                    s2 = -2.0 * d1nbasis_i1 / knot_ik__knot_i1
                else:
                    f4 = 0.0
                    s2 = 0.0

                s3 = t__knot_i * d2nbasis[i] / knot_ik_1__knot_i if d2nbasis[i] else 0.0
                s4 = knot_ik__t * d2nbasis[i1] / knot_ik__knot_i1 if d2nbasis[i1] else 0.0

                nbasis[i] = b1 + b2
                d1nbasis[i] = f1 + f2 + f3 + f4
                d2nbasis[i] = s1 + s2 + s3 + s4

        count = self.count
        if self.weights is None:
            return nbasis[:count], d1nbasis[:count], d2nbasis[:count]
        else:
            return self.weighting(nbasis[:count]), self.weighting(d1nbasis[:count]), self.weighting(d2nbasis[:count])

    def create_nbasis2(self, t: float) -> List[float]:
        nbasis = self.create_nbasis(t)
        if math.isclose(t, self.max_t):
            nbasis[self.count - 1] = 1.
        return nbasis


class DBasisU(DBasis):
    def create_nbasis2(self, t: float) -> List[float]:
        nbasis = self.create_nbasis(t)
        if math.isclose(t, self.knots[self.count]):
            nbasis[self.count - 1] = 1.
            nbasis[self.count] = 0.
        return nbasis


class BSpline:
    """
    Representation of a `B-spline`_ curve, using an uniform open `knot`_ vector ("clamped").

    Accepts 2D points as definition points, but output is always 3D (z-axis = ``0``).

    Args:
        control_points: iterable of control points as :class:`Vector` compatible objects
        order: spline order
        knots: iterable of knot values
        weights: iterable of weight values

    """

    def __init__(self, control_points: Iterable['Vertex'],
                 order: int = 4,
                 knots: Iterable[float] = None,
                 weights: Iterable[float] = None):
        self.control_points: List[Vector] = Vector.list(control_points)
        self.order: int = order
        if order > self.count:
            raise DXFValueError(f'Invalid need more control points for order {order}')

        if knots is None:
            knots = open_uniform_knot_vector(self.count, self.order)
        else:
            knots = list(knots)
            if len(knots) != self.nplusc:
                raise ValueError(f"{self.nplusc} knot values required, got {len(knots)}.")

        self.basis = Basis(knots, self.order, self.count, weights=weights)

    @classmethod
    def from_fit_points(cls, points: Iterable['Vertex'], degree=3, method='chord') -> 'BSpline':
        """ Returns :class:`BSpline` defined by fit points. """
        fit_points = Vector.list(points)
        t_vector = list(create_t_vector(fit_points, method))
        control_points, knots = _global_bspline_interpolation(fit_points, degree, t_vector)
        spline = cls(control_points, order=degree + 1, knots=knots)
        spline.t_array = t_vector
        return spline

    @classmethod
    def ellipse_approximation(cls, ellipse: 'ConstructionEllipse', num: int = 16) -> 'BSpline':
        """ Returns an ellipse approximation as :class:`BSpline` with `num` control points. """
        return cls.from_fit_points(ellipse.vertices(ellipse.params(num)), degree=2)

    @classmethod
    def arc_approximation(cls, arc: 'ConstructionArc', num: int = 16) -> 'BSpline':
        """ Returns an arc approximation as :class:`BSpline` with `num` control points. """
        return cls.from_fit_points(arc.vertices(arc.angles(num)), degree=2)

    @staticmethod
    def from_ellipse(ellipse: 'ConstructionEllipse') -> 'BSpline':
        """ Returns the ellipse as :class:`BSpline` of 2nd degree with as few control points as possible. """
        return rational_spline_from_ellipse(ellipse, segments=1)

    @staticmethod
    def from_arc(arc: 'ConstructionArc') -> 'BSpline':
        """ Returns the arc as :class:`BSpline` of 2nd degree with as few control points as possible. """
        return rational_spline_from_arc(arc.center, arc.radius, arc.start_angle, arc.end_angle, segments=1)

    @property
    def nplusc(self) -> int:
        return self.count + self.order

    @property
    def count(self) -> int:
        """ Count of control points, (n + 1 in math definition). """
        return len(self.control_points)

    @property
    def max_t(self) -> float:
        """ Biggest `knot`_ value. """
        return self.basis.max_t

    @property
    def degree(self) -> int:
        """ Degree (p) of B-spline = order - 1 """
        return self.order - 1

    def knots(self) -> List[float]:
        """ Returns a list of `knot`_ values as floats, the knot vector always has order+count values
        (n + p + 2 in math definition).
        """
        return self.basis.knots

    knot_values = knots

    def weights(self) -> List[float]:
        """ Returns a list of weights values as floats, one for each control point or an empty list.
        """
        w = self.basis.weights
        if w:
            return list(w)
        else:
            return []

    def basis_values(self, t: float) -> List[float]:
        """ Returns the `basis`_ vector for position t. """
        return self.basis.basis(t)

    def step_size(self, segments: int) -> float:
        return self.max_t / float(segments)

    def approximate(self, segments: int = 20) -> Iterable[Vector]:
        """ Approximates the whole B-spline from 0 to max_t, by line segments as a list of vertices, vertices count =
        segments + 1.
        """
        step = self.step_size(segments)
        for point_index in range(segments + 1):
            yield self.point(point_index * step)

    def point(self, t: float) -> Vector:
        """
        Get point at SplineCurve(t) as tuple (x, y, z).

        Args:
            t: parameter in range [0, max_t]

        Returns: Vector(x, y, z)

        """
        if math.isclose(t, self.max_t):
            t = self.max_t

        p = Vector()
        for control_point, basis in zip(self.control_points, self.basis_values(t)):
            if basis:  # all 0 values can be skipped and there are a lot of them
                p += control_point * basis
        return p

    def insert_knot(self, t: float) -> None:
        """
        Insert additional knot, without altering the curve shape.

        Args:
            t: position of new knot 0 < t < max_t

        """
        if self.basis.weights is not None:
            raise DXFValueError('Rational splines not supported.')

        knots = self.basis.knots
        cpoints = self.control_points
        p = self.degree

        def find_knot_index() -> int:
            for knot_index in range(1, len(knots)):
                if knots[knot_index - 1] <= t < knots[knot_index]:
                    return knot_index - 1

        def new_point(index: int) -> Vector:
            a = (t - knots[index]) / (knots[index + p] - knots[index])
            return cpoints[index - 1] * (1 - a) + cpoints[index] * a

        if t <= 0. or t >= self.max_t:
            raise DXFValueError('Invalid position t')

        k = find_knot_index()
        if k < p:
            raise DXFValueError('Invalid position t')

        cpoints[k - p + 1:k] = [new_point(i) for i in range(k - p + 1, k + 1)]
        knots.insert(k + 1, t)  # knot[k] <= t < knot[k+1]
        self.basis.count = len(cpoints)

    def transform(self, m: 'Matrix44') -> 'BSpline':
        """ Transform B-spline by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        self.control_points = list(m.transform_vertices(self.control_points))
        return self


class BSplineU(BSpline):
    """ Representation of an uniform (periodic) `B-spline`_ curve (`open curve`_). """

    def __init__(self, control_points: Iterable['Vertex'], order: int = 4, weights: Iterable[float] = None):
        control_points = list(control_points)
        knots = uniform_knot_vector(len(control_points), order)
        super().__init__(control_points, order=order, knots=knots, weights=weights)

    def step_size(self, segments: int) -> float:
        return float(self.count - self.order + 1) / segments

    def approximate(self, segments=20) -> Iterable[Vector]:
        step = self.step_size(segments)
        base = float(self.order - 1)
        for point_index in range(segments + 1):
            yield self.point(base + point_index * step)

    def t_array(self) -> List[float]:
        raise NotImplemented


class BSplineClosed(BSplineU):
    """ Representation of a closed uniform `B-spline`_ curve (`closed curve`_). """

    def __init__(self, control_points: Iterable['Vertex'], order: int = 4, weights: Iterable[float] = None):
        # control points wrap around
        points = list(control_points)
        points.extend(points[:order - 1])
        if weights is not None:
            weights = list(weights)
            weights.extend(weights[:order - 1])
        super().__init__(points, order=order, weights=weights)


class DerivativePoint:  # Mixin
    def point(self, t: float) -> Tuple[Vector, Vector, Vector]:
        """
        Get point, 1st and 2nd derivative at B-spline(t) as tuple (p, d1, d3),
        where p, d1 and d2 are :class:`Vector` objects.

        Args:
            t: parameter in range [0, max_t]

        """
        if math.isclose(self.max_t, t):
            t = self.max_t

        nbasis, d1nbasis, d2nbasis = self.basis_values(t)
        point = Vector()
        d1 = Vector()
        d2 = Vector()
        for i, control_point in enumerate(self.control_points):
            point += control_point * nbasis[i]
            d1 += control_point * d1nbasis[i]
            d2 += control_point * d2nbasis[i]
        return point, d1, d2


class DBSpline(DerivativePoint, BSpline):
    """
    Subclass of :class:`BSpline`

    Calculate points and derivative of a `B-spline`_ curve, using an uniform open `knot`_ vector (`clamped curve`_).

    """

    def __init__(self, control_points: Iterable['Vertex'],
                 order: int = 4,
                 knots: Iterable[float] = None,
                 weights: Iterable[float] = None):
        super().__init__(control_points, order=order, knots=knots, weights=weights)
        self.basis = DBasis(self.knots(), self.order, self.count)


class DBSplineU(DerivativePoint, BSplineU):
    """
    Subclass of :class:`DBSpline`

    Calculate points and derivative of a `B-spline`_ curve, uniform (periodic) `knot`_ vector (`open curve`_).

    """

    def __init__(self, control_points: Iterable['Vertex'], order: int = 4, weights: Iterable[float] = None):
        super().__init__(control_points, order=order, weights=weights)
        self.basis = DBasisU(self.knots(), self.order, self.count)


class DBSplineClosed(DerivativePoint, BSplineClosed):
    """
    Subclass of :class:`DBSpline`

    Calculate the points and derivative of a closed uniform `B-spline`_ curve (`closed curve`_).

    UNTESTED!
    """

    def __init__(self, control_points: Iterable['Vertex'], order: int = 4, weights: Iterable[float] = None):
        super().__init__(control_points, order=order, weights=weights)
        self.basis = DBasisU(self.knots(), self.order, self.count)


def rational_spline_from_arc(
        center: Vector = (0, 0), radius: float = 1, start_angle: float = 0, end_angle: float = 360,
        segments: int = 1) -> BSpline:
    """
    Returns a rational B-splines for a circular 2D arc.

    Args:
        center: circle center as :class:`Vector` compatible object
        radius: circle radius
        start_angle: start angle in degrees
        end_angle: end angle in degrees
        segments: count of spline segments, at least one segment for each quarter (90 deg), ``1`` for as few as needed.

    .. versionadded:: 0.13

    """
    center = Vector(center)
    radius = float(radius)
    start_angle = math.radians(start_angle) % math.tau
    end_angle = math.radians(end_angle) % math.tau
    control_points, weights, knots = nurbs_arc_parameters(start_angle, end_angle, segments)
    return BSpline(
        control_points=(center + (p * radius) for p in control_points),
        weights=weights,
        knots=knots,
        order=3,
    )


PI_2 = math.pi / 2.0


def rational_spline_from_ellipse(ellipse: 'ConstructionEllipse', segments: int = 1) -> BSpline:
    """
    Returns a rational B-splines for an elliptic arc.

    Args:
        ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse` object
        segments: count of spline segments, at least one segment for each quarter (pi/2), ``1`` for as few as needed.

    .. versionadded:: 0.13

    """
    from ezdxf.math import param_to_angle
    start_angle = param_to_angle(ellipse.ratio, ellipse.start_param) % math.tau
    end_angle = param_to_angle(ellipse.ratio, ellipse.end_param) % math.tau

    def transform_control_points() -> Iterable[Vector]:
        center = Vector(ellipse.center)
        x_axis = ellipse.major_axis
        y_axis = ellipse.minor_axis
        for p in control_points:
            yield center + x_axis * p.x + y_axis * p.y

    control_points, weights, knots = nurbs_arc_parameters(start_angle, end_angle, segments)
    return BSpline(
        control_points=transform_control_points(),
        weights=weights,
        knots=knots,
        order=3,
    )


def nurbs_arc_parameters(start_angle: float, end_angle: float, segments: int = 1):
    """
    Returns a rational B-spline parameters for a circular 2D arc with center at (0, 0) and a radius of 1.

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians
        segments: count of segments, at least one segment for each quarter (pi/2)

    Returns: control_points, weights, knots

    """
    # Source: https://www.researchgate.net/publication/283497458_ONE_METHOD_FOR_REPRESENTING_AN_ARC_OF_ELLIPSE_BY_A_NURBS_CURVE/citation/download
    if segments < 1:
        raise ValueError('Invalid argument segments (>= 1).')
    delta_angle = end_angle - start_angle
    arc_count = max(math.ceil(delta_angle / PI_2), segments)

    segment_angle = delta_angle / arc_count
    segment_angle_2 = segment_angle / 2
    arc_weight = math.cos(segment_angle_2)

    # First control point
    control_points = [Vector(math.cos(start_angle), math.sin(start_angle))]
    weights = [1.0]

    angle = start_angle
    d = 1.0 / math.cos(segment_angle / 2.0)
    for _ in range(arc_count):
        # next control point between points on arc
        angle += segment_angle_2
        control_points.append(Vector(math.cos(angle) * d, math.sin(angle) * d))
        weights.append(arc_weight)

        # next control point on arc
        angle += segment_angle_2
        control_points.append(Vector(math.cos(angle), math.sin(angle)))
        weights.append(1.0)

    # Knot vector calculation for B-spline of order=3
    # Clamped B-Spline starts with `order` 0.0 knots and
    # ends with `order` 1.0 knots
    knots = [0.0, 0.0, 0.0]
    step = 1.0 / ((max(len(control_points) + 1, 4) - 4) / 2.0 + 1.0)
    g = step
    while g < 1.0:
        knots.extend((g, g))
        g += step
    knots.extend([1.0] * (required_knot_values(len(control_points), 3) - len(knots)))

    return control_points, weights, knots


def bspline_basis(u: float, index: int, degree: int, knots: Sequence[float]) -> float:
    """
    B-spline basis function.

    Simple recursive implementation for testing and comparison.

    Args:
        u: curve parameter in range [0 .. max(knots)]
        index: index of control point
        degree: degree of B-spline
        knots: knots vector

    Returns:
        float: basis value N_i,p(u)

    """
    cache = {}  # type: Dict[Tuple[int, int], float]
    u = float(u)

    def N(i: int, p: int) -> float:
        try:
            return cache[(i, p)]
        except KeyError:
            if p == 0:
                retval = 1 if knots[i] <= u < knots[i + 1] else 0.
            else:
                dominator = (knots[i + p] - knots[i])
                f1 = (u - knots[i]) / dominator * N(i, p - 1) if dominator else 0.

                dominator = (knots[i + p + 1] - knots[i + 1])
                f2 = (knots[i + p + 1] - u) / dominator * N(i + 1, p - 1) if dominator else 0.

                retval = f1 + f2
            cache[(i, p)] = retval
            return retval

    return N(int(index), int(degree))


def bspline_basis_vector(u: float, count: int, degree: int, knots: Sequence[float]) -> List[float]:
    """
    Create basis vector at parameter u.

    Used with the bspline_basis() for testing and comparison.

    Args:
        u: curve parameter in range [0 .. max(knots)]
        count: control point count (n + 1)
        degree: degree of B-spline (order = degree + 1)
        knots: knot vector

    Returns:
        List[float]: basis vector, len(basis) == count

    """
    assert len(knots) == (count + degree + 1)
    basis = [bspline_basis(u, index, degree, knots) for index in range(count)]  # type: List[float]
    if math.isclose(u, knots[-1]):  # pick up last point ??? why is this necessary ???
        basis[-1] = 1.
    return basis


def bspline_vertex(u: float, degree: int, control_points: Sequence['Vertex'], knots: Sequence[float]) -> Vector:
    """
    Calculate B-spline vertex at parameter u.

    Used with the bspline_basis_vector() for testing and comparison.

    Args:
        u:  curve parameter in range [0 .. max(knots)]
        degree: degree of B-spline (order = degree + 1)
        control_points: control points as list of (x, y[,z]) tuples
        knots: knot vector as list of floats, len(knots) == (count + order)

    """
    basis_vector = bspline_basis_vector(u, count=len(control_points), degree=degree, knots=knots)

    vertex = Vector()
    for basis, point in zip(basis_vector, control_points):
        vertex += Vector(point) * basis
    return vertex
