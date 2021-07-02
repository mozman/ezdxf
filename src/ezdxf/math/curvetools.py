#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Union, List
import math
from ezdxf.math import BSpline, Bezier4P, Bezier3P

__all__ = [
    "bezier_to_bspline",
    "quadratic_to_cubic_bezier",
    "have_bezier_curves_g1_continuity",
    "AnyBezier",
    "reverse_bezier_curves",
]

AnyBezier = Union[Bezier3P, Bezier4P]


def quadratic_to_cubic_bezier(curve: Bezier3P) -> Bezier4P:
    """Convert quadratic Bèzier curves (:class:`ezdxf.math.Bezier3P`) into
    cubic Bèzier curves (:class:`ezdxf.math.Bezier4P`).

    .. versionadded: 0.16

    """
    start, control, end = curve.control_points
    control_1 = start + 2 * (control - start) / 3
    control_2 = end + 2 * (control - end) / 3
    return Bezier4P((start, control_1, control_2, end))


def bezier_to_bspline(curves: Iterable[AnyBezier]) -> BSpline:
    """Convert multiple quadratic or cubic Bèzier curves into a single cubic
    B-spline (:class:`ezdxf.math.BSpline`).
    For good results the curves must be lined up seamlessly, i.e. the starting
    point of the following curve must be the same as the end point of the
    previous curve. G1 continuity or better at the connection points of the
    Bézier curves is required to get best results.

    .. versionadded: 0.16

    """

    # Source: https://math.stackexchange.com/questions/2960974/convert-continuous-bezier-curve-to-b-spline
    def get_points(bezier: AnyBezier):
        points = bezier.control_points
        if len(points) < 4:
            return quadratic_to_cubic_bezier(bezier).control_points
        else:
            return points

    bezier_curve_points = [get_points(c) for c in curves]
    if len(bezier_curve_points) == 0:
        raise ValueError("one or more Bézier curves required")
    # Control points of the B-spline are the same as of the Bézier curves.
    # Remove duplicate control points at start and end of the curves.
    control_points = list(bezier_curve_points[0])
    for c in bezier_curve_points[1:]:
        control_points.extend(c[1:])
    knots = [0, 0, 0, 0]  # multiplicity of the 1st and last control point is 4
    n = len(bezier_curve_points)
    for k in range(1, n):
        knots.extend((k, k, k))  # multiplicity of the inner control points is 3
    knots.extend((n, n, n, n))
    return BSpline(control_points, order=4, knots=knots)


def have_bezier_curves_g1_continuity(
    b1: AnyBezier, b2: AnyBezier, g1_tol: float = 1e-4
) -> bool:
    """Return ``True`` if the given adjacent bezier curves have G1 continuity.

    .. versionadded: 0.16

    """
    b1_pnts = tuple(b1.control_points)
    b2_pnts = tuple(b2.control_points)

    if not b1_pnts[-1].isclose(b2_pnts[0]):
        return False  # start- and end point are not close enough

    try:
        te = (b1_pnts[-1] - b1_pnts[-2]).normalize()
    except ZeroDivisionError:
        return False  # tangent calculation not possible

    try:
        ts = (b2_pnts[1] - b2_pnts[0]).normalize()
    except ZeroDivisionError:
        return False  # tangent calculation not possible

    # 0 = normal; 1 = same direction; -1 = opposite direction
    return math.isclose(te.dot(ts), 1.0, abs_tol=g1_tol)


def reverse_bezier_curves(curves: List[AnyBezier]) -> List[AnyBezier]:
    curves = list(c.reverse() for c in curves)
    curves.reverse()
    return curves
