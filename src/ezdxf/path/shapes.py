#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
import math
from ezdxf.math import (
    cubic_bezier_arc_parameters, Matrix44, Vertex, basic_transformation,
)
from ezdxf.render import forms
from .path import Path
from . import converter

__all__ = [
    "unit_circle", "elliptic_transformation", "rect", "ngon", "wedge", "star",
    "gear"
]


def unit_circle(
        start_angle: float = 0,
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


def wedge(start_angle: float,
          end_angle: float,
          segments: int = 1,
          transform: Matrix44 = None) -> Path:
    """ Returns a wedge as a :class:`Path` object, with the center at
    (0, 0, 0) and the radius of 1 drawing unit.

    The arc spans from the start- to the end angle in counter clockwise
    orientation. The end angle has to be greater than the start angle and the
    angle span has to be greater than 0.

    Args:
        start_angle: start angle in radians
        end_angle: end angle in radians (end_angle > start_angle!)
        segments: count of Bèzier-curve segments, default is one segment for
            each arc quarter (π/2)
        transform: transformation Matrix applied to the wedge

    """
    path = Path()
    start_flag = True
    for start, ctrl1, ctrl2, end in cubic_bezier_arc_parameters(
            start_angle, end_angle, segments):
        if start_flag:
            path.line_to(start)
            start_flag = False
        path.curve4_to(end, ctrl1, ctrl2)
    path.line_to((0, 0, 0))
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

    Example how to create an ellipse with an major axis length of 3, a minor
    axis length 1.5 and rotated about 90°::

        m = elliptic_transformation(radius=3, ratio=0.5, rotation=math.pi / 2)
        ellipse = shapes.unit_circle(transform=m)

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


def ngon(count: int, length: float = None, radius: float = 1.0,
         transform: Matrix44 = None) -> Path:
    """ Returns a `regular polygon <https://en.wikipedia.org/wiki/Regular_polygon>`_
    a :class:`Path` object, with the center at (0, 0, 0).
    The polygon size is determined by the edge `length` or the circum `radius`
    argument. If both are given `length` has higher priority. Default size is
    a `radius` of 1. The ngon starts with the first vertex is on the x-axis!
    The base geometry is created by function :func:`ezdxf.render.forms.ngon`.

    Args:
        count: count of polygon corners >= 3
        length: length of polygon side
        radius: circum radius, default is 1
        transform: transformation Matrix applied to the ngon

    """
    vertices = forms.ngon(count, length=length, radius=radius)
    if transform is not None:
        vertices = transform.transform_vertices(vertices)
    return converter.from_vertices(vertices, close=True)


def star(count: int, r1: float, r2: float, transform: Matrix44 = None) -> Path:
    """ Returns a `star shape <https://en.wikipedia.org/wiki/Star_polygon>`_ as
    a :class:`Path` object, with the center at (0, 0, 0).

    Argument `count` defines the count of star spikes, `r1` defines the radius
    of the "outer" vertices and `r2` defines the radius of the "inner" vertices,
    but this does not mean that `r1` has to be greater than `r2`.
    The star shape starts with the first vertex is on the x-axis!
    The base geometry is created by function :func:`ezdxf.render.forms.star`.

    Args:
        count: spike count >= 3
        r1: radius 1
        r2: radius 2
        transform: transformation Matrix applied to the star

    """
    vertices = forms.star(count, r1=r1, r2=r2)
    if transform is not None:
        vertices = transform.transform_vertices(vertices)
    return converter.from_vertices(vertices, close=True)


def gear(count: int, top_width: float, bottom_width: float, height: float,
         outside_radius: float, transform: Matrix44 = None) -> Path:
    """
    Returns a `gear <https://en.wikipedia.org/wiki/Gear>`_ (cogwheel) shape as
    a :class:`Path` object, with the center at (0, 0, 0).
    The base geometry is created by function :func:`ezdxf.render.forms.gear`.

    .. warning::

        This function does not create correct gears for mechanical engineering!

    Args:
        count: teeth count >= 3
        top_width: teeth width at outside radius
        bottom_width: teeth width at base radius
        height: teeth height; base radius = outside radius - height
        outside_radius: outside radius
        transform: transformation Matrix applied to the gear shape

    """
    vertices = forms.gear(count, top_width, bottom_width, height,
                          outside_radius)
    if transform is not None:
        vertices = transform.transform_vertices(vertices)
    return converter.from_vertices(vertices, close=True)
