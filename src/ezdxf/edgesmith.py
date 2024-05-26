# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
"""
EdgeSmith
=========

A module for creating entities like polylines and hatch boundary paths from linked edges.

The complementary module to ezdxf.edgeminer.

.. versionadded:: 1.4

"""
from __future__ import annotations
from typing import Iterator, Iterable
import math

from ezdxf.edgeminer import Edge, GAP_TOL, ABS_TOL
from ezdxf import entities as et
from ezdxf.math import arc_angle_span_deg, ellipse_param_span, Vec2, Vec3

__all__ = ["is_closed_entity", "edge_from_entity"]


def is_closed_entity(entity: et.DXFEntity) -> bool:
    """Returns ``True`` if the given entity represents a closed loop."""
    if isinstance(entity, et.Arc):  # Arc inherits from Circle!
        radius = abs(entity.dxf.radius)
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        angle_span = arc_angle_span_deg(start_angle, end_angle)
        return abs(radius) > ABS_TOL and math.isclose(
            angle_span, 360.0, abs_tol=ABS_TOL
        )
    if isinstance(entity, et.Circle):
        return abs(entity.dxf.radius) > ABS_TOL

    if isinstance(entity, et.Ellipse):
        start_param = entity.dxf.start_param
        end_param = entity.dxf.end_param
        span = ellipse_param_span(start_param, end_param)
        if not math.isclose(span, math.tau, abs_tol=ABS_TOL):
            return False
        return True

    if isinstance(entity, et.Spline):
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

    if isinstance(entity, et.LWPolyline):
        if len(entity) < 1:
            return False
        if entity.closed is True:
            return True
        start = Vec2(entity.lwpoints[0][:2])
        end = Vec2(entity.lwpoints[-1][:2])
        return start.isclose(end, abs_tol=ABS_TOL)

    if isinstance(entity, et.Polyline):
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


def edge_from_entity(entity: et.DXFEntity, gap_tol=GAP_TOL) -> Edge | None:
    """Makes an :class:`Edge` instance for the DXF entity types LINE, ARC, ELLIPSE and
    SPLINE if the entity is an open linear curve.  Returns ``None`` if the entity
    is a closed curve or cannot represent an edge.
    """
    edge: Edge | None = None

    if isinstance(entity, et.Line):
        start = Vec3(entity.dxf.start)
        end = Vec3(entity.dxf.end)
        length = start.distance(end)
        edge = Edge(start, end, length, entity)
    elif isinstance(entity, et.Arc):
        try:
            ct0 = entity.construction_tool()
        except ValueError:
            return None
        radius = abs(ct0.radius)
        if radius < ABS_TOL:
            return None
        span_deg = arc_angle_span_deg(ct0.start_angle, ct0.end_angle)
        length = radius * span_deg / 180.0 * math.pi
        edge = Edge(ct0.start_point, ct0.end_point, length, entity)
    elif isinstance(entity, et.Ellipse):
        try:
            ct1 = entity.construction_tool()
        except ValueError:
            return None
        if ct1.major_axis.magnitude < ABS_TOL or ct1.minor_axis.magnitude < ABS_TOL:
            return None
        span = ellipse_param_span(ct1.start_param, ct1.end_param)
        num = max(3, round(span / 0.1745))  #  resolution of ~1 deg
        # length of elliptic arc is an approximation:
        points = list(ct1.vertices(ct1.params(num)))
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = Edge(Vec3(points[0]), Vec3(points[-1]), length, entity)
    elif isinstance(entity, et.Spline):
        try:
            ct2 = entity.construction_tool()
        except ValueError:
            return None
        start = Vec3(ct2.control_points[0])
        end = Vec3(ct2.control_points[-1])
        points = list(ct2.control_points)
        # length of B-spline is a very rough approximation:
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = Edge(start, end, length, entity)

    if isinstance(edge, Edge):
        if edge.start.distance(edge.end) < gap_tol:
            return None
        if edge.length < gap_tol:
            return None
    return edge


def edges_from_entities(
    entities: Iterable[et.DXFEntity], gap_tol=GAP_TOL
) -> Iterator[Edge]:
    """Yields all DXF entities as edges. 
    
    Skips all entities which can not be represented as edge.
    """
    for entity in entities:
        edge = edge_from_entity(entity, gap_tol)
        if edge is not None:
            yield edge
