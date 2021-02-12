#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import math
from ezdxf.math import (
    cubic_bezier_arc_parameters, Matrix44, Vertex, basic_transformation,
)
from .path import Path
from . import converter


__all__ = ["unit_circle", "elliptic_transformation", "rect"]


def unit_circle(start_angle: float = 0,
                end_angle: float = math.tau,
                segments: int = 1,
                transform: Matrix44 = None) -> Path:
    """ Returns an unit circle as a :class:`Path` object, with the center at
    (0, 0, 0) and the radius of 1 drawing unit.

    The arc spans from the start- to the end angle in counter clockwise
    orientation. The end angle has to be greater than the start angle and the
    angle span has to be greater than 0.

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians (end_angle > start_angle!)
        segments: count of Bèzier-curve segments, default is one segment for
            each arc quarter (π/2)
        transform: transformation Matrix applied to the unit circle

    """
    path = Path()
    start_flag = True
    for start, ctrl1, ctrl2, end in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        if start_flag:
            path.start = start
            start_flag = False
        path.curve4_to(end, ctrl1, ctrl2)
    if transform is None:
        return path
    else:
        return path.transform(transform)


def elliptic_transformation(
        center: Vertex = (0, 0, 0),
        radius: float = 1,
        ratio: float = 1,
        rotation: float = 0) -> Matrix44:
    """ Returns the transformation matrix to transform an unit circle into
    an arbitrary circular- or elliptic arc.

    Args:
        center: curve center in WCS
        radius: radius of the major axis in drawing units
        ratio: ratio of minor axis to major axis
        rotation: rotation angle about the z-axis in radians

    """
    if radius < 1e-6:
        raise ValueError(f'invalid radius: {radius}')
    if ratio < 1e-6:
        raise ValueError(f'invalid ratio: {ratio}')
    scale_x = radius
    scale_y = radius * ratio
    return basic_transformation(center, (scale_x, scale_y, 1), rotation)


def rect(width: float = 1, height: float = 1,
         transform: Matrix44 = None) -> Path:
    """ Returns a closed rectangle as a :class:`Path` object, with the center at
    (0, 0, 0) and the given `width` and `height` in drawing units.

    Args:
        width: width of the rectangle in drawing units, width > 0
        height: height of the rectangle in drawing units, height > 0
        transform: transformation Matrix applied to the rectangle

    """
    if width < 1e-9:
        raise ValueError(f"invalid width: {width}")
    if height < 1e-9:
        raise ValueError(f"invalid height: {height}")

    w2 = float(width) / 2.0
    h2 = float(height) / 2.0
    path = converter.from_vertices(
        [(w2, h2), (-w2, h2), (-w2, -h2), (w2, h2)],
        close=True
    )
    if transform is None:
        return path
    else:
        return path.transform(transform)
