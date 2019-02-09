# Purpose: math and construction tools
# Created: 27.03.2010, 2018 integrated into ezdxf
# Copyright (c) 2010-2019 Manfred Moitzi
# License: MIT License
from .construct2d import is_close_points
from .vector import Vector, X_AXIS, Y_AXIS, Z_AXIS
from .matrix44 import Matrix44
from .matrix import Matrix
from .bspline import bspline_control_frame, bspline_control_frame_approx
from .bspline import BSpline, BSplineU, BSplineClosed, DBSpline, DBasisU, DBSplineClosed
from .bezier import Bezier, DBezier
from .bezier4p import Bezier4P
from .ucs import OCS, UCS, PassTroughUCS
from .bulge import bulge_to_arc, bulge_3_points, bulge_center, bulge_radius, arc_to_bulge
from .arc import ConstructionArc
from .line import ConstructionRay, ConstructionLine
from .circle import ConstructionCircle
from .box import ConstructionBox
from .convexhull import convex_hull_2d
from .points import closest_point


def xround(value: float, rounding: float = 0.) -> float:
    """
    Extended rounding.

    `rounding` defines the rounding limit:
        - 0 = remove fraction
        - 0.1 = round next to x.1, x.2, ... x.0
        - 0.25 = round next to x.25, x.50, x.75 or x.00
        - 0.5 = round next to x.5 or x.0
        - 1. = round to a multiple of 1: remove fraction
        - 2. = round to a multiple of 2: xxx2, xxx4, xxx6 ...
        - 5. = round to a multiple of 5: xxx5 or xxx0
        - 10. = round to a multiple of 10: xx10, xx20, ...

    Args:
        value: float value to round
        rounding: rounding limit

    """
    if rounding == 0:
        return round(value)
    factor = 1. / rounding
    return round(value * factor) / factor