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
from typing_extensions import TypeAlias
import math
import functools

from ezdxf import edgeminer as em
from ezdxf import entities as et
from ezdxf import path
from ezdxf.entities import boundary_paths as bp

from ezdxf.math import (
    Vec2,
    Vec3,
    arc_angle_span_deg,
    ellipse_param_span,
    bulge_from_arc_angle,
    Z_AXIS,
    Matrix44,
)

__all__ = [
    "chain_vertices",
    "edge_path_from_chain",
    "edges_from_entities_2d",
    "is_closed_entity",
    "lwpolyline_from_chain",
    "make_edge_2d",
    "path2d_from_chain",
    "polyline2d_from_chain",
    "polyline_path_from_chain",
]
# Tolerances
LEN_TOL = 1e-9  # length and distance
DEG_TOL = 1e-9  # angles in degree
RAD_TOL = 1e-7  # angles in radians
GAP_TOL = em.GAP_TOL


# noinspection PyUnusedLocal
@functools.singledispatch
def is_closed_entity(entity: et.DXFEntity) -> bool:
    """Returns ``True`` if the given entity represents a closed loop."""
    return False


@is_closed_entity.register(et.Arc)
def _is_closed_arc(entity: et.Arc) -> bool:
    radius = abs(entity.dxf.radius)
    start_angle = entity.dxf.start_angle
    end_angle = entity.dxf.end_angle
    angle_span = arc_angle_span_deg(start_angle, end_angle)
    return abs(radius) > LEN_TOL and math.isclose(angle_span, 360.0, abs_tol=LEN_TOL)


@is_closed_entity.register(et.Circle)
def _is_closed_circle(entity: et.Circle) -> bool:
    return abs(entity.dxf.radius) > LEN_TOL


@is_closed_entity.register(et.Ellipse)
def _is_closed_ellipse(entity: et.Ellipse) -> bool:
    start_param = entity.dxf.start_param
    end_param = entity.dxf.end_param
    span = ellipse_param_span(start_param, end_param)
    if not math.isclose(span, math.tau, abs_tol=RAD_TOL):
        return False
    return True


@is_closed_entity.register(et.Spline)
def _is_closed_spline(entity: et.Spline) -> bool:
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


@is_closed_entity.register(et.LWPolyline)
def _is_closed_lwpolyline(entity: et.LWPolyline) -> bool:
    if len(entity) < 1:
        return False
    if entity.closed is True:
        return True
    start = Vec2(entity.lwpoints[0][:2])
    end = Vec2(entity.lwpoints[-1][:2])
    return start.isclose(end, abs_tol=LEN_TOL)


@is_closed_entity.register(et.Polyline)
def _is_closed_polyline2d(entity: et.Polyline) -> bool:
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


def _validate_edge(edge: em.Edge, gap_tol: float) -> em.Edge | None:
    if edge.start.distance(edge.end) < gap_tol:
        return None
    if edge.length < gap_tol:
        return None
    return edge


# noinspection PyUnusedLocal
@functools.singledispatch
def make_edge_2d(entity: et.DXFEntity, gap_tol=GAP_TOL) -> em.Edge | None:
    """Makes an :class:`Edge` instance from the following DXF entity types:

        - :class:`~ezdxf.entities.Line` (length accurate)
        - :class:`~ezdxf.entities.Arc` (length accurate)
        - :class:`~ezdxf.entities.Ellipse` (length approximated)
        - :class:`~ezdxf.entities.Spline` (length approximated as straight lines between
          control points)
        - :class:`~ezdxf.entities.LWPolyline` (length of bulges as straight line from
          start- to end point)
        - :class:`~ezdxf.entities.Polyline` (length of bulges as straight line from
          start- to end point)

    The start- and end points of the edge is projected onto the xy-plane. Returns
    ``None`` if the entity has a closed shape or cannot be represented as an edge.
    """
    return None


@make_edge_2d.register(et.Line)
def _edge_from_line(entity: et.Line, gap_tol=GAP_TOL) -> em.Edge | None:
    # line projected onto the xy-plane
    start = Vec2(entity.dxf.start)
    end = Vec2(entity.dxf.end)
    length = start.distance(end)
    return _validate_edge(em.make_edge(start, end, length, payload=entity), gap_tol)


@make_edge_2d.register(et.Arc)
def _edge_from_arc(entity: et.Arc, gap_tol=GAP_TOL) -> em.Edge | None:
    radius = abs(entity.dxf.radius)
    if radius < LEN_TOL:
        return None
    start_angle = entity.dxf.start_angle
    end_angle = entity.dxf.end_angle
    span_deg = arc_angle_span_deg(start_angle, end_angle)
    length = radius * span_deg / 180.0 * math.pi
    sp, ep = entity.vertices((start_angle, end_angle))
    return _validate_edge(
        # arc projected onto the xy-plane
        em.make_edge(Vec2(sp), Vec2(ep), length, payload=entity),
        gap_tol,
    )


@make_edge_2d.register(et.Ellipse)
def _edge_from_ellipse(entity: et.Ellipse, gap_tol=GAP_TOL) -> em.Edge | None:
    try:
        ct1 = entity.construction_tool()
    except ValueError:
        return None
    if ct1.major_axis.magnitude < LEN_TOL or ct1.minor_axis.magnitude < LEN_TOL:
        return None
    span = ellipse_param_span(ct1.start_param, ct1.end_param)
    num = max(3, round(span / 0.1745))  # resolution of ~1 deg
    # length of elliptic arc is an approximation:
    # ellipse projected onto the xy-plane
    points = Vec2.list(ct1.vertices(ct1.params(num)))
    length = sum(a.distance(b) for a, b in zip(points, points[1:]))
    return _validate_edge(
        em.make_edge(points[0], points[-1], length, payload=entity), gap_tol
    )


@make_edge_2d.register(et.Spline)
def _edge_from_spline(entity: et.Spline, gap_tol=GAP_TOL) -> em.Edge | None:
    try:
        ct2 = entity.construction_tool()
    except ValueError:
        return None
    # spline projected onto the xy-plane
    start = Vec2(ct2.control_points[0])
    end = Vec2(ct2.control_points[-1])
    points = Vec2.list(ct2.control_points)
    # length of B-spline is a very rough approximation:
    length = sum(a.distance(b) for a, b in zip(points, points[1:]))
    return _validate_edge(em.make_edge(start, end, length, payload=entity), gap_tol)


@make_edge_2d.register(et.LWPolyline)
def _edge_from_lwpolyline(entity: et.LWPolyline, gap_tol=GAP_TOL) -> em.Edge | None:
    if _is_closed_lwpolyline(entity):
        return None
    # polyline projected onto the xy-plane
    points = Vec2.list(entity.vertices_in_wcs())
    if len(points) < 2:
        return None
    start = points[0]
    end = points[-1]
    # length of LWPolyline does not include bulge length:
    length = sum(a.distance(b) for a, b in zip(points, points[1:]))
    return _validate_edge(em.make_edge(start, end, length, payload=entity), gap_tol)


@make_edge_2d.register(et.Polyline)
def _edge_from_polyline(entity: et.Polyline, gap_tol=GAP_TOL) -> em.Edge | None:
    if not (entity.is_2d_polyline or entity.is_3d_polyline):
        return None
    if _is_closed_polyline2d(entity):
        return None
    # polyline projected onto the xy-plane
    points = Vec2.list(entity.points_in_wcs())
    if len(points) < 2:
        return None

    start = points[0]
    end = points[-1]
    # length of Polyline does not include bulge length:
    length = sum(a.distance(b) for a, b in zip(points, points[1:]))
    return _validate_edge(em.make_edge(start, end, length, payload=entity), gap_tol)


def edges_from_entities_2d(
    entities: Iterable[et.DXFEntity], gap_tol=GAP_TOL
) -> Iterator[em.Edge]:
    """Yields all DXF entities as 2D edges in the xy-plane.

    Skips all entities that have a closed shape or can not be represented as edge.
    """
    for entity in entities:
        edge = make_edge_2d(entity, gap_tol)
        if edge is not None:
            yield edge


def chain_vertices(edges: Sequence[em.Edge], gap_tol=GAP_TOL) -> Sequence[Vec3]:
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


def lwpolyline_from_chain(
    edges: Sequence[em.Edge],
    dxfattribs: Any = None,
    max_sagitta: float = -1,
) -> et.LWPolyline:
    """Returns a new virtual :class:`~ezdxf.entities.LWPolyline` entity.

    This function assumes the building blocks as simple DXF entities attached as payload
    to the edges. The edges are processed in order of the input sequence. The output
    polyline is projected onto the xy-plane.

        - :class:`~ezdxf.entities.Line` as line segment
        - :class:`~ezdxf.entities.Arc` as bulge
        - :class:`~ezdxf.entities.Ellipse` as bulge or as flattened line segments
        - :class:`~ezdxf.entities.Spline` as flattened line segments
        - :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Polyline`
          will be merged
        - Everything else will be added as line segment from :attr:`Edge.start` to
          :attr:`Edge.end`
        - Gaps between edges are connected by line segments.

    """
    polyline = et.LWPolyline.new(dxfattribs=dxfattribs)
    if len(edges) == 0:
        return polyline
    polyline.set_points(_make_polyline_points(edges, max_sagitta), format="vb")  # type: ignore
    return polyline


def polyline2d_from_chain(
    edges: Sequence[em.Edge], dxfattribs: Any = None, max_sagitta: float = -1
) -> et.Polyline:
    """Returns a new virtual :class:`Polyline` entity.

    This function assumes the building blocks as simple DXF entities attached as payload
    to the edges. The edges are processed in order of the input sequence. The output
    polyline is projected onto the xy-plane.

        - :class:`~ezdxf.entities.Line` as line segment
        - :class:`~ezdxf.entities.Arc` as bulge
        - :class:`~ezdxf.entities.Ellipse` as bulge or as flattened line segments
        - :class:`~ezdxf.entities.Spline` as flattened line segments
        - :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Polyline`
          will be merged
        - Everything else will be added as line segment from :attr:`Edge.start` to
          :attr:`Edge.end`
        - Gaps between edges are connected by line segments.

    """
    polyline = et.Polyline.new(dxfattribs=dxfattribs)
    if len(edges) == 0:
        return polyline
    polyline.append_formatted_vertices(
        _make_polyline_points(edges, max_sagitta), format="vb"
    )
    return polyline


BulgePoints: TypeAlias = list[tuple[Vec2, float]]


def _adjust_max_sagitta(max_sagitta: float, length: float) -> float:
    if max_sagitta < 0:
        max_sagitta = length / 100.0
    return max_sagitta


def _flatten_3d_entity(
    entity, length: float, max_sagitta: float, is_reverse: bool
) -> BulgePoints:
    points: BulgePoints = []
    try:
        entity_path = path.make_path(entity)
    except TypeError:
        return points
    max_sagitta = _adjust_max_sagitta(max_sagitta, length)
    if max_sagitta > LEN_TOL:
        points.extend((p, 0.0) for p in Vec2.list(entity_path.flattening(max_sagitta)))
    if is_reverse:
        # edge.start and edge.end are in correct order
        # start and end of the attached entity are NOT in correct order
        points.reverse()
    return points


def _arc_to_bulge_points(edge: em.Edge, max_sagitta: float) -> BulgePoints:
    arc: et.Arc = edge.payload
    if Z_AXIS.isclose(arc.dxf.extrusion):
        span = arc_angle_span_deg(arc.dxf.start_angle, arc.dxf.end_angle)
        bulge: float = 0.0
        if span > DEG_TOL:
            bulge = bulge_from_arc_angle(math.radians(span))
            if edge.is_reverse:
                bulge = -bulge
        return [
            (Vec2(edge.start), bulge),
            (Vec2(edge.end), 0.0),
        ]
    # flatten arc and project onto xy-plane
    return _flatten_3d_entity(arc, edge.length, max_sagitta, edge.is_reverse)


def _ellipse_to_bulge_points(edge: em.Edge, max_sagitta: float) -> BulgePoints:
    ellipse: et.Ellipse = edge.payload
    ratio = abs(ellipse.dxf.ratio)
    span = ellipse_param_span(ellipse.dxf.start_param, ellipse.dxf.end_param)
    if math.isclose(ratio, 1.0) and Z_AXIS.isclose(ellipse.dxf.extrusion):
        bulge = 0.0
        if span > RAD_TOL:
            bulge = bulge_from_arc_angle(span)
            if edge.is_reverse:
                bulge = -bulge
        return [
            (Vec2(edge.start), bulge),
            (Vec2(edge.end), 0.0),
        ]
    # flatten ellipse and project onto xy-plane
    return _flatten_3d_entity(ellipse, edge.length, max_sagitta, edge.is_reverse)


def _sum_distances(vertices: Sequence[Vec3]) -> float:
    if len(vertices) < 2:
        return 0.0
    return sum(p0.distance(p1) for p0, p1 in zip(vertices, vertices[1:]))


def _max_sagitta_spline(max_sagitta: float, control_points: Sequence[Vec3]):
    if max_sagitta > 0:
        return max_sagitta
    return _sum_distances(control_points) / 100.0


def _spline_to_bulge_points(edge: em.Edge, max_sagitta: float) -> BulgePoints:
    spline: et.Spline = edge.payload
    points: BulgePoints = []
    try:
        ct = spline.construction_tool()
    except ValueError:
        return points

    max_sagitta = _max_sagitta_spline(max_sagitta, ct.control_points)
    if max_sagitta > LEN_TOL:
        points.extend((Vec2(p), 0.0) for p in ct.flattening(max_sagitta))
    if edge.is_reverse:
        # edge.start and edge.end are in correct order
        # start and end of the attached entity are NOT in correct order
        points.reverse()
    return points


def _lwpolyline_to_bulge_points(edge: em.Edge, max_sagitta: float) -> BulgePoints:
    pl: et.LWPolyline = edge.payload
    if Z_AXIS.isclose(pl.dxf.extrusion):
        points = [(Vec2(x, y), b) for x, y, b in pl.get_points(format="xyb")]
        if edge.is_reverse:
            return _revert_bulge_points(points)
        return points
    return _flatten_3d_entity(pl, edge.length, max_sagitta, edge.is_reverse)


def _polyline2d_to_bulge_points(edge: em.Edge, max_sagitta: float) -> BulgePoints:
    pl: et.Polyline = edge.payload

    if pl.is_2d_polyline and Z_AXIS.isclose(pl.dxf.extrusion):
        points = [(Vec2(v.dxf.location), v.dxf.bulge) for v in pl.vertices]
        if edge.is_reverse:
            return _revert_bulge_points(points)
        return points
    return _flatten_3d_entity(pl, edge.length, max_sagitta, edge.is_reverse)


def _revert_bulge_points(pts: BulgePoints) -> BulgePoints:
    if len(pts) < 2:
        return pts
    pts.reverse()
    bulges = [pnt[1] for pnt in pts]
    if any(bulges):
        # shift bulge values to previous vertex
        first = bulges.pop(0)
        bulges.append(first)
        return list(zip((pnt[0] for pnt in pts), bulges))
    return pts


def _extend_bulge_points(points: BulgePoints, extension: BulgePoints) -> BulgePoints:
    if len(extension) < 2:
        return points
    try:
        current_end, _ = points[-1]
    except IndexError:
        points.extend(extension)
        return points

    connection_point, _ = extension[0]
    if current_end.distance(connection_point) < LEN_TOL:
        points.pop()
    points.extend(extension)
    return points


POLYLINE_CONVERTERS = {
    et.Arc: _arc_to_bulge_points,
    et.Ellipse: _ellipse_to_bulge_points,
    et.Spline: _spline_to_bulge_points,
    et.LWPolyline: _lwpolyline_to_bulge_points,
    et.Polyline: _polyline2d_to_bulge_points,
}


def _make_polyline_points(edges: Sequence[em.Edge], max_sagitta: float) -> BulgePoints:
    """Returns the polyline points to create a LWPolyline or a 2D Polyline entity."""
    points: BulgePoints = []
    extension: BulgePoints = []
    for edge in edges:
        extension.clear()
        converter = POLYLINE_CONVERTERS.get(type(edge.payload))
        if converter:
            extension = converter(edge, max_sagitta)
        if len(extension) < 2:
            extension = [
                (Vec2(edge.start), 0.0),
                (Vec2(edge.end), 0.0),
            ]
        points = _extend_bulge_points(points, extension)
    return points


def polyline_path_from_chain(
    edges: Sequence[em.Edge], max_sagitta: float = -1
) -> bp.PolylinePath:
    """Returns a new :class:`~ezdxf.entities.PolylinePath` for :class:`~ezdxf.entities.Hatch`
    entities.

    This function assumes the building blocks as simple DXF entities attached as payload
    to the edges. The edges are processed in order of the input sequence. The output
    path is projected onto the xy-plane.

        - :class:`~ezdxf.entities.Line` as line segment
        - :class:`~ezdxf.entities.Arc` as bulge
        - :class:`~ezdxf.entities.Ellipse` as bulge or flattened line segments
        - :class:`~ezdxf.entities.Spline` as flattened line segments
        - :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Polyline` are
          merged
        - Everything else will be added as line segment from :attr:`Edge.start` to
          :attr:`Edge.end`
        - Gaps between edges are connected by line segments.

    """
    polyline_path = bp.PolylinePath()
    if len(edges) == 0:
        return polyline_path
    bulge_points = _make_polyline_points(edges, max_sagitta)
    polyline_path.set_vertices([(p.x, p.y, b) for p, b in bulge_points])
    return polyline_path


def edge_path_from_chain(
    edges: Sequence[em.Edge], max_sagitta: float = -1
) -> bp.EdgePath:
    """Returns a new :class:`~ezdxf.entities.EdgePath` for :class:`~ezdxf.entities.Hatch`
    entities.

    This function assumes the building blocks as simple DXF entities attached as payload
    to the edges.  The edges are processed in order of the input sequence. The output
    path is projected onto the xy-plane.

        - :class:`~ezdxf.entities.Line` as :class:`~ezdxf.entities.LineEdge`
        - :class:`~ezdxf.entities.Arc` as :class:`~ezdxf.entities.ArcEdge`
        - :class:`~ezdxf.entities.Ellipse` as :class:`~ezdxf.entities.EllipseEdge`
        - :class:`~ezdxf.entities.Spline` as :class:`~ezdxf.entities.SplineEdge`
        - :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Polyline` as
          :class:`~ezdxf.entities.LineEdge` and :class:`~ezdxf.entities.ArcEdge`
        - Everything else will be added as line segment from :attr:`Edge.start` to
          :attr:`Edge.end`
        - Gaps between edges are connected by line segments.

    """
    raise NotImplementedError()


def path2d_from_chain(edges: Sequence[em.Edge]) -> path.Path:
    """Returns a new :class:`ezdxf.path.Path` entity.

    This function assumes the building blocks as simple DXF entities attached as payload
    to the edges.  The edges are processed in order of the input sequence.  The output
    is a 2D path projected onto the xy-plane.

        - :class:`~ezdxf.entities.Line` as line segment
        - :class:`~ezdxf.entities.Arc` as cubic Bézier curves
        - :class:`~ezdxf.entities.Ellipse` as cubic Bézier curves
        - :class:`~ezdxf.entities.Spine` cubic Bézier curves
        - :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Polyline`
          as line segments and cubic Bézier curves
        - Everything else will be added as line segment from :attr:`Edge.start` to
          :attr:`Edge.end`
        - Gaps between edges are connected by line segments.

    """
    main_path = path.Path()
    if len(edges) == 0:
        return main_path

    # project vertices onto the xy-plane by multiplying the z-axis by 0
    m = Matrix44.scale(1.0, 1.0, 0.0)
    for edge in edges:
        try:
            sub_path = path.make_path(edge.payload)
        except (ValueError, TypeError):
            continue
        sub_path = sub_path.transform(m)
        if edge.is_reverse:
            sub_path = sub_path.reversed()
        main_path.append_path(sub_path)
    return main_path
