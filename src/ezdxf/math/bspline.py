# Copyright (c) 2012-2020 Manfred Moitzi
# License: MIT License
"""
B-Splines
=========

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node4.html

Rational B-splines
==================

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node5.html:

"The NURBS Book" by Les Piegl and Wayne Tiller

https://books.google.at/books/about/The_NURBS_Book.html?id=7dqY5dyAwWkC&redir_esc=y

"""
from typing import (
    List, Iterable, Sequence, TYPE_CHECKING, Dict, Tuple,
    Optional, Union,
)
import math
import bisect
from ezdxf.math import Vec3, NULLVEC
from .parametrize import (
    create_t_vector, estimate_tangents,
    estimate_end_tangent_magnitude,
)
from .linalg import (
    LUDecomposition, Matrix, BandedMatrixLU, compact_banded_matrix,
    detect_banded_matrix,
    quadratic_equation, binomial_coefficient,
)
from .construct2d import linspace
from .construct3d import distance_point_line_3d
from ezdxf.lldxf.const import DXFValueError
from ezdxf import PYPY

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
    from ezdxf.math import ConstructionArc, ConstructionEllipse, Matrix44
    from .bezier4p import Bezier4P

# Acceleration of banded diagonal matrix solver kicks in at:
# N=15 for CPython on Windows and Linux
# N=60 for pypy3 on Windows and Linux
USE_BANDED_MATRIX_SOLVER_CPYTHON_LIMIT = 15
USE_BANDED_MATRIX_SOLVER_PYPY_LIMIT = 60

__all__ = [
    # High level functions:
    'fit_points_to_cad_cv', 'global_bspline_interpolation',
    'local_cubic_bspline_interpolation', 'rational_spline_from_arc',
    'rational_spline_from_ellipse',

    # B-spline representation without derivatives support:
    'BSpline', 'BSplineU', 'BSplineClosed',

    # Low level interpolation function:
    'unconstrained_global_bspline_interpolation',
    'global_bspline_interpolation_end_tangents',
    'global_bspline_interpolation_first_derivatives',
    'local_cubic_bspline_interpolation_from_tangents',

    # Low level knot parametrization functions:
    'knots_from_parametrization', 'averaged_knots_unconstrained',
    'averaged_knots_constrained',
    'natural_knots_unconstrained', 'natural_knots_constrained', 'double_knots',

    # Low level knot function:
    'required_knot_values', 'uniform_knot_vector', 'open_uniform_knot_vector',
]


def fit_points_to_cad_cv(fit_points: Iterable['Vertex'], degree: int = 3,
                         method='chord',
                         tangents: Iterable['Vertex'] = None) -> 'BSpline':
    """ Returns the control vertices and knot vector configuration for DXF SPLINE entities
    defined only by fit points as close as possible to common CAD applications like BricsCAD.

    There exist infinite numerical correct solution for this setup, but some facts are known:

    - Global curve interpolation with start- and end derivatives, e.g. 6 fit points
      creates 8 control vertices in BricsCAD
    - Degree of B-spline is limited to 2 or 3, a stored degree of >3 is ignored, this limit exist only
      for B-splines defined by fit points
    - Knot parametrization method is "chord"
    - Knot distribution is "natural"

    The last missing parameter is the start- and end tangents estimation method used by BricsCAD,
    if these tangents are stored in the DXF file provide them as argument `tangents` as
    2-tuple (start, end) and the interpolated control vertices will match the BricsCAD calculation,
    except for floating point imprecision.

    Args:
        fit_points: points the spline is passing through
        degree: degree of spline, only 2 or 3 is supported by BricsCAD, default = 3
        method: knot parametrization method, default = 'chord'
        tangents: start- and end tangent, default is autodetect

    Returns:
        :class:`BSpline`

    .. versionadded:: 0.13

    """
    points = Vec3.list(fit_points)
    m1, m2 = estimate_end_tangent_magnitude(points, method='chord')
    if tangents is None:
        # 5-points is the closest estimation method I found so far
        tangents = estimate_tangents(points, method='5-p')
        start_tangent = tangents[0].normalize(m1)
        end_tangent = tangents[-1].normalize(m2)
    else:
        tangents = Vec3.list(tangents)
        start_tangent = Vec3(tangents[0]).normalize(m1)
        end_tangent = Vec3(tangents[-1]).normalize(m2)

    degree = int(degree)
    if degree < 2:
        degree = 2
    elif degree > 3:
        degree = 3
    return global_bspline_interpolation(points, degree,
                                        (start_tangent, end_tangent), method)


def global_bspline_interpolation(
        fit_points: Iterable['Vertex'],
        degree: int = 3,
        tangents: Iterable['Vertex'] = None,
        method: str = 'chord') -> 'BSpline':
    """
    `B-spline`_ interpolation  by `Global Curve Interpolation`_.
    Given are the fit points and the degree of the B-spline.
    The function provides 3 methods for generating the parameter vector t:

    - "uniform": creates a uniform t vector, from 0 to 1 evenly spaced, see `uniform`_ method
    - "chord", "distance": creates a t vector with values proportional to the fit point distances,
      see `chord length`_ method
    - "centripetal", "sqrt_chord": creates a t vector with values proportional to the fit point sqrt(distances),
      see `centripetal`_ method
    - "arc": creates a t vector with values proportional to the arc length between fit points.

    It is possible to constraint the curve by tangents, by start- and end tangent if only two tangents
    are given or by one tangent for each fit point.

    If tangents are given, they represent 1st derivatives and and should be scaled if they are
    unit vectors, if only start- and end tangents given the function :func:`~ezdxf.math.estimate_end_tangent_magnitude`
    helps with an educated guess, if all tangents are given, scaling by chord length is a reasonable
    choice (Piegl & Tiller).

    Args:
        fit_points: fit points of B-spline, as list of :class:`Vec3` compatible objects
        tangents: if only two vectors are given, take the first and the last vector as start-
            and end tangent constraints or if for all fit points a tangent is given use all
            tangents as interpolation constraints (optional)
        degree: degree of B-spline
        method: calculation method for parameter vector t

    Returns:
        :class:`BSpline`

    """
    fit_points = Vec3.list(fit_points)
    count = len(fit_points)
    order = degree + 1

    if tangents:
        # two control points for tangents will be added
        count += 2
    if order > count and tangents is None:
        raise ValueError(f'More fit points required for degree {degree}')

    t_vector = list(create_t_vector(fit_points, method))
    # natural knot generation for uneven degrees else averaged
    knot_generation_method = 'natural' if degree % 2 else 'average'
    if tangents is not None:
        tangents = Vec3.list(tangents)
        if len(tangents) == 2:
            control_points, knots = global_bspline_interpolation_end_tangents(
                fit_points, tangents[0], tangents[1], degree, t_vector,
                knot_generation_method)
        elif len(tangents) == len(fit_points):
            control_points, knots = global_bspline_interpolation_first_derivatives(
                fit_points, tangents, degree, t_vector)
        else:
            raise ValueError(
                'Invalid count of tangents, two tangents as start- and end tangent constrains'
                ' or one tangent for each fit point.'
            )
    else:
        control_points, knots = unconstrained_global_bspline_interpolation(
            fit_points, degree, t_vector,
            knot_generation_method)
    bspline = BSpline(control_points, order=order, knots=knots)
    bspline.t_array = t_vector
    return bspline


def local_cubic_bspline_interpolation(
        fit_points: Iterable['Vertex'],
        method: str = '5-points',
        tangents: Iterable['Vertex'] = None) -> 'BSpline':
    """
    `B-spline`_ interpolation by 'Local Cubic Curve Interpolation', which creates
    B-spline from fit points and estimated tangent direction at start-, end- and
    passing points.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.3.4

    Available tangent estimation methods:

    - "3-points": 3 point interpolation
    - "5-points": 5 point interpolation
    - "bezier": cubic bezier curve interpolation
    - "diff": finite difference

    or pass pre-calculated tangents, which overrides tangent estimation.

    Args:
        fit_points: all B-spline fit points as :class:`Vec3` compatible objects
        method: tangent estimation method
        tangents: tangents as :class:`Vec3` compatible objects (optional)

    Returns:
        :class:`BSpline`

    """
    from .parametrize import estimate_tangents
    fit_points = Vec3.list(fit_points)
    if tangents:
        tangents = Vec3.list(tangents)
    else:
        tangents = estimate_tangents(fit_points, method)
    control_points, knots = local_cubic_bspline_interpolation_from_tangents(
        fit_points, tangents)
    return BSpline(control_points, order=4, knots=knots)


def required_knot_values(count: int, order: int) -> int:
    """
    Returns the count of required knot values for a B-spline of `order` and `count` control points.

    Args:
        count: count of control points, in text-books referred as "n + 1"
        order: order of B-Spline, in text-books referred as "k"

    Relationship:

    "p" is the degree of the B-spline, text-book notation.

    - k = p + 1
    - 2 ≤ k ≤ n + 1

    """
    k = int(order)
    n = int(count) - 1
    p = k - 1
    if not (2 <= k <= (n + 1)):
        raise DXFValueError('Invalid count/order combination')
    # n + p + 2 = count + order
    return n + p + 2


def normalize_knots(knots: List[float]) -> List[float]:
    """ Normalize knot vector into range [0, 1]. """
    min_val = min(knots)
    max_val = max(knots) - min_val
    return [(v - min_val) / max_val for v in knots]


def uniform_knot_vector(count: int, order: int, normalize=False) -> List[float]:
    """
    Returns an uniform knot vector for a B-spline of `order` and `count` control points.

    `order` = degree + 1

    Args:
        count: count of control points
        order: spline order
        normalize: normalize values in range [0, 1] if ``True``

    """
    if normalize:
        max_value = float(count + order - 1)
    else:
        max_value = 1.0
    return [knot_value / max_value for knot_value in range(count + order)]


def open_uniform_knot_vector(count: int, order: int, normalize=False) -> List[
    float]:
    """
    Returns an open (clamped) uniform knot vector for a B-spline of `order` and `count` control points.

    `order` = degree + 1

    Args:
        count: count of control points
        order: spline order
        normalize: normalize values in range [0, 1] if ``True``

    """
    k = count - order
    if normalize:
        max_value = float(count - order + 1)
        tail = [1.0] * order
    else:
        max_value = 1.0
        tail = [1.0 + k] * order

    knots = [0.0] * order
    knots.extend((1.0 + v) / max_value for v in range(k))
    knots.extend(tail)
    return knots


def knots_from_parametrization(n: int, p: int, t: Iterable[float],
                               method='average', constrained=False) -> List[
    float]:
    """
    Returns a 'clamped' knot vector for B-splines.
    All knot values normalized in the range [0 .. 1].

    Args:
        n: count fit points - 1
        p: degree of spline
        t: parametrization vector, length(t_vector) == n, normalized [0..1]
        method: "average", "natural"
        constrained: ``True`` for B-spline constrained by end derivatives

    Returns:
        List of n+p+2 knot values as floats

    """
    order = int(p + 1)
    if order > (n + 1):
        raise DXFValueError(
            'Invalid n/p combination, more fit points required.')

    t = [float(v) for v in t]
    if t[0] != 0.0 or t[-1] != 1.0:
        raise ValueError('Parametrization vector t has to be normalized.')

    if method == 'average':
        return averaged_knots_constrained(n, p,
                                          t) if constrained else averaged_knots_unconstrained(
            n, p, t)
    elif method == 'natural':
        return natural_knots_constrained(n, p,
                                         t) if constrained else natural_knots_unconstrained(
            n, p, t)
    else:
        raise ValueError(f'Unknown knot generation method: {method}')


def averaged_knots_unconstrained(n: int, p: int, t: Sequence[float]) -> List[
    float]:
    """
    Returns an averaged knot vector from parametrization vector `t` for an unconstrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0..1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(sum(t[j: j + p]) / p for j in range(1, n - p + 1))
    if knots[-1] > 1.0:
        raise ValueError('Normalized [0..1] values required')
    knots.extend([1.0] * (p + 1))
    return knots


def averaged_knots_constrained(n: int, p: int, t: Sequence[float]) -> List[
    float]:
    """
    Returns an averaged knot vector from parametrization vector `t` for a constrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0..1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(sum(t[j: j + p - 1]) / p for j in range(n - p))
    knots.extend([1.0] * (p + 1))
    return knots


def natural_knots_unconstrained(n: int, p: int, t: Sequence[float]) -> List[
    float]:
    """
    Returns a 'natural' knot vector from parametrization vector `t` for an unconstrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0..1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(t[2: n - p + 2])
    knots.extend([1.0] * (p + 1))
    return knots


def natural_knots_constrained(n: int, p: int, t: Sequence[float]) -> List[
    float]:
    """
    Returns a 'natural' knot vector from parametrization vector `t` for a constrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0..1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(t[1: n - p + 1])
    knots.extend([1.0] * (p + 1))
    return knots


def double_knots(n: int, p: int, t: Sequence[float]) -> List[float]:
    """
    Returns a knot vector from parametrization vector `t` for B-spline constrained
    by first derivatives at all fit points.

    Args:
        n: count of fit points - 1
        p: degree of spline
        t: parametrization vector, first value has to be 0.0 and last value has to be 1.0

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    u = [0.0] * (p + 1)
    prev_t = 0.0

    u1 = []
    for t1 in t[1:-1]:
        if p == 2:
            # add one knot between prev_t and t
            u1.append((prev_t + t1) / 2.0)
            u1.append(t1)
        else:
            if prev_t == 0.0:  # first knot
                u1.append(t1 / 2)
            else:
                # add one knot at the 1st third and one knot
                # at the 2nd third between prev_t and t.
                u1.append((2 * prev_t + t1) / 3.0)
                u1.append((prev_t + 2 * t1) / 3.0)
        prev_t = t1
    u.extend(u1[:n * 2 - p])
    u.append((t[-2] + 1.0) / 2.0)  # last knot
    u.extend([1.0] * (p + 1))
    return u


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


def unconstrained_global_bspline_interpolation(
        fit_points: Sequence['Vertex'],
        degree: int,
        t_vector: Sequence[float],
        knot_generation_method: str = 'average') -> Tuple[
    List[Vec3], List[float]]:
    """
    Interpolate the control points for a B-spline by global interpolation from fit points without
    any constraints.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.2.1

    Args:
        fit_points: points the B-spline has to pass
        degree: degree of spline >= 2
        t_vector: parametrization vector, first value has to be 0.0 and last value has to be 1.0
        knot_generation_method: knot generation method from parametrization vector, "average" or "natural"

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector as list of floats

    """
    # Source: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
    knots = knots_from_parametrization(len(fit_points) - 1, degree, t_vector,
                                       knot_generation_method,
                                       constrained=False)
    N = Basis(knots=knots, order=degree + 1, count=len(fit_points))
    solver = _get_best_solver([N.basis_vector(t) for t in t_vector], degree)
    control_points = solver.solve_matrix(fit_points)
    return Vec3.list(control_points.rows()), knots


def global_bspline_interpolation_end_tangents(
        fit_points: List[Vec3],
        start_tangent: Vec3,
        end_tangent: Vec3,
        degree: int,
        t_vector: Sequence[float],
        knot_generation_method: str = 'average') -> Tuple[
    List[Vec3], List[float]]:
    """
    Interpolate the control points for a B-spline by global interpolation from fit points and
    1st derivatives for start- and end point as constraints. These 'tangents' are 1st derivatives
    and not unit vectors, if an estimation of the magnitudes is required use the
    :func:`estimate_end_tangent_magnitude` function.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.2.2

    Args:
        fit_points: points the B-spline has to pass
        start_tangent: 1st derivative as start constraint
        end_tangent: 1st derivative as end constrain
        degree: degree of spline >= 2
        t_vector: parametrization vector, first value has to be 0.0 and last value has to be 1.0
        knot_generation_method: knot generation method from parametrization vector, "average" or "natural"

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector as list of floats

    """
    n = len(fit_points) - 1
    p = degree
    if degree > 3:
        # todo: 'average' produces weird results for degree > 3, 'natural' is better but also not good
        knot_generation_method = 'natural'
    knots = knots_from_parametrization(n + 2, p, t_vector,
                                       knot_generation_method, constrained=True)

    N = Basis(knots=knots, order=p + 1, count=n + 3)
    rows = [N.basis_vector(u) for u in t_vector]
    spacing = [0.0] * (n + 1)
    rows.insert(1, [-1.0, +1.0] + spacing)
    rows.insert(-1, spacing + [-1.0, +1.0])
    fit_points.insert(1, start_tangent * (knots[p + 1] / p))
    fit_points.insert(-1, end_tangent * ((1.0 - knots[-(p + 2)]) / p))

    solver = _get_best_solver(rows, degree)
    control_points = solver.solve_matrix(fit_points)
    return Vec3.list(control_points.rows()), knots


def global_bspline_interpolation_first_derivatives(
        fit_points: List[Vec3],
        derivatives: List[Vec3],
        degree: int,
        t_vector: Sequence[float]) -> Tuple[List[Vec3], List[float]]:
    """
    Interpolate the control points for a B-spline by global interpolation from fit points and
    1st derivatives as constraints.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.2.4

    Args:
        fit_points: points the B-spline has to pass
        derivatives: 1st derivatives as constrains, not unit vectors!
            Scaling by chord length is a reasonable choice (Piegl & Tiller).
        degree: degree of spline >= 2
        t_vector: parametrization vector, first value has to be 0.0 and last value has to be 1.0

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector as list of floats

    """

    def nbasis(t: float):
        span = N.find_span(t)
        front = span - p
        back = count + p + 1 - span
        for basis in N.basis_funcs_derivatives(span, t, n=1):
            yield [0.0] * front + basis + [0.0] * back

    p = degree
    n = len(fit_points) - 1
    knots = double_knots(n, p, t_vector)
    count = len(fit_points) * 2
    N = Basis(knots=knots, order=p + 1, count=count)
    A = [
        [1.0] + [0.0] * (count - 1),  # Q0
        [-1.0, +1.0] + [0.0] * (count - 2),  # D0
    ]
    for f in (nbasis(t) for t in t_vector[1:-1]):
        A.extend(f)  # Qi, Di
    # swapped equations!
    A.append([0.0] * (count - 2) + [-1.0, +1.0])  # Dn
    A.append([0.0] * (count - 1) + [+1.0])  # Qn

    # Build right handed matrix B
    B = []
    for rows in zip(fit_points, derivatives):
        B.extend(rows)  # Qi, Di

    # also swap last rows!
    B[-1], B[-2] = B[-2], B[-1]  # Dn, Qn

    # modify equation for derivatives D0 and Dn
    B[1] *= knots[p + 1] / p
    B[-2] *= (1.0 - knots[-(p + 2)]) / p
    solver = _get_best_solver(A, degree)
    control_points = solver.solve_matrix(B)
    return Vec3.list(control_points.rows()), knots


def local_cubic_bspline_interpolation_from_tangents(
        fit_points: List[Vec3],
        tangents: List[Vec3]) -> Tuple[List[Vec3], List[float]]:
    """
    Interpolate the control points for a cubic B-spline by local interpolation from fit points and
    tangents as unit vectors for each fit point. if an estimation of tangents is required use the
    :func:`estimate_tangents` function.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.3.4

    Args:
        fit_points: curve definition points - curve has to pass all given fit points
        tangents: one tangent vector for each fit point as unit vectors

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector as list of floats

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
    def __init__(self, knots: Iterable[float], order: int, count: int,
                 weights: Sequence[float] = None):
        self.knots: List[float] = list(knots)
        self.order: int = order
        self.count: int = count
        self.weights: Optional[Sequence[float]] = weights

    @property
    def max_t(self) -> float:
        return self.knots[-1]

    @property
    def is_rational(self) -> bool:
        """ Returns ``True`` if curve is a rational B-spline. (has weights) """
        return bool(self.weights)

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
        knots = self.knots
        count = self.count
        p = self.order - 1
        # if it is an standard clamped spline
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
        knots = self.knots
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
        weights = self.weights[span - self.order + 1: span + 1]
        products = [nb * w for nb, w in zip(nbasis, weights)]
        s = sum(products)
        return [0.0] * self.order if s == 0.0 else [p / s for p in products]

    def basis_funcs_derivatives(self, span: int, u: float, n: int = 1):
        # Source: The NURBS Book: Algorithm A2.3
        order = self.order
        p = order - 1
        n = min(n, p)

        knots = self.knots
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
                                      self.weights[index]
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


class BSpline:
    """
    Representation of a `B-spline`_ curve, using an uniform open `knot`_ vector ("clamped").

    Args:
        control_points: iterable of control points as :class:`Vec3` compatible objects
        order: spline order (degree + 1)
        knots: iterable of knot values
        weights: iterable of weight values

    """

    def __init__(self, control_points: Iterable['Vertex'],
                 order: int = 4,
                 knots: Iterable[float] = None,
                 weights: Iterable[float] = None):
        self.control_points: List[Vec3] = Vec3.list(control_points)
        self.order: int = order
        if order > self.count:
            raise DXFValueError(
                f'Invalid need more control points for order {order}')

        if knots is None:
            knots = open_uniform_knot_vector(self.count, self.order,
                                             normalize=True)
        else:
            knots = list(knots)
            required_knot_count = self.count + self.order
            if len(knots) != required_knot_count:
                raise ValueError(
                    f"{required_knot_count} knot values required, got {len(knots)}.")
            if knots[0] != 0.0:
                knots = normalize_knots(knots)
        self.basis = Basis(knots, self.order, self.count, weights=weights)

    def __str__(self):
        return f'BSpline degree={self.degree}, {len(self.control_points)} control points, {len(self.knots())} knot values, {len(self.weights())} weights'

    @staticmethod
    def from_fit_points(points: Iterable['Vertex'], degree=3,
                        method='chord') -> 'BSpline':
        """ Returns :class:`BSpline` defined by fit points. """
        return global_bspline_interpolation(points, degree, method=method)

    @staticmethod
    def ellipse_approximation(ellipse: 'ConstructionEllipse',
                              num: int = 16) -> 'BSpline':
        """ Returns an ellipse approximation as :class:`BSpline` with `num` control points. """
        return global_bspline_interpolation(
            ellipse.vertices(ellipse.params(num)), degree=2)

    @staticmethod
    def arc_approximation(arc: 'ConstructionArc', num: int = 16) -> 'BSpline':
        """ Returns an arc approximation as :class:`BSpline` with `num` control points. """
        return global_bspline_interpolation(arc.vertices(arc.angles(num)),
                                            degree=2)

    @staticmethod
    def from_ellipse(ellipse: 'ConstructionEllipse') -> 'BSpline':
        """ Returns the ellipse as :class:`BSpline` of 2nd degree with as few control points as possible. """
        return rational_spline_from_ellipse(ellipse, segments=1)

    @staticmethod
    def from_arc(arc: 'ConstructionArc') -> 'BSpline':
        """ Returns the arc as :class:`BSpline` of 2nd degree with as few control points as possible. """
        return rational_spline_from_arc(arc.center, arc.radius, arc.start_angle,
                                        arc.end_angle, segments=1)

    @staticmethod
    def from_nurbs_python_curve(curve) -> 'BSpline':
        """
        Interface to `NURBS-Python <https://pypi.org/project/geomdl/>`_.

        Returns a :class:`BSpline` object from a :class:`geomdl.BSpline.Curve` object.

        """
        return BSpline(
            control_points=curve.ctrlpts,
            order=curve.order,
            knots=curve.knotvector,
            weights=curve.weights,
        )

    def reverse(self) -> 'BSpline':
        """ Returns a new BSpline with reversed control point order. """

        def reverse_knots():
            for k in reversed(normalize_knots(self.knots())):
                yield 1.0 - k

        return self.__class__(
            control_points=reversed(self.control_points),
            order=self.order,
            knots=reverse_knots(),
            weights=list(reversed(self.weights())),
        )

    def normalize_knots(self):
        """ Normalize knot vector into range [0, 1]. """
        if self.basis.knots:
            self.basis.knots = normalize_knots(self.basis.knots)

    @property
    def count(self) -> int:
        """ Count of control points, (n + 1 in text book notation). """
        return len(self.control_points)

    @property
    def max_t(self) -> float:
        """ Biggest `knot`_ value. """
        return self.basis.max_t

    @property
    def degree(self) -> int:
        """ Degree (p) of B-spline = order - 1 """
        return self.order - 1

    @property
    def is_rational(self):
        """ Returns ``True`` if curve is a rational B-spline. (has weights) """
        return self.basis.is_rational

    @property
    def is_clamped(self):
        """ Returns ``True`` if curve is a clamped (open) B-spline. """
        return not any(self.basis.knots[:self.order])

    def knots(self) -> List[float]:
        """ Returns a list of `knot`_ values as floats, the knot vector **always** has order + count values
        (n + p + 2 in text book notation).
        """
        return self.basis.knots

    knot_values = knots

    def weights(self) -> List[float]:
        """ Returns a list of weights values as floats, one for each control point or an empty list.
        """
        if self.basis.is_rational:
            return list(self.basis.weights)
        else:
            return []

    def step_size(self, segments: int) -> float:
        return self.max_t / float(segments)

    def approximate(self, segments: int = 20) -> Iterable[Vec3]:
        """ Approximates curve by vertices as :class:`Vec3` objects, vertices count = segments + 1. """
        yield from self.points(self.params(segments))

    def flattening(self, distance: float,
                   segments: int = 4) -> Iterable[Vec3]:
        """ Adaptive recursive flattening. The argument `segments` is the
        minimum count of approximation segments between two knots, if the
        distance from the center of the approximation segment to the curve is
        bigger than `distance` the segment will be subdivided.

        Args:
            distance: maximum distance from the projected curve point onto the
                segment chord.
            segments: minimum segment count between two knots

        .. versionadded:: 0.15

        """

        def subdiv(s: Vec3, e: Vec3, start_t: float, end_t: float):
            mid_t = (start_t + end_t) * 0.5
            m = self.point(mid_t)
            if distance_point_line_3d(m, s, e) < distance:
                yield e
            else:
                yield from subdiv(s, m, start_t, mid_t)
                yield from subdiv(m, e, mid_t, end_t)

        knots = sorted(set(self.knots()))
        t = 0.0
        start_point = self.point(t)
        yield start_point
        for t1 in knots[1:]:
            delta = (t1 - t) / segments
            while t < t1:
                next_t = t + delta
                if math.isclose(next_t, t1):
                    next_t = t1
                end_point = self.point(next_t)
                yield from subdiv(start_point, end_point, t, next_t)
                t = next_t
                start_point = end_point

    def params(self, segments: int) -> Iterable[float]:
        """ Yield evenly spaced parameters from 0 to max_t for given segment count. """
        return linspace(0, self.max_t, segments + 1)

    def point(self, t: float) -> Vec3:
        """
        Returns point for parameter `t`.

        Args:
            t: parameter in range [0, max_t]

        """
        if math.isclose(t, self.max_t):
            t = self.max_t
        return self.basis.curve_point(t, self.control_points)

    def points(self, t: Iterable[float]) -> Iterable[Vec3]:
        """
        Yields points for parameter vector `t`.

        Args:
            t: parameters in range [0, max_t]

        """
        for u in t:
            yield self.point(u)

    def derivative(self, t: float, n: int = 2) -> List[Vec3]:
        """
        Return point and derivatives up to `n` <= degree for parameter `t`.

        e.g. n=1 returns point and 1st derivative.

        Args:
            t: parameter in range [0, max_t]
            n: compute all derivatives up to n <= degree

        Returns:
            n+1 values as :class:`Vec3` objects

        """
        if math.isclose(t, self.max_t):
            t = self.max_t
        return self.basis.curve_derivatives(t, self.control_points, n)

    def derivatives(self, t: Iterable[float], n: int = 2) -> Iterable[
        List[Vec3]]:
        """
        Yields points and derivatives up to `n` <= degree for parameter vector `t`.

        e.g. n=1 returns point and 1st derivative.

        Args:
            t: parameters in range [0, max_t]
            n: compute all derivatives up to n <= degree

        Returns:
            List of n+1 values as :class:`Vec3` objects

        """
        for u in t:
            yield self.derivative(u, n)

    def insert_knot(self, t: float) -> None:
        """
        Insert additional knot, without altering the curve shape.

        Args:
            t: position of new knot 0 < t < max_t

        """
        if self.basis.is_rational:
            raise TypeError('Rational B-splines not supported.')

        knots = self.basis.knots
        cpoints = self.control_points
        p = self.degree

        def new_point(index: int) -> Vec3:
            a = (t - knots[index]) / (knots[index + p] - knots[index])
            return cpoints[index - 1] * (1 - a) + cpoints[index] * a

        if t <= 0. or t >= self.max_t:
            raise DXFValueError('Invalid position t')

        k = self.basis.find_span(t)
        if k < p:
            raise DXFValueError('Invalid position t')

        cpoints[k - p + 1:k] = [new_point(i) for i in range(k - p + 1, k + 1)]
        knots.insert(k + 1, t)  # knot[k] <= t < knot[k+1]
        self.basis.count = len(cpoints)

    def knot_refinement(self, u: Iterable[float]) -> None:
        """ Insert multiple knots, without altering the curve

        Args:
            u: vector of new knots t and for each t: 0 < t  < max_t

        """
        for t in u:
            self.insert_knot(t)

    def transform(self, m: 'Matrix44') -> 'BSpline':
        """ Transform B-spline by transformation matrix `m` inplace.

        .. versionadded:: 0.13

        """
        self.control_points = list(m.transform_vertices(self.control_points))
        return self

    def to_nurbs_python_curve(self):
        """
        Returns a :class:`geomdl.BSpline.Curve` object if the `NURBS-Python <https://pypi.org/project/geomdl/>`_
        package is installed.

        """
        if self.basis.is_rational:
            from geomdl.NURBS import Curve
        else:
            from geomdl.BSpline import Curve
        curve = Curve()
        curve.degree = self.degree
        curve.ctrlpts = [v.xyz for v in self.control_points]
        curve.knotvector = self.knots()
        curve.weights = self.weights()
        return curve

    def bezier_decomposition(self) -> Iterable[List[Vec3]]:
        """ Decompose a non-rational B-spline into multiple Bézier curves.

        This is the preferred method to represent the most common non-rational
        B-splines of 3rd degree by cubic Bézier curves, which are often supported
        by render backends.

        Returns:
            Yields control points of Bézier curves, each Bézier segment
            has degree+1 control points e.g. B-spline of 3rd degree yields
            cubic Bézier curves of 4 control points.

        """
        # Source: "The NURBS Book": Algorithm A5.6
        if self.basis.is_rational:
            raise TypeError('Rational B-splines not supported.')
        if not self.is_clamped:
            raise TypeError('Clamped B-Spline required.')

        n = self.count - 1
        p = self.degree
        knots = self.basis.knots  # U
        control_points = self.control_points  # Pw
        alphas = [0.0] * len(knots)

        m = n + p + 1
        a = p
        b = p + 1
        bezier_points = control_points[0: p + 1]  # Qw

        while b < m:
            next_bezier_points = [NULLVEC] * (p + 1)
            i = b
            while b < m and math.isclose(knots[b + 1], knots[b]):
                b += 1
            mult = b - i + 1
            if mult < p:
                numer = knots[b] - knots[a]
                for j in range(p, mult, -1):
                    alphas[j - mult - 1] = numer / (knots[a + j] - knots[a])
                r = p - mult
                for j in range(1, r + 1):
                    save = r - j
                    s = mult + j
                    for k in range(p, s - 1, -1):
                        alpha = alphas[k - s]
                        bezier_points[k] = bezier_points[k] * alpha + \
                                           bezier_points[k - 1] * (1.0 - alpha)
                    if b < m:
                        next_bezier_points[save] = bezier_points[p]
            yield bezier_points

            if b < m:
                for i in range(p - mult, p + 1):
                    next_bezier_points[i] = control_points[b - p + i]
                a = b
                b += 1
                bezier_points = next_bezier_points

    def cubic_bezier_approximation(self, level: int = 3,
                                   segments: int = None) -> Iterable[
        'Bezier4P']:
        """ Approximate arbitrary B-splines (degree != 3 and/or rational) by multiple segments of
        cubic Bézier curves. The choice of cubic Bézier curves is based on the widely support
        of this curves by many render backends. For cubic non-rational B-splines, which is maybe the
        most common used B-spline, is :meth:`bezier_decomposition` the better choice.

        1. approximation by `level`: an educated guess, the first level of approximation
        segments is based on the count of control points and their distribution along the
        B-spline, every additional level is a subdivision of the previous level.
        E.g. a B-Spline of 8 control points has 7 segments at the first level, 14 at the 2nd level
        and 28 at the 3rd level, a level >= 3 is recommended.

        2. approximation by a given count of evenly distributed approximation segments.

        Args:
            level: subdivision level of approximation segments (ignored if argument ``segments`` != ``None``)
            segments: absolute count of approximation segments

        Returns:
            Yields control points of cubic Bézier curves as :class:`Bezier4P` objects

        """
        if segments is None:
            points = list(self.points(self.approximation_params(level)))
        else:
            points = list(self.approximate(segments))
        from .bezier4p import cubic_bezier_interpolation
        return cubic_bezier_interpolation(points)

    def approximation_params(self, level: int = 3) -> List[float]:
        """ Returns an educated guess, the first level of approximation
        segments is based on the count of control points and their distribution along the
        B-spline, every additional level is a subdivision of the previous level.
        E.g. a B-Spline of 8 control points has 7 segments at the first level, 14 at the 2nd level
        and 28 at the 3rd level.

        """
        params = list(create_t_vector(self.control_points, 'chord'))
        if self.max_t != 1.0:
            max_t = self.max_t
            params = [p * max_t for p in params]
        for _ in range(level - 1):
            params = list(subdivide_params(params))
        return params


def subdivide_params(p: List[float]) -> Iterable[float]:
    for i in range(len(p) - 1):
        yield p[i]
        yield (p[i] + p[i + 1]) / 2.0
    yield p[-1]


class BSplineU(BSpline):
    """ Representation of an uniform (periodic) `B-spline`_ curve (`open curve`_). """

    def __init__(self, control_points: Iterable['Vertex'],
                 order: int = 4,
                 knots: Iterable[float] = None,  # just for consistent interface
                 weights: Iterable[float] = None):
        control_points = list(control_points)
        knots = uniform_knot_vector(len(control_points), order, normalize=False)
        super().__init__(control_points, order=order, knots=knots,
                         weights=weights)

    def step_size(self, segments: int) -> float:
        return float(self.count - self.order + 1) / segments

    def params(self, segments: int) -> Iterable[float]:
        step = self.step_size(segments)
        base = float(self.order - 1)
        for i in range(segments + 1):
            yield base + i * step

    def t_array(self) -> List[float]:
        raise NotImplemented


class BSplineClosed(BSplineU):
    """ Representation of a closed uniform `B-spline`_ curve (`closed curve`_).
    """

    def __init__(self, control_points: Iterable['Vertex'],
                 order: int = 4,
                 knots: Iterable[float] = None,  # just for consistent interface
                 weights: Iterable[float] = None):
        # control points wrap around
        points = list(control_points)
        points.extend(points[:order - 1])
        if weights is not None:
            weights = list(weights)
            weights.extend(weights[:order - 1])
        super().__init__(points, order=order, knots=None, weights=weights)


def rational_spline_from_arc(
        center: Vec3 = (0, 0), radius: float = 1, start_angle: float = 0,
        end_angle: float = 360,
        segments: int = 1) -> BSpline:
    """
    Returns a rational B-splines for a circular 2D arc.

    Args:
        center: circle center as :class:`Vec3` compatible object
        radius: circle radius
        start_angle: start angle in degrees
        end_angle: end angle in degrees
        segments: count of spline segments, at least one segment for each quarter (90 deg), ``1`` for as few as needed.

    .. versionadded:: 0.13

    """
    center = Vec3(center)
    radius = float(radius)
    start_angle = math.radians(start_angle) % math.tau
    end_angle = math.radians(end_angle) % math.tau
    if end_angle == 0:
        end_angle = math.tau
    control_points, weights, knots = nurbs_arc_parameters(start_angle,
                                                          end_angle, segments)
    return BSpline(
        control_points=(center + (p * radius) for p in control_points),
        weights=weights,
        knots=knots,
        order=3,
    )


PI_2 = math.pi / 2.0


def rational_spline_from_ellipse(ellipse: 'ConstructionEllipse',
                                 segments: int = 1) -> BSpline:
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

    def transform_control_points() -> Iterable[Vec3]:
        center = Vec3(ellipse.center)
        x_axis = ellipse.major_axis
        y_axis = ellipse.minor_axis
        for p in control_points:
            yield center + x_axis * p.x + y_axis * p.y

    control_points, weights, knots = nurbs_arc_parameters(start_angle,
                                                          end_angle, segments)
    return BSpline(
        control_points=transform_control_points(),
        weights=weights,
        knots=knots,
        order=3,
    )


def nurbs_arc_parameters(start_angle: float, end_angle: float,
                         segments: int = 1):
    """
    Returns a rational B-spline parameters for a circular 2D arc with center at (0, 0) and a radius of 1.

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians
        segments: count of segments, at least one segment for each quarter (pi/2)

    Returns:
        control_points, weights, knots

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
    control_points = [Vec3(math.cos(start_angle), math.sin(start_angle))]
    weights = [1.0]

    angle = start_angle
    d = 1.0 / math.cos(segment_angle / 2.0)
    for _ in range(arc_count):
        # next control point between points on arc
        angle += segment_angle_2
        control_points.append(Vec3(math.cos(angle) * d, math.sin(angle) * d))
        weights.append(arc_weight)

        # next control point on arc
        angle += segment_angle_2
        control_points.append(Vec3(math.cos(angle), math.sin(angle)))
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
    knots.extend(
        [1.0] * (required_knot_values(len(control_points), 3) - len(knots)))

    return control_points, weights, knots


def bspline_basis(u: float, index: int, degree: int,
                  knots: Sequence[float]) -> float:
    """
    B-spline basis_vector function.

    Simple recursive implementation for testing and comparison.

    Args:
        u: curve parameter in range [0 .. max(knots)]
        index: index of control point
        degree: degree of B-spline
        knots: knots vector

    Returns:
        float: basis_vector value N_i,p(u)

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
                f1 = (u - knots[i]) / dominator * N(i,
                                                    p - 1) if dominator else 0.

                dominator = (knots[i + p + 1] - knots[i + 1])
                f2 = (knots[i + p + 1] - u) / dominator * N(i + 1,
                                                            p - 1) if dominator else 0.

                retval = f1 + f2
            cache[(i, p)] = retval
            return retval

    return N(int(index), int(degree))


def bspline_basis_vector(u: float, count: int, degree: int,
                         knots: Sequence[float]) -> List[float]:
    """
    Create basis_vector vector at parameter u.

    Used with the bspline_basis() for testing and comparison.

    Args:
        u: curve parameter in range [0 .. max(knots)]
        count: control point count (n + 1)
        degree: degree of B-spline (order = degree + 1)
        knots: knot vector

    Returns:
        List[float]: basis_vector vector, len(basis_vector) == count

    """
    assert len(knots) == (count + degree + 1)
    basis = [bspline_basis(u, index, degree, knots) for index in
             range(count)]  # type: List[float]
    if math.isclose(u, knots[
        -1]):  # pick up last point ??? why is this necessary ???
        basis[-1] = 1.
    return basis
