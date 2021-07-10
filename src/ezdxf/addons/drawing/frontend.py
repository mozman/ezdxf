# Copyright (c) 2020-2021, Matthew Broadway
# License: MIT License
import math
from typing import Iterable, cast, Union, List, Dict, Callable
from ezdxf.lldxf import const
from ezdxf.addons.drawing.backend import Backend
from ezdxf.addons.drawing.properties import (
    RenderContext, VIEWPORT_COLOR, Properties, set_color_alpha, Filling,
)
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.type_hints import FilterFunc
from ezdxf.entities import (
    DXFGraphic, Insert, MText, Polyline, LWPolyline, Spline, Hatch, Attrib,
    Text, Polyface, Wipeout, AttDef, Solid, Face3d,
)
from ezdxf.entities.dxfentity import DXFTagStorage, DXFEntity
from ezdxf.layouts import Layout
from ezdxf.math import Vec3, Z_AXIS
from ezdxf.path import (
    make_path, from_hatch_boundary_path, fast_bbox_detection,
    winding_deconstruction, from_vertices,
)
from ezdxf.render import MeshBuilder, TraceBuilder
from ezdxf import reorder
from ezdxf.proxygraphic import ProxyGraphic

__all__ = ['Frontend']
NEG_Z_AXIS = -Z_AXIS
INFINITE_LINE_LENGTH = 25
DEFAULT_PDSIZE = 1

IGNORE_PROXY_GRAPHICS = 0
USE_PROXY_GRAPHICS = 1
PREFER_PROXY_GRAPHICS = 2


class Frontend:
    """ Drawing frontend, responsible for decomposing entities into graphic
    primitives and resolving entity properties.

    Args:
        ctx: actual render context of a DXF document
        out: backend

    """

    def __init__(self, ctx: RenderContext, out: Backend,
        proxy_graphics: int = USE_PROXY_GRAPHICS):
        # RenderContext contains all information to resolve resources for a
        # specific DXF document.
        self.ctx = ctx

        # DrawingBackend is the interface to the render engine
        self.out = out

        # To get proxy graphics support proxy graphics have to be loaded:
        # Set the global option ezdxf.options.load_proxy_graphics to True.
        # How to handle proxy graphics:
        # 0 = ignore proxy graphics
        # 1 = use proxy graphics if no rendering support by ezdxf exist
        # 2 = prefer proxy graphics over ezdxf rendering
        self.proxy_graphics = proxy_graphics

        # Transfer render context info to backend:
        ctx.update_backend_configuration(out)

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

        # set to None to disable nested polygon detection:
        self.nested_polygon_detection = fast_bbox_detection

        self._dispatch = self._build_dispatch_table()

    def _build_dispatch_table(self) -> Dict[
        str, Callable[[DXFGraphic, Properties], None]]:
        dispatch_table = {
            'POINT': self.draw_point_entity,
            'HATCH': self.draw_hatch_entity,
            'MESH': self.draw_mesh_entity,
            'VIEWPORT': self.draw_viewport_entity,
            'WIPEOUT': self.draw_wipeout_entity,
            'MTEXT': self.draw_mtext_entity,
        }
        for dxftype in ('LINE', 'XLINE', 'RAY'):
            dispatch_table[dxftype] = self.draw_line_entity
        for dxftype in ('TEXT', 'ATTRIB', 'ATTDEF'):
            dispatch_table[dxftype] = self.draw_text_entity
        for dxftype in ('CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE'):
            dispatch_table[dxftype] = self.draw_curve_entity
        for dxftype in ('3DFACE', 'SOLID', 'TRACE'):
            dispatch_table[dxftype] = self.draw_solid_entity
        for dxftype in ('POLYLINE', 'LWPOLYLINE'):
            dispatch_table[dxftype] = self.draw_polyline_entity

        # These types have a virtual_entities() method, which returns
        # the content of the associated block or anonymous block
        for dxftype in ['INSERT', 'DIMENSION', 'ARC_DIMENSION',
            'LARGE_RADIAL_DIMENSION', 'LEADER',
            'MLINE', 'ACAD_TABLE']:
            dispatch_table[dxftype] = self.draw_composite_entity

        return dispatch_table

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

    def draw_layout(
        self, layout: 'Layout',
        finalize: bool = True,
        *,
        filter_func: FilterFunc = None
    ) -> None:
        self.ctx.set_current_layout(layout)
        self.parent_stack = []
        handle_mapping = list(layout.get_redraw_order())
        if handle_mapping:
            self.draw_entities(
                reorder.ascending(layout, handle_mapping),
                filter_func=filter_func,
            )
        else:
            self.draw_entities(
                layout,
                filter_func=filter_func,
            )
        self.out.set_background(self.ctx.current_layout.background_color)
        if finalize:
            self.out.finalize()

    def draw_entities(
        self,
        entities: Iterable[DXFGraphic],
        *,
        filter_func: FilterFunc = None,
    ) -> None:
        if filter_func is not None:
            entities = filter(filter_func, entities)
        for entity in entities:
            # Skip unsupported DXF entities - just tag storage to preserve data
            if isinstance(entity, DXFTagStorage):
                self.skip_entity(entity, 'Cannot parse DXF entity')
                continue
            properties = self.ctx.resolve_all(entity)
            self.override_properties(entity, properties)

            if properties.is_visible:
                self.draw_entity(entity, properties)
            else:
                self.skip_entity(entity, 'invisible')

    def draw_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        """ Draw a single DXF entity.

        Args:
            entity: DXF Entity
            properties: resolved entity properties

        """
        self.out.enter_entity(entity, properties)

        if entity.proxy_graphic and self.proxy_graphics == PREFER_PROXY_GRAPHICS:
            self.draw_proxy_graphic(entity)
        else:
            draw_method = self._dispatch.get(entity.dxftype(), None)
            if draw_method is not None:
                draw_method(entity, properties)
            elif entity.proxy_graphic and self.proxy_graphics == USE_PROXY_GRAPHICS:
                self.draw_proxy_graphic(entity)
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

    def draw_text_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        if is_spatial_text(Vec3(entity.dxf.extrusion)):
            self.draw_text_entity_3d(entity, properties)
        else:
            self.draw_text_entity_2d(entity, properties)

    def draw_text_entity_2d(self, entity: DXFGraphic,
        properties: Properties) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        if dxftype in ('TEXT', 'ATTRIB', 'ATTDEF'):
            entity = cast(Union[Text, Attrib, AttDef], entity)
            for line, transform, cap_height in simplified_text_chunks(
                entity, self.out, font=properties.font):
                self.out.draw_text(line, transform, properties, cap_height)
        else:
            raise TypeError(dxftype)

    def draw_text_entity_3d(self, entity: DXFGraphic,
        properties: Properties) -> None:
        self.skip_entity(entity, '3D text not supported')

    def draw_mtext_entity(self, mtext: 'MText',
        properties: Properties) -> None:
        if is_spatial_text(Vec3(mtext.dxf.extrusion)):
            self.skip_entity(mtext, '3D MTEXT not supported')
            return
        if mtext.has_columns:
            columns = mtext.columns
            if len(columns.linked_columns):
                has_linked_content = any(c.text for c in columns.linked_columns)
                if has_linked_content:
                    # Column content is spread across multiple MTEXT entities.
                    # For now we trust the DXF creator that each MTEXT entity
                    # has exact the required column content.
                    # This is not granted and AutoCAD/BricsCAD do the column
                    # content distribution always by themself!
                    self.draw_mtext_column(mtext, properties)
                    for column in mtext.columns.linked_columns:
                        self.draw_mtext_column(column, properties)
                    return
            self.distribute_mtext_columns_content(mtext, properties)
        else:
            self.draw_mtext_column(mtext, properties)

    def distribute_mtext_columns_content(self, mtext: MText,
        properties: Properties):
        """ Distribute the content of the MTEXT entity across multiple columns
        """
        # TODO: complex MTEXT renderer
        self.draw_mtext_column(mtext, properties)

    def draw_mtext_column(self, mtext: MText,
        properties: Properties) -> None:
        """ Draw the content of a MTEXT entity as a single column. """
        # TODO: complex MTEXT renderer
        for line, transform, cap_height in simplified_text_chunks(
            mtext, self.out, font=properties.font):
            self.out.draw_text(line, transform, properties, cap_height)

    def draw_curve_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        try:
            path = make_path(entity)
        except AttributeError:  # API usage error
            raise TypeError(
                f"Unsupported DXF type {entity.dxftype()}")
        self.out.draw_path(path, properties)

    def draw_point_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        point = cast('Point', entity)
        pdmode = self.out.pdmode

        # Defpoints are regular POINT entities located at the "defpoints" layer:
        if properties.layer.lower() == 'defpoints':
            if not self.out.show_defpoints:
                return
            else:  # Render defpoints as dimensionless points:
                pdmode = 0

        pdsize = self.out.pdsize
        if pdsize <= 0:  # relative points size is not supported
            pdsize = DEFAULT_PDSIZE

        if pdmode == 0:
            self.out.draw_point(entity.dxf.location, properties)
        else:
            for entity in point.virtual_entities(pdsize, pdmode):
                if entity.dxftype() == 'LINE':
                    start = Vec3(entity.dxf.start)
                    end = entity.dxf.end
                    if start.isclose(end):
                        self.out.draw_point(start, properties)
                    else:
                        self.out.draw_line(start, end, properties)
                    pass
                else:  # CIRCLE
                    self.draw_curve_entity(entity, properties)

    def draw_solid_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        assert isinstance(entity, (Solid, Face3d)), \
            "API error, requires a SOLID, TRACE or 3DFACE entity"
        dxf, dxftype = entity.dxf, entity.dxftype()
        points = entity.wcs_vertices()
        if dxftype == '3DFACE':
            self.out.draw_path(from_vertices(points, close=True), properties)
        else:
            # set solid fill type for SOLID and TRACE
            properties.filling = Filling()
            self.out.draw_filled_polygon(points, properties)

    def draw_hatch_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        def to_path(paths):
            loops = []
            for boundary in paths:
                path = from_hatch_boundary_path(boundary, ocs, elevation)
                for sub_path in path.sub_paths():
                    sub_path.close()
                    loops.append(sub_path)
            return loops

        if not self.out.show_hatch:
            return

        hatch = cast(Hatch, entity)
        ocs = hatch.ocs()
        # all OCS coordinates have the same z-axis stored as vector (0, 0, z),
        # default (0, 0, 0)
        elevation = entity.dxf.elevation.z

        external_paths = []
        holes = []
        paths = hatch.paths.rendering_paths(hatch.dxf.hatch_style)
        if self.nested_polygon_detection:
            polygons = self.nested_polygon_detection(to_path(paths))
            external_paths, holes = winding_deconstruction(polygons)
        else:
            for p in paths:
                if p.path_type_flags & const.BOUNDARY_PATH_EXTERNAL:
                    external_paths.extend(to_path(p))
                else:
                    holes.extend(to_path(p))

        if external_paths:
            self.out.draw_filled_paths(external_paths, holes, properties)
        elif holes:
            # First path is the exterior path, everything else is a hole
            self.out.draw_filled_paths([holes[0]], holes[1:], properties)

    def draw_wipeout_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        wipeout = cast(Wipeout, entity)
        properties.filling = Filling()
        properties.color = self.ctx.current_layout.background_color
        path = wipeout.boundary_path_wcs()
        self.out.draw_filled_polygon(path, properties)

    def draw_viewport_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        assert entity.dxftype() == 'VIEWPORT'
        # Special VIEWPORT id == 1, this viewport defines the "active viewport"
        # which is the area currently shown in the layout tab by the CAD
        # application.
        # BricsCAD set id to -1 if the viewport is off and 'status' (group
        # code 68) is not present.
        if entity.dxf.id < 2 or entity.dxf.status < 1:
            return
        dxf = entity.dxf
        view_vector: Vec3 = dxf.view_direction_vector
        mag = view_vector.magnitude
        if math.isclose(mag, 0.0):
            self.log_message('Warning: viewport with null view vector')
            return
        view_vector /= mag
        if not math.isclose(view_vector.dot(Vec3(0, 0, 1)), 1.0):
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
        self.out.draw_filled_polygon([Vec3(x, y, 0) for x, y in points],
            props)

    def draw_mesh_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        builder = MeshBuilder.from_mesh(entity)
        self.draw_mesh_builder_entity(builder, properties)

    def draw_mesh_builder_entity(self, builder: MeshBuilder,
        properties: Properties) -> None:
        for face in builder.faces_as_vertices():
            self.out.draw_path(
                from_vertices(face, close=True), properties=properties)

    def draw_polyline_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
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
                    elevation = Vec3(entity.dxf.elevation).z

            trace = TraceBuilder.from_polyline(
                entity, segments=self.circle_approximation_count // 2
            )
            for polygon in trace.polygons():  # polygon is a sequence of Vec2()
                if transform:
                    points = ocs.points_to_wcs(
                        Vec3(v.x, v.y, elevation) for v in polygon
                    )
                else:
                    points = Vec3.generate(polygon)
                # Set default SOLID filling for LWPOLYLINE
                properties.filling = Filling()
                self.out.draw_filled_polygon(points, properties)
            return

        path = make_path(entity)
        self.out.draw_path(path, properties)

    def draw_composite_entity(self, entity: DXFGraphic,
        properties: Properties) -> None:
        def set_opaque(entities: Iterable[DXFGraphic]):
            for child in entities:
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

        elif hasattr(entity, 'virtual_entities'):
            # draw_entities() includes the visibility check:
            self.draw_entities(set_opaque(entity.virtual_entities()))
        else:
            raise TypeError(dxftype)

    def draw_proxy_graphic(self, entity: DXFGraphic) -> None:
        if entity.proxy_graphic:
            gfx = ProxyGraphic(entity.proxy_graphic, entity.doc)
            self.draw_entities(gfx.virtual_entities())


def is_spatial_text(extrusion: Vec3) -> bool:
    # note: the magnitude of the extrusion vector has no effect on text scale
    return not math.isclose(extrusion.x, 0) or not math.isclose(extrusion.y, 0)
