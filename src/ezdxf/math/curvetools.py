#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Union
import math
from ezdxf.math import BSpline, fit_points_to_cad_cv
from ezdxf.math import Bezier4P, Bezier3P

__all__ = [
    "bezier_to_bspline", "quadratic_to_cubic_bezier",
    "have_bezier_curves_g1_continuity", "AnyBezier"
]

AnyBezier = Union[Bezier3P, Bezier4P]


def quadratic_to_cubic_bezier(curve: Bezier3P) -> Bezier4P:
    """ Convert quadratic Bèzier curves (:class:`ezdxf.math.Bezier3P`) into
    cubic Bèzier curves (:class:`ezdxf.math.Bezier4P`).

    .. versionadded: 0.16

    """
    start, control, end = curve.control_points
    control_1 = start + 2 * (control - start) / 3
    control_2 = end + 2 * (control - end) / 3
    return Bezier4P((start, control_1, control_2, end))


def bezier_to_bspline(curves: Iterable[AnyBezier],
                      segments: int = 3) -> BSpline:
    """ Convert multiple Bèzier curves into a cubic B-splines
    (:class:`ezdxf.math.BSpline`).
    The curves must be lined up seamlessly, i.e. the starting point of the
    following curve must be the same as the end point of the previous curve.

    .. versionadded: 0.16

    """
    curves = list(curves)
    if len(curves) == 0:
        raise ValueError('one or more Bézier curves required')
    first = curves[0].control_points
    start_tangent = first[1] - first[0]
    last = curves[-1].control_points
    end_tangent = last[-1] - last[-2]
    fit_points = [first[0]]
    for curve in curves:
        points = curve.control_points
        if points[0].isclose(fit_points[-1]):
            approx = list(curve.approximate(segments))
            fit_points.extend(approx[1:])
        else:
            raise ValueError('gap between curves')
    return fit_points_to_cad_cv(
        fit_points, tangents=[start_tangent, end_tangent])


def have_bezier_curves_g1_continuity(b1: AnyBezier, b2: AnyBezier,
                                     g1_tol: float = 1e-4) -> bool:
    """ Return ``True`` if the given adjacent bezier curves have G1 continuity.
    """
    b1_pnts = list(b1.control_points)
    b2_pnts = list(b2.control_points)
    if not b1_pnts[-1].isclose(b2_pnts[0]):
        return False
    te = (b1_pnts[-1] - b1_pnts[-2]).normalize()
    ts = (b2_pnts[1] - b2_pnts[0]).normalize()
    # 0 = normal; 1 = same direction; -1 = opposite direction
    return math.isclose(te.dot(ts), 1.0, abs_tol=g1_tol)
