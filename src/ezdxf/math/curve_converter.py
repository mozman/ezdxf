#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Union

from ezdxf.math import BSpline, fit_points_to_cad_cv
from ezdxf.math import Bezier4P, Bezier3P

__all__ = ["bezier_to_bspline", "quadratic_to_cubic_bezier"]

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
