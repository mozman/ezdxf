# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
import math
from collections import namedtuple
from .vector import Vector
from .matrix44 import Matrix44
from .construct2d import rytz_axis_construction

EllipseParams = namedtuple('EllipseParams', 'center major_axis minor_axis extrusion ratio start_param end_param')
pi2 = math.pi / 2


def transform(m: Matrix44, center: Vector, major_axis: Vector, extrusion: Vector, ratio: float,
              start_param: float, end_param: float) -> EllipseParams:
    new_center = m.transform(center)
    old_start_param = start_param = start_param % math.tau
    old_end_param = end_param = end_param % math.tau
    old_minor_axis = minor_axis(major_axis, extrusion, ratio)
    new_major_axis, new_minor_axis = m.transform_directions((major_axis, old_minor_axis))

    # Original ellipse parameters stay untouched until end of transformation
    if not math.isclose(new_major_axis.dot(new_minor_axis), 0, abs_tol=1e-9):
        new_major_axis, new_minor_axis, new_ratio = rytz_axis_construction(new_major_axis, new_minor_axis)
        adjust_params = True
    else:
        new_ratio = new_minor_axis.magnitude / new_major_axis.magnitude
        adjust_params = False

    if adjust_params and not math.isclose(start_param, end_param, abs_tol=1e-9):
        # open ellipse, adjusting start- and end parameter
        x_axis = new_major_axis.normalize()
        y_axis = new_minor_axis.normalize()
        old_param_span = (end_param - start_param) % math.tau

        def param(vec: 'Vector') -> float:
            dy = y_axis.dot(vec) / new_ratio  # adjust to circle
            dx = x_axis.dot(vec)
            return math.atan2(dy, dx) % math.tau

        # transformed start- and end point of old ellipse
        start_point = m.transform(vertex(start_param, major_axis, old_minor_axis, center, ratio))
        end_point = m.transform(vertex(end_param, major_axis, old_minor_axis, center, ratio))

        start_param = param(start_point - new_center)
        end_param = param(end_point - new_center)

        # Test if drawing the correct side of the curve
        if not math.isclose(old_param_span, math.pi, abs_tol=1e-9):
            # equal param span check works well, except for a span of exact pi (180 deg)
            new_param_span = (end_param - start_param) % math.tau
            if not math.isclose(old_param_span, new_param_span, abs_tol=1e-9):
                start_param, end_param = end_param, start_param
        else:  # param span is exact pi (180 deg)
            # expensive but it seem to work:
            old_chk_point = m.transform(vertex(
                mid_param(old_start_param, old_end_param),
                major_axis,
                old_minor_axis,
                center,
                ratio,
            ))
            new_chk_point = vertex(
                mid_param(start_param, end_param),
                new_major_axis,
                new_minor_axis,
                new_center,
                new_ratio,
            )
            if not old_chk_point.isclose(new_chk_point, abs_tol=1e-9):
                start_param, end_param = end_param, start_param

    new_extrusion = new_major_axis.cross(new_minor_axis).normalize()
    if new_ratio > 1:
        new_major_axis = minor_axis(new_major_axis, new_extrusion, new_ratio)
        new_ratio = 1.0 / new_ratio
        new_minor_axis = minor_axis(new_major_axis, new_extrusion, new_ratio)
        if not (math.isclose(start_param, 0) and math.isclose(end_param, math.tau)):
            start_param -= pi2
            end_param -= pi2

    return EllipseParams(
        new_center,
        new_major_axis,
        new_minor_axis,
        new_extrusion,
        max(new_ratio, 1e-6),
        start_param % math.tau,
        end_param % math.tau,
    )


def mid_param(start: float, end: float) -> float:
    if end < start:
        end += math.tau
    return (start + end) / 2.0


def minor_axis(major_axis: Vector, extrusion: Vector, ratio: float) -> Vector:
    return extrusion.cross(major_axis).normalize(major_axis.magnitude * ratio)


def vertex(param: float, major_axis: Vector, minor_axis: Vector, center: Vector, ratio: float) -> Vector:
    x_axis = major_axis.normalize()
    y_axis = minor_axis.normalize()
    radius_x = major_axis.magnitude
    radius_y = radius_x * ratio
    x = math.cos(param) * radius_x * x_axis
    y = math.sin(param) * radius_y * y_axis
    return center + x + y
