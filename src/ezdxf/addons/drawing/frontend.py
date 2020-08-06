# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import math
from typing import Iterable, cast, Union, List
from ezdxf.lldxf import const
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.properties import (
    RenderContext, VIEWPORT_COLOR, Properties, set_color_alpha, Filling
)
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.utils import get_tri_or_quad_points
from ezdxf.entities import (
    DXFGraphic, Insert, MText, Polyline, LWPolyline, Spline, Hatch, Attrib,
    Text, Polyface, Wipeout,
)
from ezdxf.entities.dxfentity import DXFTagStorage, DXFEntity
from ezdxf.layouts import Layout
from ezdxf.math import Vector, Z_AXIS
from ezdxf.render import MeshBuilder, TraceBuilder, Path

__all__ = ['Frontend']
NEG_Z_AXIS = -Z_AXIS
INFINITE_LINE_LENGTH = 25

COMPOSITE_ENTITY_TYPES = {
    # Unsupported types, represented as DXFTagStorage(), will sorted out in
    # Frontend.draw_entities().
    'INSERT',
    # This types have a virtual_entities() method, which returns the content of
    # the associated anonymous block
    'DIMENSION', 'ARC_DIMENSION', 'LARGE_RADIAL_DIMENSION', 'LEADER',
    'ACAD_TABLE',
}


class Frontend:
    """ Drawing frontend, responsible for decomposing entities into graphic
    primitives and resolving entity properties.

    Args:
        ctx: actual render context of a DXF document
        out: backend

    """

    def __init__(self, ctx: RenderContext, out: Backend):
        # RenderContext contains all information to resolve resources for a
        # specific DXF document.
        self.ctx = ctx

        # DrawingBackend is the interface to the render engine
        self.out = out

        # Parents entities of current entity/sub-entity
        self.parent_stack: List[DXFGraphic] = []

        # Approximate a full circle by `n` segments, arcs have proportional
        # less segments
        self.circle_approximation_count = 128

        # The sagitta (also known as the versine) is a line segment drawn
        # perpendicular to a chord, between the midpoint of that chord and the
        # arc of the circle. https://en.wikipedia.org/wiki/Circle not used yet!
        # Could be used for all curves CIRCLE, ARC, ELLIPSE and SPLINE
        # self.approximation_max_sagitta = 0.01  # for drawing unit = 1m, max
        # sagitta = 1cm

    def log_message(self, message: str):
        print(message)

    def skip_entity(self, entity: DXFEntity, msg: str) -> None:
        self.log_message(f'skipped entity {str(entity)}. Reason: "{msg}"')

    def override_properties(self, entity: DXFGraphic,
                            properties: Properties) -> None:
        """ The :meth:`override_properties` filter can change the properties of
        an entity independent from the DXF attributes.

        This filter has access to the DXF attributes by the `entity` object,
        the current render context, and the resolved properties by the
        `properties` object. It is recommended to modify only the `properties`
        object in this filter.
        """
        if entity.dxftype() == 'HATCH':
            properties.color = set_color_alpha(properties.color, 200)

    def draw_layout(self, layout: 'Layout', finalize: bool = True) -> None:
        self.parent_stack = []
        self.draw_entities(layout)
        self.out.set_background(self.ctx.current_layout.background_color)
        if finalize:
            self.out.finalize()

    def draw_entities(self, entities: Iterable[DXFGraphic]) -> None:
        for entity in entities:
            # Skip unsupported DXF entities - just tag storage to preserve data
            if isinstance(entity, DXFTagStorage):
                self.skip_entity(entity, 'Cannot parse DXF entity')
                continue

            properties = self.ctx.resolve_all(entity)
            self.override_properties(entity, properties)

            # The content of a block reference does not depend
            # on the visibility state of the INSERT entity:
            if properties.is_visible or entity.dxftype() == 'INSERT':
                self.draw_entity(entity, properties)
            elif not properties.is_visible:
                self.skip_entity(entity, 'invisible')

    def draw_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        """ Draw a single DXF entity.

        Args:
            entity: DXF Entity
            properties: resolved entity properties

        """
        dxftype = entity.dxftype()
        self.out.enter_entity(entity, properties)
        if dxftype in {'LINE', 'XLINE', 'RAY'}:
            self.draw_line_entity(entity, properties)
        elif dxftype in {'TEXT', 'MTEXT', 'ATTRIB'}:
            if is_spatial(Vector(entity.dxf.extrusion)):
                self.draw_text_entity_3d(entity, properties)
            else:
                self.draw_text_entity_2d(entity, properties)
        elif dxftype in {'CIRCLE', 'ARC', 'ELLIPSE'}:
            self.draw_elliptic_arc_entity(entity, properties)
        elif dxftype == 'SPLINE':
            self.draw_spline_entity(entity, properties)
        elif dxftype == 'POINT':
            self.draw_point_entity(entity, properties)
        elif dxftype == 'HATCH':
            self.draw_hatch_entity(entity, properties)
        elif dxftype == 'MESH':
            self.draw_mesh_entity(entity, properties)
        elif dxftype in {'3DFACE', 'SOLID', 'TRACE'}:
            self.draw_solid_entity(entity, properties)
        elif dxftype in {'POLYLINE', 'LWPOLYLINE'}:
            self.draw_polyline_entity(entity, properties)
        elif dxftype in COMPOSITE_ENTITY_TYPES:
            self.draw_composite_entity(entity, properties)
        elif dxftype == 'WIPEOUT':
            self.draw_wipeout_entity(entity, properties)
        elif dxftype == 'VIEWPORT':
            self.draw_viewport_entity(entity)
        else:
            self.skip_entity(entity, 'Unsupported entity')
        self.out.exit_entity(entity)

    def draw_line_entity(self, entity: DXFGraphic,
                         properties: Properties) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        if dxftype == 'LINE':
            self.out.draw_line(d.start, d.end, properties)

        elif dxftype in ('XLINE', 'RAY'):
            start = d.start
            delta = d.unit_vector * INFINITE_LINE_LENGTH
            if dxftype == 'XLINE':
                self.out.draw_line(start - delta / 2, start + delta / 2,
                                   properties)
            elif dxftype == 'RAY':
                self.out.draw_line(start, start + delta, properties)
        else:
            raise TypeError(dxftype)

    def draw_text_entity_2d(self, entity: DXFGraphic,
                            properties: Properties) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        if dxftype in ('TEXT', 'MTEXT', 'ATTRIB'):
            entity = cast(Union[Text, MText, Attrib], entity)
            for line, transform, cap_height in simplified_text_chunks(
                    entity, self.out, font=properties.font):
                self.out.draw_text(line, transform, properties, cap_height)
        else:
            raise TypeError(dxftype)

    def draw_text_entity_3d(self, entity: DXFGraphic,
                            properties: Properties) -> None:
        return  # not supported

    def draw_elliptic_arc_entity(self, entity: DXFGraphic,
                                 properties: Properties) -> None:
        dxftype = entity.dxftype()
        if dxftype == 'CIRCLE':
            path = Path.from_circle(cast('Circle', entity))
        elif dxftype == 'ARC':
            path = Path.from_arc(cast('Arc', entity))
        elif dxftype == 'ELLIPSE':
            path = Path.from_ellipse(cast('Ellipse', entity))
        else:  # API usage error
            raise TypeError(dxftype)
        self.out.draw_path(path, properties)

    def draw_spline_entity(self, entity: DXFGraphic,
                           properties: Properties) -> None:
        path = Path.from_spline(cast(Spline, entity))
        self.out.draw_path(path, properties)

    def draw_point_entity(self, entity: DXFGraphic,
                          properties: Properties) -> None:
        self.out.draw_point(entity.dxf.location, properties)

    def draw_solid_entity(self, entity: DXFGraphic,
                          properties: Properties) -> None:
        # Handles SOLID, TRACE and 3DFACE
        dxf, dxftype = entity.dxf, entity.dxftype()
        points = get_tri_or_quad_points(
            entity, adjust_order=dxftype != '3DFACE')
        # TRACE is an OCS entity
        if dxftype == 'TRACE' and dxf.hasattr('extrusion'):
            ocs = entity.ocs()
            points = list(ocs.points_to_wcs(points))
        if dxftype == '3DFACE':
            self.out.draw_path(Path.from_vertices(points, close=True),
                               properties)
        else:
            # Set default SOLID filling for SOLID and TRACE
            properties.filling = Filling()
            self.out.draw_filled_polygon(points, properties)

    def draw_hatch_entity(self, entity: DXFGraphic,
                          properties: Properties) -> None:
        hatch = cast(Hatch, entity)
        ocs = hatch.ocs()
        # all OCS coordinates have the same z-axis stored as vector (0, 0, z),
        # default (0, 0, 0)
        elevation = entity.dxf.elevation.z
        for p in hatch.paths:
            if p.path_type_flags & const.BOUNDARY_PATH_EXTERNAL:
                # todo: implement support for inner paths
                if p.PATH_TYPE == 'EdgePath':
                    path = Path.from_hatch_edge_path(p, ocs, elevation)
                else:
                    path = Path.from_hatch_polyline_path(p, ocs, elevation)
                path.close()
                self.out.draw_path(path, properties)

    def draw_wipeout_entity(self, entity: DXFGraphic, properties: Properties):
        wipeout = cast(Wipeout, entity)
        properties.filling = Filling()
        properties.color = self.ctx.current_layout.background_color
        path = wipeout.boundary_path_wcs()
        self.out.draw_filled_polygon(path, properties)

    def draw_viewport_entity(self, entity: DXFGraphic) -> None:
        assert entity.dxftype() == 'VIEWPORT'
        dxf = entity.dxf
        view_vector: Vector = dxf.view_direction_vector
        mag = view_vector.magnitude
        if math.isclose(mag, 0.0):
            self.log_message('Warning: viewport with null view vector')
            return
        view_vector /= mag
        if not math.isclose(view_vector.dot(Vector(0, 0, 1)), 1.0):
            self.log_message(
                f'Cannot render viewport with non-perpendicular view direction:'
                f' {dxf.view_direction_vector}'
            )
            return

        cx, cy = dxf.center.x, dxf.center.y
        dx = dxf.width / 2
        dy = dxf.height / 2
        minx, miny = cx - dx, cy - dy
        maxx, maxy = cx + dx, cy + dy
        points = [
            (minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)
        ]
        props = Properties()
        props.color = VIEWPORT_COLOR
        # Set default SOLID filling for VIEWPORT
        props.filling = Filling()
        self.out.draw_filled_polygon([Vector(x, y, 0) for x, y in points],
                                     props)

    def draw_mesh_entity(self, entity: DXFGraphic,
                         properties: Properties) -> None:
        builder = MeshBuilder.from_mesh(entity)
        self.draw_mesh_builder_entity(builder, properties)

    def draw_mesh_builder_entity(self, builder: MeshBuilder,
                                 properties: Properties) -> None:
        for face in builder.faces_as_vertices():
            self.out.draw_path(
                Path.from_vertices(face, close=True), properties=properties)

    def draw_polyline_entity(self, entity: DXFGraphic, properties: Properties):
        dxftype = entity.dxftype()
        if dxftype == 'POLYLINE':
            e = cast(Polyface, entity)
            if e.is_polygon_mesh or e.is_poly_face_mesh:
                # draw 3D mesh or poly-face entity
                self.draw_mesh_builder_entity(
                    MeshBuilder.from_polyface(e),
                    properties,
                )
                return

        entity = cast(Union[LWPolyline, Polyline], entity)
        is_lwpolyline = dxftype == 'LWPOLYLINE'

        if entity.has_width:  # draw banded 2D polyline
            elevation = 0.0
            ocs = entity.ocs()
            transform = ocs.transform
            if transform:
                if is_lwpolyline:  # stored as float
                    elevation = entity.dxf.elevation
                else:  # stored as vector (0, 0, elevation)
                    elevation = Vector(entity.dxf.elevation).z

            trace = TraceBuilder.from_polyline(
                entity, segments=self.circle_approximation_count // 2
            )
            for polygon in trace.polygons():  # polygon is a sequence of Vec2()
                if transform:
                    points = ocs.points_to_wcs(
                        Vector(v.x, v.y, elevation) for v in polygon
                    )
                else:
                    points = Vector.generate(polygon)
                # Set default SOLID filling for LWPOLYLINE
                properties.filling = Filling()
                self.out.draw_filled_polygon(points, properties)
            return

        path = Path.from_lwpolyline(entity) \
            if is_lwpolyline else Path.from_polyline(entity)
        self.out.draw_path(path, properties)

    def draw_composite_entity(self, entity: DXFGraphic,
                              properties: Properties) -> None:
        def set_opaque(entities: Iterable[DXFGraphic]):
            for child in entities:
                # todo: defaults to 1.0 (fully transparent)???
                child.transparency = 0.0
                yield child

        def draw_insert(insert: Insert):
            self.draw_entities(insert.attribs)
            # draw_entities() includes the visibility check:
            self.draw_entities(insert.virtual_entities(
                skipped_entity_callback=self.skip_entity)
            )

        dxftype = entity.dxftype()
        if dxftype == 'INSERT':
            entity = cast(Insert, entity)
            self.ctx.push_state(properties)
            if entity.mcount > 1:
                for virtual_insert in entity.multi_insert():
                    draw_insert(virtual_insert)
            else:
                draw_insert(entity)
            self.ctx.pop_state()

        # DIMENSION, ARC_DIMENSION, LARGE_RADIAL_DIMENSION, LEADER
        # todo: ACAD_TABLE, MLINE, MLEADER
        elif hasattr(entity, 'virtual_entities'):
            # draw_entities() includes the visibility check:
            self.draw_entities(set_opaque(entity.virtual_entities()))
        else:
            raise TypeError(dxftype)


def is_spatial(v: Vector) -> bool:
    return not v.isclose(Z_AXIS) and not v.isclose(NEG_Z_AXIS)
