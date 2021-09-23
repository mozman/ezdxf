# Copyright (c) 2012-2021, Manfred Moitzi
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
    List,
    Iterable,
    Sequence,
    TYPE_CHECKING,
    Dict,
    Tuple,
    Union,
)
import math
from ezdxf.math import (
    Vec3,
    NULLVEC,
    Basis,
    Evaluator,
    create_t_vector,
    estimate_end_tangent_magnitude,
    estimate_tangents,
    LUDecomposition,
    Matrix,
    BandedMatrixLU,
    compact_banded_matrix,
    detect_banded_matrix,
    quadratic_equation,
    linspace,
    distance_point_line_3d,
    arc_angle_span_deg,
)
from ezdxf.lldxf.const import DXFValueError
from ezdxf import PYPY

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex
    from ezdxf.math import (
        ConstructionArc,
        ConstructionEllipse,
        Matrix44,
        Bezier4P,
    )

# Acceleration of banded diagonal matrix solver kicks in at:
# N=15 for CPython on Windows and Linux
# N=60 for pypy3 on Windows and Linux
USE_BANDED_MATRIX_SOLVER_CPYTHON_LIMIT = 15
USE_BANDED_MATRIX_SOLVER_PYPY_LIMIT = 60

__all__ = [
    # High level functions:
    "fit_points_to_cad_cv",
    "global_bspline_interpolation",
    "local_cubic_bspline_interpolation",
    "rational_bspline_from_arc",
    "rational_bspline_from_ellipse",
    "fit_points_to_cubic_bezier",
    "open_uniform_bspline",
    "closed_uniform_bspline",
    # B-spline representation with derivatives support:
    "BSpline",
    # Low level interpolation function:
    "unconstrained_global_bspline_interpolation",
    "global_bspline_interpolation_end_tangents",
    "global_bspline_interpolation_first_derivatives",
    "local_cubic_bspline_interpolation_from_tangents",
    # Low level knot parametrization functions:
    "knots_from_parametrization",
    "averaged_knots_unconstrained",
    "averaged_knots_constrained",
    "natural_knots_unconstrained",
    "natural_knots_constrained",
    "double_knots",
    # Low level knot function:
    "required_knot_values",
    "uniform_knot_vector",
    "open_uniform_knot_vector",
    "required_fit_points",
    "required_control_points",
]


def fit_points_to_cad_cv(
    fit_points: Iterable["Vertex"],
    tangents: Iterable["Vertex"] = None,
    estimate: str = "5-p",
) -> "BSpline":
    """Returns a cubic :class:`BSpline` from fit points as close as possible
    to common CAD applications like BricsCAD.

    There exist infinite numerical correct solution for this setup, but some
    facts are known:

    - Global curve interpolation with start- and end derivatives, e.g. 6 fit points
      creates 8 control vertices in BricsCAD
    - Degree of B-spline is always 3, the stored degree is ignored,
      this is only valid for B-splines defined by fit points
    - Knot parametrization method is "chord"
    - Knot distribution is "natural"

    The last missing parameter is the start- and end tangents estimation method
    used by BricsCAD, if these tangents are stored in the DXF file provide them
    as argument `tangents` as 2-tuple (start, end) and the interpolated control
    vertices will match the BricsCAD calculation, except for floating point
    imprecision.

    If the end tangents are not given, the start- and ent tangent directions
    will be estimated. The argument `estimate` lets choose from different
    estimation methods (first 3 letters are significant):

    - "3-points": 3 point interpolation
    - "5-points": 5 point interpolation
    - "bezier": tangents from an interpolated cubic bezier curve
    - "diff": finite difference

    The estimation method "5-p" yields the closest match to the BricsCAD
    rendering, but sometimes "bez" creates a better result.

    If I figure out how BricsCAD estimates the end tangents directions, the
    argument `estimate` gets an additional value for that case. The existing
    estimation methods will perform the same way as now, except for bug fixes.
    But the default value may change, therefore set argument `estimate` to
    specific value to always get the same result in the future.

    Args:
        fit_points: points the spline is passing through
        tangents: start- and end tangent, default is autodetect
        estimate: tangent direction estimation method

    .. versionchanged:: 0.16
        removed unused arguments `degree` and `method`

    """
    # See also Spline class in ezdxf/entities/spline.py:
    # degree has no effect. A spline with degree=3 is always constructed when
    # interpolating a series of fit points.
    points = Vec3.list(fit_points)
    if len(points) < 2:
        raise ValueError("two ore more points required ")
    m1, m2 = estimate_end_tangent_magnitude(points, method="chord")
    if tangents is None:
        t = estimate_tangents(points, method=estimate, normalize=False)
        start_tangent = t[0].normalize(m1)
        end_tangent = t[-1].normalize(m2)
    else:
        t = Vec3.list(tangents)
        start_tangent = t[0].normalize(m1)
        end_tangent = t[-1].normalize(m2)

    return global_bspline_interpolation(
        points,
        degree=3,
        tangents=(start_tangent, end_tangent),
        method="chord",
    )


def fit_points_to_cubic_bezier(fit_points: Iterable["Vertex"]) -> "BSpline":
    """Returns a cubic :class:`BSpline` from fit points **without** end
    tangents.

    This function uses the cubic Bèzier interpolation to create multiple Bèzier
    curves and combine them into a single B-spline, this works for short simple
    splines better than the :func:`fit_points_to_cad_cv`, but is worse
    for longer and more complex splines.

    Args:
        fit_points: points the spline is passing through

    .. versionadded:: 0.16

    """
    points = Vec3.list(fit_points)
    if len(points) < 2:
        raise ValueError("two ore more points required ")

    from ezdxf.math import cubic_bezier_interpolation, bezier_to_bspline

    bezier_curves = cubic_bezier_interpolation(points)
    return bezier_to_bspline(bezier_curves)


def global_bspline_interpolation(
    fit_points: Iterable["Vertex"],
    degree: int = 3,
    tangents: Iterable["Vertex"] = None,
    method: str = "chord",
) -> "BSpline":
    """`B-spline`_ interpolation by the `Global Curve Interpolation`_.
    Given are the fit points and the degree of the B-spline.
    The function provides 3 methods for generating the parameter vector t:

    - "uniform": creates a uniform t vector, from 0 to 1 evenly spaced, see
      `uniform`_ method
    - "chord", "distance": creates a t vector with values proportional to the
      fit point distances, see `chord length`_ method
    - "centripetal", "sqrt_chord": creates a t vector with values proportional
      to the fit point sqrt(distances), see `centripetal`_ method
    - "arc": creates a t vector with values proportional to the arc length
      between fit points.

    It is possible to constraint the curve by tangents, by start- and end
    tangent if only two tangents are given or by one tangent for each fit point.

    If tangents are given, they represent 1st derivatives and should be
    scaled if they are unit vectors, if only start- and end tangents given the
    function :func:`~ezdxf.math.estimate_end_tangent_magnitude` helps with an
    educated guess, if all tangents are given, scaling by chord length is a
    reasonable choice (Piegl & Tiller).

    Args:
        fit_points: fit points of B-spline, as list of :class:`Vec3` compatible
            objects
        tangents: if only two vectors are given, take the first and the last
            vector as start- and end tangent constraints or if for all fit
            points a tangent is given use all tangents as interpolation
            constraints (optional)
        degree: degree of B-spline
        method: calculation method for parameter vector t

    Returns:
        :class:`BSpline`

    """
    _fit_points = Vec3.list(fit_points)
    count = len(_fit_points)
    order: int = degree + 1

    if tangents:
        # two control points for tangents will be added
        count += 2
    if order > count and tangents is None:
        raise ValueError(f"More fit points required for degree {degree}")

    t_vector = list(create_t_vector(_fit_points, method))
    # natural knot generation for uneven degrees else averaged
    knot_generation_method = "natural" if degree % 2 else "average"
    if tangents is not None:
        _tangents = Vec3.list(tangents)
        if len(_tangents) == 2:
            control_points, knots = global_bspline_interpolation_end_tangents(
                _fit_points,
                _tangents[0],
                _tangents[1],
                degree,
                t_vector,
                knot_generation_method,
            )
        elif len(_tangents) == len(_fit_points):
            (
                control_points,
                knots,
            ) = global_bspline_interpolation_first_derivatives(
                _fit_points, _tangents, degree, t_vector
            )
        else:
            raise ValueError(
                "Invalid count of tangents, two tangents as start- and end "
                "tangent constrains or one tangent for each fit point."
            )
    else:
        control_points, knots = unconstrained_global_bspline_interpolation(
            _fit_points, degree, t_vector, knot_generation_method
        )
    bspline = BSpline(control_points, order=order, knots=knots)
    return bspline


def local_cubic_bspline_interpolation(
    fit_points: Iterable["Vertex"],
    method: str = "5-points",
    tangents: Iterable["Vertex"] = None,
) -> "BSpline":
    """`B-spline`_ interpolation by 'Local Cubic Curve Interpolation', which
    creates B-spline from fit points and estimated tangent direction at start-,
    end- and passing points.

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

    _fit_points = Vec3.list(fit_points)
    if tangents:
        _tangents = Vec3.list(tangents)
    else:
        _tangents = estimate_tangents(_fit_points, method)
    control_points, knots = local_cubic_bspline_interpolation_from_tangents(
        _fit_points, _tangents
    )
    return BSpline(control_points, order=4, knots=knots)


def required_knot_values(count: int, order: int) -> int:
    """Returns the count of required knot values for a B-spline of `order` and
    `count` control points.

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
        raise DXFValueError("Invalid count/order combination")
    # n + p + 2 = count + order
    return n + p + 2


def required_fit_points(order: int, tangents=True) -> int:
    """Returns the count of required fit points to calculate the spline
    control points.

    Args:
        order: spline order (degree + 1)
        tangents: start- and end tangent are given or estimated

    """
    if tangents:
        # If tangents are given or estimated two points for start- and end
        # tangent will be added automatically for the global bspline
        # interpolation. see function fit_points_to_cad_cv()
        order -= 2
    # required condition: order > count, see global_bspline_interpolation()
    return max(order, 2)


def required_control_points(order: int) -> int:
    """Returns the required count of control points for a valid B-spline.

    Args:
        order: spline order (degree + 1)

    Required condition: 2 <= order <= count, therefore:  count >= order

    """
    return max(order, 2)


def normalize_knots(knots: Sequence[float]) -> List[float]:
    """Normalize knot vector into range [0, 1]."""
    min_val = knots[0]
    max_val = knots[-1] - min_val
    return [(v - min_val) / max_val for v in knots]


def uniform_knot_vector(count: int, order: int, normalize=False) -> List[float]:
    """Returns an uniform knot vector for a B-spline of `order` and `count`
    control points.

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


def open_uniform_knot_vector(
    count: int, order: int, normalize=False
) -> List[float]:
    """Returns an open (clamped) uniform knot vector for a B-spline of `order`
    and `count` control points.

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


def knots_from_parametrization(
    n: int, p: int, t: Iterable[float], method="average", constrained=False
) -> List[float]:
    """Returns a 'clamped' knot vector for B-splines. All knot values are
    normalized in the range [0, 1].

    Args:
        n: count fit points - 1
        p: degree of spline
        t: parametrization vector, length(t_vector) == n, normalized [0, 1]
        method: "average", "natural"
        constrained: ``True`` for B-spline constrained by end derivatives

    Returns:
        List of n+p+2 knot values as floats

    """
    order = int(p + 1)
    if order > (n + 1):
        raise DXFValueError(
            "Invalid n/p combination, more fit points required."
        )

    t = [float(v) for v in t]
    if t[0] != 0.0 or t[-1] != 1.0:
        raise ValueError("Parametrization vector t has to be normalized.")

    if method == "average":
        return (
            averaged_knots_constrained(n, p, t)
            if constrained
            else averaged_knots_unconstrained(n, p, t)
        )
    elif method == "natural":
        return (
            natural_knots_constrained(n, p, t)
            if constrained
            else natural_knots_unconstrained(n, p, t)
        )
    else:
        raise ValueError(f"Unknown knot generation method: {method}")


def averaged_knots_unconstrained(
    n: int, p: int, t: Sequence[float]
) -> List[float]:
    """Returns an averaged knot vector from parametrization vector `t` for an
    unconstrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0, 1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(sum(t[j : j + p]) / p for j in range(1, n - p + 1))
    if knots[-1] > 1.0:
        raise ValueError("Normalized [0, 1] values required")
    knots.extend([1.0] * (p + 1))
    return knots


def averaged_knots_constrained(
    n: int, p: int, t: Sequence[float]
) -> List[float]:
    """Returns an averaged knot vector from parametrization vector `t` for a
    constrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0, 1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(sum(t[j : j + p - 1]) / p for j in range(n - p))
    knots.extend([1.0] * (p + 1))
    return knots


def natural_knots_unconstrained(
    n: int, p: int, t: Sequence[float]
) -> List[float]:
    """Returns a 'natural' knot vector from parametrization vector `t` for an
    unconstrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0, 1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(t[2 : n - p + 2])
    knots.extend([1.0] * (p + 1))
    return knots


def natural_knots_constrained(
    n: int, p: int, t: Sequence[float]
) -> List[float]:
    """Returns a 'natural' knot vector from parametrization vector `t` for a
    constrained B-spline.

    Args:
        n: count of control points - 1
        p: degree
        t: parametrization vector, normalized [0, 1]

    """
    assert t[0] == 0.0
    assert t[-1] == 1.0

    knots = [0.0] * (p + 1)
    knots.extend(t[1 : n - p + 1])
    knots.extend([1.0] * (p + 1))
    return knots


def double_knots(n: int, p: int, t: Sequence[float]) -> List[float]:
    """Returns a knot vector from parametrization vector `t` for B-spline
    constrained by first derivatives at all fit points.

    Args:
        n: count of fit points - 1
        p: degree of spline
        t: parametrization vector, first value has to be 0.0 and last value has
            to be 1.0

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
    u.extend(u1[: n * 2 - p])
    u.append((t[-2] + 1.0) / 2.0)  # last knot
    u.extend([1.0] * (p + 1))
    return u


def _get_best_solver(matrix: Union[List, Matrix], degree: int):
    """Returns best suited linear equation solver depending on matrix
    configuration and python interpreter.
    """
    A = matrix if isinstance(matrix, Matrix) else Matrix(matrix=matrix)
    if PYPY:
        limit = USE_BANDED_MATRIX_SOLVER_PYPY_LIMIT
    else:
        limit = USE_BANDED_MATRIX_SOLVER_CPYTHON_LIMIT
    if A.nrows < limit:  # use default equation solver
        return LUDecomposition(A.matrix)
    else:
        # Theory: band parameters m1, m2 are at maximum degree-1, for
        # B-spline interpolation and approximation:
        # m1 = m2 = degree-1
        # But the speed gain is not that big and just to be sure:
        m1, m2 = detect_banded_matrix(A, check_all=False)
        A = compact_banded_matrix(A, m1, m2)
        return BandedMatrixLU(A, m1, m2)


def unconstrained_global_bspline_interpolation(
    fit_points: Sequence["Vertex"],
    degree: int,
    t_vector: Sequence[float],
    knot_generation_method: str = "average",
) -> Tuple[List[Vec3], List[float]]:
    """Interpolates the control points for a B-spline by global interpolation
    from fit points without any constraints.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.2.1

    Args:
        fit_points: points the B-spline has to pass
        degree: degree of spline >= 2
        t_vector: parametrization vector, first value has to be 0 and last
            value has to be 1
        knot_generation_method: knot generation method from parametrization
            vector, "average" or "natural"

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector
        as list of floats

    """
    # Source: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
    knots = knots_from_parametrization(
        len(fit_points) - 1,
        degree,
        t_vector,
        knot_generation_method,
        constrained=False,
    )
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
    knot_generation_method: str = "average",
) -> Tuple[List[Vec3], List[float]]:
    """Interpolates the control points for a B-spline by global interpolation
    from fit points and 1st derivatives for start- and end point as constraints.
    These 'tangents' are 1st derivatives and not unit vectors, if an estimation
    of the magnitudes is required use the :func:`estimate_end_tangent_magnitude`
    function.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.2.2

    Args:
        fit_points: points the B-spline has to pass
        start_tangent: 1st derivative as start constraint
        end_tangent: 1st derivative as end constrain
        degree: degree of spline >= 2
        t_vector: parametrization vector, first value has to be 0 and last
            value has to be 1
        knot_generation_method: knot generation method from parametrization
            vector, "average" or "natural"

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector
        as list of floats

    """
    n = len(fit_points) - 1
    p = degree
    if degree > 3:
        # todo: 'average' produces weird results for degree > 3, 'natural' is
        #  better but also not good
        knot_generation_method = "natural"
    knots = knots_from_parametrization(
        n + 2, p, t_vector, knot_generation_method, constrained=True
    )

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
    t_vector: Sequence[float],
) -> Tuple[List[Vec3], List[float]]:
    """Interpolates the control points for a B-spline by a global
    interpolation from fit points and 1st derivatives as constraints.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.2.4

    Args:
        fit_points: points the B-spline has to pass
        derivatives: 1st derivatives as constrains, not unit vectors!
            Scaling by chord length is a reasonable choice (Piegl & Tiller).
        degree: degree of spline >= 2
        t_vector: parametrization vector, first value has to be 0 and last
            value has to be 1

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector
        as list of floats

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
    B: List[Vec3] = []
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
    fit_points: List[Vec3], tangents: List[Vec3]
) -> Tuple[List[Vec3], List[float]]:
    """Interpolates the control points for a cubic B-spline by local
    interpolation from fit points and tangents as unit vectors for each fit
    point. Use the :func:`estimate_tangents` function to estimate end tangents.

    Source: Piegl & Tiller: "The NURBS Book" - chapter 9.3.4

    Args:
        fit_points: curve definition points - curve has to pass all given fit
            points
        tangents: one tangent vector for each fit point as unit vectors

    Returns:
        2-tuple of control points as list of Vec3 objects and the knot vector
        as list of floats

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


class BSpline:
    """Representation of a `B-spline`_ curve. The default configuration of
    the knot vector is an uniform open `knot`_ vector ("clamped").

    Factory functions:

        - :func:`fit_points_to_cad_cv`
        - :func:`fit_points_to_cubic_bezier`
        - :func:`open_uniform_bspline`
        - :func:`closed_uniform_bspline`
        - :func:`rational_bspline_from_arc`
        - :func:`rational_bspline_from_ellipse`
        - :func:`global_bspline_interpolation`
        - :func:`local_cubic_bspline_interpolation`

    Args:
        control_points: iterable of control points as :class:`Vec3` compatible
            objects
        order: spline order (degree + 1)
        knots: iterable of knot values
        weights: iterable of weight values

    """

    __slots__ = ("_control_points", "_basis", "_clamped")

    def __init__(
        self,
        control_points: Iterable["Vertex"],
        order: int = 4,
        knots: Iterable[float] = None,
        weights: Iterable[float] = None,
    ):
        self._control_points = Vec3.tuple(control_points)
        count = len(self._control_points)
        order = int(order)
        if order > count:
            raise DXFValueError(
                f"Invalid need more control points for order {order}"
            )

        if knots is None:
            knots = open_uniform_knot_vector(count, order, normalize=True)
        else:
            knots = tuple(knots)
            required_knot_count = count + order
            if len(knots) != required_knot_count:
                raise ValueError(
                    f"{required_knot_count} knot values required, got {len(knots)}."
                )
            if knots[0] != 0.0:
                knots = normalize_knots(knots)
        self._basis = Basis(knots, order, count, weights=weights)
        self._clamped = (
            len(set(knots[:order])) == 1 and len(set(knots[-order:])) == 1
        )

    def __str__(self):
        return (
            f"BSpline degree={self.degree}, {self.count} "
            f"control points, {len(self.knots())} knot values, "
            f"{len(self.weights())} weights"
        )

    @property
    def control_points(self) -> Sequence[Vec3]:
        """Control points as tuple of :class:`~ezdxf.math.Vec3`"""
        return self._control_points

    @property
    def count(self) -> int:
        """Count of control points, (n + 1 in text book notation)."""
        return len(self._control_points)

    @property
    def max_t(self) -> float:
        """Biggest `knot`_ value."""
        return self._basis.max_t

    @property
    def order(self) -> int:
        """Order (k) of B-spline = p + 1"""
        return self._basis.order

    @property
    def degree(self) -> int:
        """Degree (p) of B-spline = order - 1"""
        return self._basis.degree

    @property
    def evaluator(self) -> Evaluator:
        return Evaluator(self._basis, self._control_points)

    @property
    def is_rational(self):
        """Returns ``True`` if curve is a rational B-spline. (has weights)"""
        return self._basis.is_rational

    @property
    def is_clamped(self):
        """Returns ``True`` if curve is a clamped (open) B-spline."""
        return self._clamped

    @staticmethod
    def from_fit_points(
        points: Iterable["Vertex"], degree=3, method="chord"
    ) -> "BSpline":
        """Returns :class:`BSpline` defined by fit points."""
        return global_bspline_interpolation(points, degree, method=method)

    @staticmethod
    def ellipse_approximation(
        ellipse: "ConstructionEllipse", num: int = 16
    ) -> "BSpline":
        """Returns an ellipse approximation as :class:`BSpline` with `num`
        control points.

        """
        return global_bspline_interpolation(
            ellipse.vertices(ellipse.params(num)), degree=2
        )

    @staticmethod
    def arc_approximation(arc: "ConstructionArc", num: int = 16) -> "BSpline":
        """Returns an arc approximation as :class:`BSpline` with `num`
        control points.

        """
        return global_bspline_interpolation(
            arc.vertices(arc.angles(num)), degree=2
        )

    @staticmethod
    def from_ellipse(ellipse: "ConstructionEllipse") -> "BSpline":
        """Returns the ellipse as :class:`BSpline` of 2nd degree with as few
        control points as possible.

        """
        return rational_bspline_from_ellipse(ellipse, segments=1)

    @staticmethod
    def from_arc(arc: "ConstructionArc") -> "BSpline":
        """Returns the arc as :class:`BSpline` of 2nd degree with as few control
        points as possible.

        """
        return rational_bspline_from_arc(
            arc.center, arc.radius, arc.start_angle, arc.end_angle, segments=1
        )

    @staticmethod
    def from_nurbs_python_curve(curve) -> "BSpline":
        """Interface to the `NURBS-Python <https://pypi.org/project/geomdl/>`_
        package.

        Returns a :class:`BSpline` object from a :class:`geomdl.BSpline.Curve`
        object.

        """
        return BSpline(
            control_points=curve.ctrlpts,
            order=curve.order,
            knots=curve.knotvector,
            weights=curve.weights,
        )

    def reverse(self) -> "BSpline":
        """Returns a new :class:`BSpline` object with reversed control point
        order.

        """

        def reverse_knots():
            for k in reversed(normalize_knots(self.knots())):
                yield 1.0 - k

        return self.__class__(
            control_points=reversed(self.control_points),
            order=self.order,
            knots=reverse_knots(),
            weights=reversed(self.weights()) if self.is_rational else None,
        )

    def knots(self) -> Tuple[float, ...]:
        """Returns a tuple of `knot`_ values as floats, the knot vector
        **always** has order + count values (n + p + 2 in text book notation).

        """
        return self._basis.knots

    def weights(self) -> Tuple[float, ...]:
        """Returns a tuple of weights values as floats, one for each control
        point or an empty tuple.

        """
        return self._basis.weights

    def approximate(self, segments: int = 20) -> Iterable[Vec3]:
        """Approximates curve by vertices as :class:`Vec3` objects, vertices
        count = segments + 1.

        """
        return self.evaluator.points(self.params(segments))

    def params(self, segments: int) -> Iterable[float]:
        """Yield evenly spaced parameters for given segment count."""
        # works for clamped and unclamped curves
        knots = self.knots()
        lower_bound = knots[self.order - 1]
        upper_bound = knots[self.count]
        return linspace(lower_bound, upper_bound, segments + 1)

    def flattening(self, distance: float, segments: int = 4) -> Iterable[Vec3]:
        """Adaptive recursive flattening. The argument `segments` is the
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
            m = evaluator.point(mid_t)
            try:
                _dist = distance_point_line_3d(m, s, e)
            except ZeroDivisionError:  # s == e
                _dist = 0
            if _dist < distance:
                yield e
            else:
                yield from subdiv(s, m, start_t, mid_t)
                yield from subdiv(m, e, mid_t, end_t)

        evaluator = self.evaluator
        knots = self.knots()
        if self.is_clamped:
            lower_bound = 0.0
        else:
            lower_bound = knots[self.order - 1]
            knots = knots[: self.count + 1]

        knots = tuple(set(knots))  # set() must preserve order!
        t = lower_bound
        start_point = evaluator.point(t)
        yield start_point
        for t1 in knots[1:]:
            delta = (t1 - t) / segments
            while t < t1:
                next_t = t + delta
                if math.isclose(next_t, t1):
                    next_t = t1
                end_point = evaluator.point(next_t)
                yield from subdiv(start_point, end_point, t, next_t)
                t = next_t
                start_point = end_point

    def point(self, t: float) -> Vec3:
        """Returns point  for parameter `t`.

        Args:
            t: parameter in range [0, max_t]

        """
        return self.evaluator.point(t)

    def points(self, t: Iterable[float]) -> Iterable[Vec3]:
        """Yields points for parameter vector `t`.

        Args:
            t: parameters in range [0, max_t]

        """
        return self.evaluator.points(t)

    def derivative(self, t: float, n: int = 2) -> List[Vec3]:
        """Return point and derivatives up to `n` <= degree for parameter `t`.

        e.g. n=1 returns point and 1st derivative.

        Args:
            t: parameter in range [0, max_t]
            n: compute all derivatives up to n <= degree

        Returns:
            n+1 values as :class:`Vec3` objects

        """
        return self.evaluator.derivative(t, n)

    def derivatives(
        self, t: Iterable[float], n: int = 2
    ) -> Iterable[List[Vec3]]:
        """Yields points and derivatives up to `n` <= degree for parameter
        vector `t`.

        e.g. n=1 returns point and 1st derivative.

        Args:
            t: parameters in range [0, max_t]
            n: compute all derivatives up to n <= degree

        Returns:
            List of n+1 values as :class:`Vec3` objects

        """
        return self.evaluator.derivatives(t, n)

    def insert_knot(self, t: float) -> "BSpline":
        """Insert an additional knot, without altering the shape of the curve.
        Returns a new :class:`BSpline` object.

        Args:
            t: position of new knot 0 < t < max_t

        """
        if self._basis.is_rational:
            raise TypeError("Rational B-splines not supported.")

        knots = list(self._basis.knots)
        cpoints = list(self._control_points)
        p = self.degree

        def new_point(index: int) -> Vec3:
            a = (t - knots[index]) / (knots[index + p] - knots[index])
            return cpoints[index - 1] * (1 - a) + cpoints[index] * a

        if t <= 0.0 or t >= self.max_t:
            raise DXFValueError("Invalid position t")

        k = self._basis.find_span(t)
        if k < p:
            raise DXFValueError("Invalid position t")

        cpoints[k - p + 1 : k] = [new_point(i) for i in range(k - p + 1, k + 1)]
        knots.insert(k + 1, t)  # knot[k] <= t < knot[k+1]
        return BSpline(cpoints, self.order, knots)

    def knot_refinement(self, u: Iterable[float]) -> "BSpline":
        """Insert multiple knots, without altering the shape of the curve.
        Returns a new :class:`BSpline` object.

        Args:
            u: vector of new knots t and for each t: 0 < t  < max_t

        """
        spline = self
        for t in u:
            spline = spline.insert_knot(t)
        return spline

    def transform(self, m: "Matrix44") -> "BSpline":
        """Returns a new :class:`BSpline` object transformed by a
        :class:`Matrix44` transformation matrix.

        """
        cpoints = m.transform_vertices(self.control_points)
        return BSpline(cpoints, self.order, self.knots(), self.weights())

    def to_nurbs_python_curve(self):
        """Returns a :class:`geomdl.BSpline.Curve` object, if the
        `NURBS-Python <https://pypi.org/project/geomdl/>`_ package is installed.

        """
        if self._basis.is_rational:
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
        """Decompose a non-rational B-spline into multiple Bézier curves.

        This is the preferred method to represent the most common non-rational
        B-splines of 3rd degree by cubic Bézier curves, which are often supported
        by render backends.

        Returns:
            Yields control points of Bézier curves, each Bézier segment
            has degree+1 control points e.g. B-spline of 3rd degree yields
            cubic Bézier curves of 4 control points.

        """
        # Source: "The NURBS Book": Algorithm A5.6
        if self._basis.is_rational:
            raise TypeError("Rational B-splines not supported.")
        if not self.is_clamped:
            raise TypeError("Clamped B-Spline required.")

        n = self.count - 1
        p = self.degree
        knots = self._basis.knots  # U
        control_points = self._control_points  # Pw
        alphas = [0.0] * len(knots)

        m = n + p + 1
        a = p
        b = p + 1
        bezier_points = list(control_points[0 : p + 1])  # Qw

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
                        bezier_points[k] = bezier_points[
                            k
                        ] * alpha + bezier_points[k - 1] * (1.0 - alpha)
                    if b < m:
                        next_bezier_points[save] = bezier_points[p]
            yield bezier_points

            if b < m:
                for i in range(p - mult, p + 1):
                    next_bezier_points[i] = control_points[b - p + i]
                a = b
                b += 1
                bezier_points = next_bezier_points

    def cubic_bezier_approximation(
        self, level: int = 3, segments: int = None
    ) -> Iterable["Bezier4P"]:
        """Approximate arbitrary B-splines (degree != 3 and/or rational) by
        multiple segments of cubic Bézier curves. The choice of cubic Bézier
        curves is based on the widely support of this curves by many render
        backends. For cubic non-rational B-splines, which is maybe the most
        common used B-spline, is :meth:`bezier_decomposition` the better choice.

        1. approximation by `level`: an educated guess, the first level of
           approximation segments is based on the count of control points
           and their distribution along the B-spline, every additional level
           is a subdivision of the previous level.

        E.g. a B-Spline of 8 control points has 7 segments at the first level,
        14 at the 2nd level and 28 at the 3rd level, a level >= 3 is recommended.

        2. approximation by a given count of evenly distributed approximation
           segments.

        Args:
            level: subdivision level of approximation segments (ignored if
                argument `segments` is not ``None``)
            segments: absolute count of approximation segments

        Returns:
            Yields control points of cubic Bézier curves as :class:`Bezier4P`
            objects

        """
        if segments is None:
            points = list(self.points(self.approximation_params(level)))
        else:
            points = list(self.approximate(segments))
        from .bezier_interpolation import cubic_bezier_interpolation

        return cubic_bezier_interpolation(points)

    def approximation_params(self, level: int = 3) -> List[float]:
        """Returns an educated guess, the first level of approximation
        segments is based on the count of control points and their distribution
        along the B-spline, every additional level is a subdivision of the
        previous level.

        E.g. a B-Spline of 8 control points has 7 segments at the first level,
        14 at the 2nd level and 28 at the 3rd level.

        """
        params = list(create_t_vector(self._control_points, "chord"))
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


def open_uniform_bspline(
    control_points: Iterable["Vertex"],
    order: int = 4,
    weights: Iterable[float] = None,
) -> BSpline:
    """Creates an open uniform (periodic) `B-spline`_ curve (`open curve`_).

    This is an unclamped curve, which means the curve passes none of the
    control points.

    Args:
        control_points: iterable of control points as :class:`Vec3` compatible
            objects
        order: spline order (degree + 1)
        weights: iterable of weight values

    """
    _control_points = Vec3.tuple(control_points)
    knots = uniform_knot_vector(len(_control_points), order, normalize=False)
    return BSpline(control_points, order=order, knots=knots, weights=weights)


def closed_uniform_bspline(
    control_points: Iterable["Vertex"],
    order: int = 4,
    weights: Iterable[float] = None,
) -> BSpline:
    """Creates an closed uniform (periodic) `B-spline`_ curve (`open curve`_).

    This B-spline does not pass any of the control points.

    Args:
        control_points: iterable of control points as :class:`Vec3` compatible
            objects
        order: spline order (degree + 1)
        weights: iterable of weight values

    """
    _control_points = Vec3.list(control_points)
    _control_points.extend(_control_points[: order - 1])
    if weights is not None:
        weights = list(weights)
        weights.extend(weights[: order - 1])
    return open_uniform_bspline(_control_points, order, weights)


def rational_bspline_from_arc(
    center: Vec3 = (0, 0),
    radius: float = 1,
    start_angle: float = 0,
    end_angle: float = 360,
    segments: int = 1,
) -> BSpline:
    """Returns a rational B-splines for a circular 2D arc.

    Args:
        center: circle center as :class:`Vec3` compatible object
        radius: circle radius
        start_angle: start angle in degrees
        end_angle: end angle in degrees
        segments: count of spline segments, at least one segment for each
            quarter (90 deg), default is 1, for as few as needed.

    """
    center = Vec3(center)
    radius = float(radius)

    start_rad = math.radians(start_angle % 360)
    end_rad = start_rad + math.radians(
        arc_angle_span_deg(start_angle, end_angle)
    )
    control_points, weights, knots = nurbs_arc_parameters(
        start_rad, end_rad, segments
    )
    return BSpline(
        control_points=(center + (p * radius) for p in control_points),
        weights=weights,
        knots=knots,
        order=3,
    )


PI_2 = math.pi / 2.0


def rational_bspline_from_ellipse(
    ellipse: "ConstructionEllipse", segments: int = 1
) -> BSpline:
    """Returns a rational B-splines for an elliptic arc.

    Args:
        ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse`
            object
        segments: count of spline segments, at least one segment for each
            quarter (π/2), default is 1, for as few as needed.

    """
    start_angle = ellipse.start_param % math.tau
    end_angle = start_angle + ellipse.param_span

    def transform_control_points() -> Iterable[Vec3]:
        center = Vec3(ellipse.center)
        x_axis = ellipse.major_axis
        y_axis = ellipse.minor_axis
        for p in control_points:
            yield center + x_axis * p.x + y_axis * p.y

    control_points, weights, knots = nurbs_arc_parameters(
        start_angle, end_angle, segments
    )
    return BSpline(
        control_points=transform_control_points(),
        weights=weights,
        knots=knots,
        order=3,
    )


def nurbs_arc_parameters(
    start_angle: float, end_angle: float, segments: int = 1
):
    """Returns a rational B-spline parameters for a circular 2D arc with center
    at (0, 0) and a radius of 1.

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians
        segments: count of segments, at least one segment for each quarter (π/2)

    Returns:
        control_points, weights, knots

    """
    # Source: https://www.researchgate.net/publication/283497458_ONE_METHOD_FOR_REPRESENTING_AN_ARC_OF_ELLIPSE_BY_A_NURBS_CURVE/citation/download
    if segments < 1:
        raise ValueError("Invalid argument segments (>= 1).")
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
        [1.0] * (required_knot_values(len(control_points), 3) - len(knots))
    )

    return control_points, weights, knots


def bspline_basis(
    u: float, index: int, degree: int, knots: Sequence[float]
) -> float:
    """B-spline basis_vector function.

    Simple recursive implementation for testing and comparison.

    Args:
        u: curve parameter in range [0, max(knots)]
        index: index of control point
        degree: degree of B-spline
        knots: knots vector

    Returns:
        float: basis_vector value N_i,p(u)

    """
    cache: Dict[Tuple[int, int], float] = {}
    u = float(u)

    def N(i: int, p: int) -> float:
        try:
            return cache[(i, p)]
        except KeyError:
            if p == 0:
                retval = 1 if knots[i] <= u < knots[i + 1] else 0.0
            else:
                dominator = knots[i + p] - knots[i]
                f1 = (
                    (u - knots[i]) / dominator * N(i, p - 1)
                    if dominator
                    else 0.0
                )

                dominator = knots[i + p + 1] - knots[i + 1]
                f2 = (
                    (knots[i + p + 1] - u) / dominator * N(i + 1, p - 1)
                    if dominator
                    else 0.0
                )

                retval = f1 + f2
            cache[(i, p)] = retval
            return retval

    return N(int(index), int(degree))


def bspline_basis_vector(
    u: float, count: int, degree: int, knots: Sequence[float]
) -> List[float]:
    """Create basis_vector vector at parameter u.

    Used with the bspline_basis() for testing and comparison.

    Args:
        u: curve parameter in range [0, max(knots)]
        count: control point count (n + 1)
        degree: degree of B-spline (order = degree + 1)
        knots: knot vector

    Returns:
        List[float]: basis_vector vector, len(basis_vector) == count

    """
    assert len(knots) == (count + degree + 1)
    basis = [
        bspline_basis(u, index, degree, knots) for index in range(count)
    ]  # type: List[float]
    # pick up last point ??? why is this necessary ???
    if math.isclose(u, knots[-1]):
        basis[-1] = 1.0
    return basis
