# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import copy
import math
from math import radians
from typing import Iterable, cast, Union, List, Callable

from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.properties import RenderContext, VIEWPORT_COLOR, Properties
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.utils import normalize_angle, get_tri_or_quad_points, get_draw_angles
from ezdxf.entities import DXFGraphic, Insert, MText, Polyline, LWPolyline, Face3d, Solid, Trace, \
    Spline, Hatch, Attrib, Text, Ellipse, Polyface
from ezdxf.entities.dxfentity import DXFTagStorage
from ezdxf.layouts import Layout
from ezdxf.math import Vector, Z_AXIS, ConstructionEllipse, linspace
from ezdxf.render import MeshBuilder
from ezdxf.render.trace import TraceBuilder

__all__ = ['Frontend']
NEG_Z_AXIS = -Z_AXIS
INFINITE_LINE_LENGTH = 25

COMPOSITE_ENTITY_TYPES = {
    # Unsupported types, represented as DXFTagStorage(), will sorted out in Frontend.draw_entities().
    'INSERT',
    # This types have a virtual_entities() method, which returns the content of the associated anonymous block
    'DIMENSION', 'ARC_DIMENSION', 'LARGE_RADIAL_DIMENSION', 'ACAD_TABLE',
}


class Frontend:
    """
    Drawing frontend, responsible for decomposing entities into graphic primitives and resolving entity properties.

    Args:
        ctx: actual render context of a DXF document
        out: backend
        visibility_filter: callback to override entity visibility, signature is ``func(entity: DXFGraphic) -> bool``,
                           entity enters processing pipeline if this function returns ``True``, independent
                           from visibility state stored in DXF properties or layer visibility.
                           Entity property `is_visible` is updated, but the backend can still ignore this decision
                           and check the visibility of the DXF entity by itself.

    """

    def __init__(self, ctx: RenderContext, out: Backend, visibility_filter: Callable[[DXFGraphic], bool] = None):
        # RenderContext contains all information to resolve resources for a specific DXF document.
        self.ctx = ctx

        # DrawingBackend is the interface to the render engine
        self.out = out

        # The `visibility_filter` let you override the visibility of an entity independent from the DXF attributes
        self.visibility_filter = visibility_filter

        # Parents entities of current entity/sub-entity
        self.parent_stack: List[DXFGraphic] = []

        # Approximate a full circle by `n` segments, arcs have proportional less segments
        self.circle_approximation_count = 128

        # Count of spline approximation segments = count of control points x factor
        self.spline_approximation_factor = 16

        # The sagitta (also known as the versine) is a line segment drawn perpendicular to a chord, between the
        # midpoint of that chord and the arc of the circle. https://en.wikipedia.org/wiki/Circle
        # not used yet! Could be used for all curves CIRCLE, ARC, ELLIPSE and SPLINE
        self.approximation_max_sagitta = 0.01  # for drawing unit = 1m, max sagitta = 1cm

    def draw_layout(self, layout: 'Layout', finalize: bool = True) -> None:
        self.parent_stack = []
        self.draw_entities(layout)
        self.out.set_background(self.ctx.current_layout.background_color)
        if finalize:
            self.out.finalize()

    def draw_entities(self, entities: Iterable[DXFGraphic]) -> None:
        for entity in entities:
            if isinstance(entity, DXFTagStorage):
                print(f'ignoring unsupported DXF entity: {str(entity)}')
                # unsupported DXF entity, just tag storage to preserve data
                continue
            if self.visibility_filter:
                # visibility depends only on filter result
                if self.visibility_filter(entity):
                    self.draw_entity(entity)
            # visibility depends only from DXF properties and layer state
            elif self.ctx.is_visible(entity):
                self.draw_entity(entity)

    def draw_entity(self, entity: DXFGraphic) -> None:
        dxftype = entity.dxftype()
        self.out.set_current_entity(entity, tuple(self.parent_stack))
        if dxftype in {'LINE', 'XLINE', 'RAY'}:
            self.draw_line_entity(entity)
        elif dxftype in {'TEXT', 'MTEXT', 'ATTRIB'}:
            if is_spatial(Vector(entity.dxf.extrusion)):
                self.draw_text_entity_3d(entity)
            else:
                self.draw_text_entity_2d(entity)
        elif dxftype in {'CIRCLE', 'ARC', 'ELLIPSE'}:
            if is_spatial(Vector(entity.dxf.extrusion)):
                self.draw_elliptic_arc_entity_3d(entity)
            else:
                self.draw_elliptic_arc_entity_2d(entity)
        elif dxftype == 'SPLINE':
            self.draw_spline_entity(entity)
        elif dxftype == 'POINT':
            self.draw_point_entity(entity)
        elif dxftype == 'HATCH':
            self.draw_hatch_entity(entity)
        elif dxftype == 'MESH':
            self.draw_mesh_entity(entity)
        elif dxftype in {'3DFACE', 'SOLID', 'TRACE'}:
            self.draw_solid_entity(entity)
        elif dxftype in {'POLYLINE', 'LWPOLYLINE'}:
            self.draw_polyline_entity(entity)
        elif dxftype in COMPOSITE_ENTITY_TYPES:
            self.draw_composite_entity(entity)
        elif dxftype == 'VIEWPORT':
            self.draw_viewport_entity(entity)
        else:
            print(f'ignoring {dxftype} entity')
        self.out.set_current_entity(None)

    def draw_line_entity(self, entity: DXFGraphic) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        properties = self._resolve_properties(entity)
        if dxftype == 'LINE':
            self.out.draw_line(d.start, d.end, properties)

        elif dxftype in ('XLINE', 'RAY'):
            start = d.start
            delta = Vector(d.unit_vector.x, d.unit_vector.y, 0) * INFINITE_LINE_LENGTH
            if dxftype == 'XLINE':
                self.out.draw_line(start - delta / 2, start + delta / 2, properties)
            elif dxftype == 'RAY':
                self.out.draw_line(start, start + delta, properties)
        else:
            raise TypeError(dxftype)

    def _resolve_properties(self, entity: DXFGraphic) -> Properties:
        properties = self.ctx.resolve_all(entity)
        if self.visibility_filter:  # override visibility by callback
            properties.is_visible = self.visibility_filter(entity)
        return properties

    def draw_text_entity_2d(self, entity: DXFGraphic) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        properties = self._resolve_properties(entity)
        if dxftype in ('TEXT', 'MTEXT', 'ATTRIB'):
            entity = cast(Union[Text, MText, Attrib], entity)
            for line, transform, cap_height in simplified_text_chunks(entity, self.out):
                self.out.draw_text(line, transform, properties, cap_height)
        else:
            raise TypeError(dxftype)

    def draw_text_entity_3d(self, entity: DXFGraphic) -> None:
        return  # not supported

    def draw_elliptic_arc_entity_3d(self, entity: DXFGraphic) -> None:
        dxf, dxftype = entity.dxf, entity.dxftype()
        properties = self._resolve_properties(entity)

        if dxftype in {'CIRCLE', 'ARC'}:
            center = dxf.center  # ocs transformation in .from_arc()
            radius = dxf.radius
            if dxftype == 'CIRCLE':
                start_angle = 0
                end_angle = 360
            else:
                start_angle = dxf.start_angle
                end_angle = dxf.end_angle
            e = ConstructionEllipse.from_arc(center, radius, dxf.extrusion, start_angle, end_angle)
        elif dxftype == 'ELLIPSE':
            e = cast(Ellipse, entity).construction_tool()
        else:
            raise TypeError(dxftype)

        # Approximate as 3D polyline
        segments = int((e.end_param - e.start_param) / math.tau * self.circle_approximation_count)
        points = list(e.vertices(linspace(e.start_param, e.end_param, max(4, segments + 1))))
        self.out.start_path()
        for a, b in zip(points, points[1:]):
            self.out.draw_line(a, b, properties)
        self.out.end_path()

    def draw_elliptic_arc_entity_2d(self, entity: DXFGraphic) -> None:
        dxf, dxftype = entity.dxf, entity.dxftype()
        properties = self._resolve_properties(entity)
        if dxftype == 'CIRCLE':
            center = _get_arc_wcs_center(entity)
            diameter = 2 * dxf.radius
            self.out.draw_arc(center, diameter, diameter, 0, None, properties)

        elif dxftype == 'ARC':
            center = _get_arc_wcs_center(entity)
            diameter = 2 * dxf.radius
            draw_angles = get_draw_angles(radians(dxf.start_angle), radians(dxf.end_angle), Vector(dxf.extrusion))
            self.out.draw_arc(center, diameter, diameter, 0, draw_angles, properties)

        elif dxftype == 'ELLIPSE':
            # 'param' angles are anticlockwise around the extrusion vector
            # 'param' angles are relative to the major axis angle
            # major axis angle always anticlockwise in global frame
            major_axis_angle = normalize_angle(math.atan2(dxf.major_axis.y, dxf.major_axis.x))
            width = 2 * dxf.major_axis.magnitude
            height = dxf.ratio * width  # ratio == height / width
            draw_angles = get_draw_angles(dxf.start_param, dxf.end_param, Vector(dxf.extrusion))
            self.out.draw_arc(dxf.center, width, height, major_axis_angle, draw_angles, properties)
        else:
            raise TypeError(dxftype)

    def draw_spline_entity(self, entity: DXFGraphic) -> None:
        properties = self._resolve_properties(entity)
        spline = cast(Spline, entity).construction_tool()
        points = list(spline.approximate(
            segments=self.spline_approximation_factor * len(spline.control_points))
        )
        self.out.start_path()
        for a, b in zip(points, points[1:]):
            self.out.draw_line(a, b, properties)
        self.out.end_path()

    def draw_point_entity(self, entity: DXFGraphic) -> None:
        properties = self._resolve_properties(entity)
        self.out.draw_point(entity.dxf.location, properties)

    def draw_solid_entity(self, entity: DXFGraphic) -> None:
        # Handles SOLID, TRACE and 3DFACE
        dxf, dxftype = entity.dxf, entity.dxftype()
        properties = self._resolve_properties(entity)
        points = get_tri_or_quad_points(entity, adjust_order=dxftype != '3DFACE')
        # TRACE is an OCS entity
        if dxftype == 'TRACE' and dxf.hasattr('extrusion'):
            ocs = entity.ocs()
            points = list(ocs.points_to_wcs(points))
        if dxftype == '3DFACE':
            for a, b in zip(points, points[1:]):
                self.out.draw_line(a, b, properties)
        else:  # SOLID, TRACE
            self.out.draw_filled_polygon(points, properties)

    def draw_hatch_entity(self, entity: DXFGraphic) -> None:
        properties = self._resolve_properties(entity)
        entity = cast(Hatch, entity)
        ocs = entity.ocs()
        # all OCS coordinates have the same z-axis stored as vector (0, 0, z), default (0, 0, 0)
        elevation = entity.dxf.elevation.z
        paths = copy.deepcopy(entity.paths)
        paths.polyline_to_edge_path(just_with_bulge=False)

        # For hatches, the approximation don't have to be that precise.
        paths.all_to_line_edges(num=64, spline_factor=8)
        for p in paths:
            assert p.PATH_TYPE == 'EdgePath'
            vertices = []
            last_vertex = None
            for e in p.edges:
                assert e.EDGE_TYPE == 'LineEdge'
                start, end = ocs.points_to_wcs([
                    Vector(e.start[0], e.start[1], elevation),
                    Vector(e.end[0], e.end[1], elevation),
                ])
                if last_vertex is None:
                    vertices.append(start)
                elif not last_vertex.isclose(start):
                    print(f'warning: {str(entity)} edges not contiguous: {last_vertex} -> {start}')
                    vertices.append(start)
                vertices.append(end)
                last_vertex = end

            if vertices:
                if last_vertex.isclose(vertices[0]):
                    vertices.append(last_vertex)
                self.out.draw_filled_polygon(vertices, properties)

    def draw_viewport_entity(self, entity: DXFGraphic) -> None:
        assert entity.dxftype() == 'VIEWPORT'
        dxf = entity.dxf
        view_vector: Vector = dxf.view_direction_vector
        mag = view_vector.magnitude
        if math.isclose(mag, 0.0):
            print('warning: viewport with null view vector')
            return
        view_vector /= mag
        if not math.isclose(view_vector.dot(Vector(0, 0, 1)), 1.0):
            print(f'cannot render viewport with non-perpendicular view direction: {dxf.view_direction_vector}')
            return

        cx, cy = dxf.center.x, dxf.center.y
        dx = dxf.width / 2
        dy = dxf.height / 2
        minx, miny = cx - dx, cy - dy
        maxx, maxy = cx + dx, cy + dy
        points = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]
        self.out.draw_filled_polygon([Vector(x, y, 0) for x, y in points], VIEWPORT_COLOR)

    def draw_mesh_entity(self, entity: DXFGraphic) -> None:
        properties = self._resolve_properties(entity)
        builder = MeshBuilder.from_mesh(entity)
        self.draw_mesh_builder_entity(builder, properties)

    def draw_mesh_builder_entity(self, builder: MeshBuilder, properties: Properties) -> None:
        for face in builder.faces_as_vertices():
            self.out.draw_line_string(face, close=True, properties=properties)

    def draw_polyline_entity(self, entity: DXFGraphic):
        dxftype = entity.dxftype()
        if dxftype == 'POLYLINE':
            e = cast(Polyface, entity)
            if e.is_polygon_mesh or e.is_poly_face_mesh:
                # draw 3D mesh or poly-face entity
                self.draw_mesh_builder_entity(
                    MeshBuilder.from_polyface(e),
                    self._resolve_properties(entity),
                )
                return

        entity = cast(Union[LWPolyline, Polyline], entity)
        is_lwpolyline = dxftype == 'LWPOLYLINE'

        if entity.has_width:  # draw banded 2D polyline
            properties = self._resolve_properties(entity)
            elevation = 0.0
            ocs = entity.ocs()
            transform = ocs.transform
            if transform:
                if is_lwpolyline:  # stored as float
                    elevation = entity.dxf.elevation
                else:  # stored as vector (0, 0, elevation)
                    elevation = Vector(entity.dxf.elevation).z

            trace = TraceBuilder.from_polyline(entity, segments=self.circle_approximation_count // 2)
            for face in trace.faces():  # face is a 4-tuple of Vec2()
                if transform:
                    points = ocs.points_to_wcs(Vector(v.x, v.y, elevation) for v in face)
                else:
                    points = Vector.generate(face)
                self.out.draw_filled_polygon(points, properties)
            return

        if not entity.has_arc:  # draw 2D/3D polyline without arcs
            properties = self._resolve_properties(entity)
            if is_lwpolyline:
                self.out.draw_line_string(Vector.generate(entity.vertices_in_wcs()), close=entity.closed,
                                          properties=properties)
            else:  # POLYLINE
                if entity.is_2d_polyline:
                    ocs = entity.ocs()
                    elevation = Vector(entity.dxf.elevation).z
                    vertices = ocs.points_to_wcs(Vector(p[0], p[1], elevation) for p in entity.points())
                else:
                    vertices = Vector.generate(entity.points())
                self.out.draw_line_string(vertices, close=entity.is_closed, properties=properties)
            return

        # draw 2D polyline with arcs
        self.parent_stack.append(entity)
        self.out.set_current_entity(entity, tuple(self.parent_stack))
        # todo: end points of virtual entities are not in correct order
        #  can't use self.out.start_path()
        for child in entity.virtual_entities():
            # all child entities have the same properties as the parent,
            # no visibility check required:
            self.draw_entity(child)
        # self.out.end_path()
        self.parent_stack.pop()
        self.out.set_current_entity(None)

    def draw_composite_entity(self, entity: DXFGraphic) -> None:
        dxftype = entity.dxftype()
        if dxftype == 'INSERT':
            entity = cast(Insert, entity)
            self.ctx.push_state(self._resolve_properties(entity))
            self.parent_stack.append(entity)
            # visibility check is required:
            self.draw_entities(entity.attribs)
            try:
                children = list(entity.virtual_entities())
            except Exception as e:
                print(f'Exception {type(e)}({e}) failed to get children of insert entity: {e}')
                return
            # visibility check is required:
            self.draw_entities(children)
            self.parent_stack.pop()
            self.ctx.pop_state()

        # DIMENSION, ARC_DIMENSION, LARGE_RADIAL_DIMENSION and ACAD_TABLE
        # All these entities have an associated anonymous geometry block.
        elif hasattr(entity, 'virtual_entities'):
            children = []
            try:
                for child in entity.virtual_entities():
                    child.transparency = 0.0  # todo: defaults to 1.0 (fully transparent)???
                    children.append(child)
            except Exception as e:
                print(f'Exception {type(e)}({e}) failed to get children of entity: {str(entity)}')
                return

            self.parent_stack.append(entity)
            # visibility check is required:
            self.draw_entities(children)
            self.parent_stack.pop()

        else:
            raise TypeError(dxftype)


def _get_arc_wcs_center(arc: DXFGraphic) -> Vector:
    """ Returns the center of an ARC or CIRCLE as WCS coordinates. """
    center = arc.dxf.center
    if arc.dxf.hasattr('extrusion'):
        ocs = arc.ocs()
        return ocs.to_wcs(center)
    else:
        return center


def is_spatial(v: Vector) -> bool:
    return not v.isclose(Z_AXIS) and not v.isclose(NEG_Z_AXIS)
