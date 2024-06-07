# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
"""
EdgeSmith
=========

A module for creating entities like polylines and hatch boundary paths from linked edges.

The complementary module to ezdxf.edgeminer.

.. important::
    
    THIS MODULE IS WORK IN PROGRESS (ALPHA VERSION), EVERYTHING CAN CHANGE UNTIL 
    THE RELEASE IN EZDXF V1.4.

"""
from __future__ import annotations
from typing import Iterator, Iterable, Sequence, Any
import math

from ezdxf import edgeminer as em
from ezdxf import entities as et
from ezdxf.math import (
    Vec2,
    Vec3,
    arc_angle_span_deg,
    ellipse_param_span,
    bulge_from_radius_and_chord,
    bulge_from_arc_angle,
)

__all__ = [
    "chain_vertices",
    "edge_from_entity",
    "edges_from_entities",
    "is_closed_entity",
    "polyline_from_chain",
]
# Tolerances
LEN_TOL = 1e-9  # length and distance
DEG_TOL = 1e-9  # angles in degree
RAD_TOL = 1e-9  # angles in radians


def is_closed_entity(entity: et.DXFEntity) -> bool:
    """Returns ``True`` if the given entity represents a closed loop."""
    if isinstance(entity, et.Arc):  # Arc inherits from Circle!
        radius = abs(entity.dxf.radius)
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        angle_span = arc_angle_span_deg(start_angle, end_angle)
        return abs(radius) > LEN_TOL and math.isclose(
            angle_span, 360.0, abs_tol=LEN_TOL
        )
    if isinstance(entity, et.Circle):
        return abs(entity.dxf.radius) > LEN_TOL

    if isinstance(entity, et.Ellipse):
        start_param = entity.dxf.start_param
        end_param = entity.dxf.end_param
        span = ellipse_param_span(start_param, end_param)
        if not math.isclose(span, math.tau, abs_tol=RAD_TOL):
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
        return start.isclose(end, abs_tol=LEN_TOL)

    if isinstance(entity, et.LWPolyline):
        if len(entity) < 1:
            return False
        if entity.closed is True:
            return True
        start = Vec2(entity.lwpoints[0][:2])
        end = Vec2(entity.lwpoints[-1][:2])
        return start.isclose(end, abs_tol=LEN_TOL)

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
            if p0.isclose(p1, abs_tol=LEN_TOL):
                return True
        return False
    return False


def edge_from_entity(entity: et.DXFEntity, gap_tol=em.GAP_TOL) -> em.Edge | None:
    """Makes an :class:`Edge` instance for the DXF entity types LINE, ARC, ELLIPSE and
    SPLINE if the entity is an open linear curve.  Returns ``None`` if the entity
    is a closed curve or cannot represent an edge.
    """
    edge: em.Edge | None = None

    if isinstance(entity, et.Line):
        start = Vec3(entity.dxf.start)
        end = Vec3(entity.dxf.end)
        length = start.distance(end)
        edge = em.make_edge(start, end, length, payload=entity)
    elif isinstance(entity, et.Arc):
        radius = abs(entity.dxf.radius)
        if radius < LEN_TOL:
            return None
        start_angle = entity.dxf.start_angle
        end_angle = entity.dxf.end_angle
        span_deg = arc_angle_span_deg(start_angle, end_angle)
        length = radius * span_deg / 180.0 * math.pi
        sp, ep = entity.vertices((start_angle, end_angle))
        edge = em.make_edge(sp, ep, length, payload=entity)
    elif isinstance(entity, et.Ellipse):
        try:
            ct1 = entity.construction_tool()
        except ValueError:
            return None
        if ct1.major_axis.magnitude < LEN_TOL or ct1.minor_axis.magnitude < LEN_TOL:
            return None
        span = ellipse_param_span(ct1.start_param, ct1.end_param)
        num = max(3, round(span / 0.1745))  #  resolution of ~1 deg
        # length of elliptic arc is an approximation:
        points = list(ct1.vertices(ct1.params(num)))
        length = sum(a.distance(b) for a, b in zip(points, points[1:]))
        edge = em.make_edge(Vec3(points[0]), Vec3(points[-1]), length, payload=entity)
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
        edge = em.make_edge(start, end, length, payload=entity)

    if isinstance(edge, em.Edge):
        if edge.start.distance(edge.end) < gap_tol:
            return None
        if edge.length < gap_tol:
            return None
    return edge


def edges_from_entities(
    entities: Iterable[et.DXFEntity], gap_tol=em.GAP_TOL
) -> Iterator[em.Edge]:
    """Yields all DXF entities as edges.

    Skips all entities which can not be represented as edge.
    """
    for entity in entities:
        edge = edge_from_entity(entity, gap_tol)
        if edge is not None:
            yield edge


def chain_vertices(edges: Sequence[em.Edge], gap_tol=em.GAP_TOL) -> Sequence[Vec3]:
    """Returns all vertices from a sequence of connected edges.

    Adds line segments between edges when the gap is bigger than `gap_tol`.
    """
    if not edges:
        return tuple()
    vertices: list[Vec3] = [edges[0].start]
    for edge in edges:
        if not em.isclose(vertices[-1], edge.start, gap_tol):
            vertices.append(edge.start)
        vertices.append(edge.end)
    return vertices


def polyline_from_chain(
    edges: Sequence[em.Edge], dxfattribs: Any = None
) -> et.LWPolyline:
    """Returns a new virtual :class:`LWPolyline` entity.

    This function assumes the building blocks as simple DXF entities attached as payload
    to the edges.  The edges are processed in order of the input sequence.

        - LINE entities are added as line segments
        - ARC entities are added as bulges
        - ELLIPSE entities with a ratio of 1.0 are added as bulges
        - Everything else will be added as line segment from Edge.start to Edge.end
        - Gaps between edges are connected by line segments.

    """
    # bulge value is stored in the start vertex of the curved segment
    polyline = et.LWPolyline.new(dxfattribs=dxfattribs)
    if len(edges) == 0:
        return polyline
    points: list[Vec3] = [edges[0].start]
    bulges: list[float] = [0.0]
    for edge in edges:
        current_end = points[-1]
        if not edge.start.isclose(current_end):
            current_end = edge.start
            points.append(current_end)
            bulges.append(0.0)
        entity = edge.payload
        if isinstance(entity, et.Arc):
            span = arc_angle_span_deg(entity.dxf.start_angle, entity.dxf.end_angle)
            if span > DEG_TOL:
                bulge = bulge_from_arc_angle(math.radians(span))
                bulges[-1] = -bulge if edge.is_reverse else bulge         
        elif isinstance(entity, et.Ellipse):
            ratio = abs(entity.dxf.ratio)
            span = ellipse_param_span(entity.dxf.start_param, entity.dxf.end_param)
            if math.isclose(ratio, 1.0) and span > RAD_TOL:
                bulge = bulge_from_arc_angle(span)
                bulges[-1] = -bulge if edge.is_reverse else bulge 
        points.append(edge.end)
        bulges.append(0.0)
    polyline = et.LWPolyline.new(dxfattribs=dxfattribs)
    polyline.set_points(zip(points, bulges), format="vb")  # type: ignore
    return polyline
