# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
import math

from ezdxf.entities import DXFEntity, Circle, Arc, Ellipse, Spline, LWPolyline, Polyline
from ezdxf.math import arc_angle_span_deg, ellipse_param_span, Vec2, Vec3

__all__ = ["is_closed_entity"]

ABS_TOL = 1e-12


def is_closed_entity(entity: DXFEntity) -> bool:
    """Returns ``True`` if the given entity represents a closed loop.
    """
    if isinstance(entity, Arc):  # Arc is inherits from Circle!
        radius = abs(entity.dxf.radius)
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        angle_span = arc_angle_span_deg(start_angle, end_angle)
        return abs(radius) > ABS_TOL and math.isclose(
            angle_span, 360.0, abs_tol=ABS_TOL
    
        )
    if isinstance(entity, Circle):
        return abs(entity.dxf.radius) > ABS_TOL
    
    if isinstance(entity, Ellipse):
        start_param = entity.dxf.start_param
        end_param = entity.dxf.end_param
        span = ellipse_param_span(start_param, end_param)
        if not math.isclose(span, math.tau, abs_tol=ABS_TOL):
            return False
        return True
    
    if isinstance(entity, Spline):
        try:
            bspline = entity.construction_tool()
        except ValueError:
            return False
        control_points = bspline.control_points
        if len(control_points) < 3:
            return False
        start = control_points[0]
        end = control_points[-1]
        return start.isclose(end, abs_tol=ABS_TOL)
    
    if isinstance(entity, LWPolyline):
        if len(entity) < 1:
            return False
        if entity.closed is True:
            return True
        start = Vec2(entity.lwpoints[0][:2])
        end = Vec2(entity.lwpoints[-1][:2])
        return start.isclose(end, abs_tol=ABS_TOL)

    if isinstance(entity, Polyline):
        if entity.is_2d_polyline or entity.is_3d_polyline:
            # Note: does not check if all vertices of a 3D polyline are placed on a 
            # common plane.
            vertices = entity.vertices
            if len(vertices) < 2:
                return False
            if entity.is_closed:
                return True
            p0: Vec3 = vertices[0].dxf.location  # type: ignore
            p1: Vec3 = vertices[-1].dxf.location  # type: ignore
            if p0.isclose(p1, abs_tol=ABS_TOL):
                return True
        return False
    return False
