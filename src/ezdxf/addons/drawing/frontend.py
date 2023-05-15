# Copyright (c) 2020-2022, Matthew Broadway
# License: MIT License
from __future__ import annotations
import math
from typing import (
    Iterable,
    Iterator,
    cast,
    Union,
    Sequence,
    Dict,
    Callable,
    Tuple,
    Optional,
)
from typing_extensions import TypeAlias
import logging
import itertools
import time

import ezdxf.bbox
from ezdxf.addons.drawing.config import (
    Configuration,
    ProxyGraphicPolicy,
    HatchPolicy,
)
from ezdxf.addons.drawing.backend import BackendInterface
from ezdxf.addons.drawing.clipper import ClippingRect
from ezdxf.addons.drawing.properties import (
    RenderContext,
    VIEWPORT_COLOR,
    OLE2FRAME_COLOR,
    Properties,
    Filling,
    LayoutProperties,
    BackendProperties,
    hex_to_rgb,
    rgb_to_hex,
)
from ezdxf.addons.drawing.config import LinePolicy, BackgroundPolicy, ColorPolicy
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.type_hints import FilterFunc
from ezdxf.addons.drawing.gfxproxy import DXFGraphicProxy
from ezdxf.addons.drawing.mtext_complex import complex_mtext_renderer
from ezdxf.addons.drawing.unified_text_renderer import UnifiedTextRenderer
from ezdxf.entities import (
    DXFEntity,
    DXFGraphic,
    Insert,
    MText,
    Polyline,
    LWPolyline,
    Text,
    Polyface,
    Wipeout,
    Solid,
    Face3d,
    OLE2Frame,
    Point,
    Viewport,
)
from ezdxf.entities.attrib import BaseAttrib
from ezdxf.entities.polygon import DXFPolygon
from ezdxf.entities.boundary_paths import AbstractBoundaryPath
from ezdxf.layouts import Layout
from ezdxf.math import Vec2, Vec3, OCS, NULLVEC, Matrix44, AnyVec
from ezdxf.path import (
    Path,
    Path2d,
    make_path,
    from_hatch_boundary_path,
    fast_bbox_detection,
    winding_deconstruction,
    from_vertices,
    single_paths,
)
from ezdxf.render import MeshBuilder, TraceBuilder, linetypes
from ezdxf import reorder
from ezdxf.proxygraphic import ProxyGraphic, ProxyGraphicError
from ezdxf.protocols import SupportsVirtualEntities, virtual_entities
from ezdxf.tools.text import (
    has_inline_formatting_codes,
    replace_non_printable_characters,
)
from ezdxf.lldxf import const
from ezdxf.render import hatching
from ezdxf.fonts import fonts
from ezdxf.colors import luminance
from .type_hints import Color


__all__ = ["Frontend"]


TDispatchTable: TypeAlias = Dict[str, Callable[[DXFGraphic, Properties], None]]
PatternKey: TypeAlias = Tuple[str, float]

POST_ISSUE_MSG = (
    "Please post sample DXF file at https://github.com/mozman/ezdxf/issues."
)
logger = logging.getLogger("ezdxf")


class Frontend:
    """Drawing frontend, responsible for decomposing entities into graphic
    primitives and resolving entity properties.

    By passing the bounding box cache of the modelspace entities can speed up
    paperspace rendering, because the frontend can filter entities which are not
    visible in the VIEWPORT. Even passing in an empty cache can speed up
    rendering time when multiple viewports need to be processed.

    Args:
        ctx: the properties relevant to rendering derived from a DXF document
        out: the backend to draw to
        config: settings to configure the drawing frontend and backend
        bbox_cache: bounding box cache of the modelspace entities or an empty
            cache which will be filled dynamically when rendering multiple
            viewports or ``None`` to disable bounding box caching at all

    """

    def __init__(
        self,
        ctx: RenderContext,
        out: BackendInterface,
        config: Configuration = Configuration.defaults(),
        bbox_cache: Optional[ezdxf.bbox.Cache] = None,
    ):
        # RenderContext contains all information to resolve resources for a
        # specific DXF document.
        self.ctx = ctx
        self.out = out
        self.config = ctx.update_configuration(config)

        if self.config.pdsize is None or self.config.pdsize <= 0:
            self.log_message("relative point size is not supported")
            self.config = self.config.with_changes(pdsize=1)

        self.out.configure(self.config)

        # Parents entities of current entity/sub-entity
        self.parent_stack: list[DXFGraphic] = []

        self._dispatch = self._build_dispatch_table()

        # Supported DXF entities which use only proxy graphic for rendering:
        self._proxy_graphic_only_entities: set[str] = {
            "MLEADER",  # todo: remove if MLeader.virtual_entities() is implemented
            "MULTILEADER",
            "ACAD_PROXY_ENTITY",
        }
        # connection link between frontend and backend, the frontend should not
        # call the draw_...() methods of the backend directly:
        self._designer = Designer(self, out)

        # Optional bounding box cache, which maybe was created by detecting the
        # modelspace extends. This cache is used when rendering VIEWPORT
        # entities in paperspace to detect if an entity is even visible,
        # this can speed up rendering time if multiple viewports are present.
        # If the bbox_cache is not ``None``, entities not in cache will be
        # added dynamically. This is only beneficial when rendering multiple
        # viewports, as the upfront bounding box calculation adds some rendering
        # time.
        self._bbox_cache = bbox_cache

    @property
    def text_engine(self):
        return self._designer.text_engine

    def _build_dispatch_table(self) -> TDispatchTable:
        dispatch_table: TDispatchTable = {
            "POINT": self.draw_point_entity,
            "HATCH": self.draw_hatch_entity,
            "MPOLYGON": self.draw_mpolygon_entity,
            "MESH": self.draw_mesh_entity,
            "VIEWPORT": self.draw_viewport_entity,
            "WIPEOUT": self.draw_wipeout_entity,
            "MTEXT": self.draw_mtext_entity,
            "OLE2FRAME": self.draw_ole2frame_entity,
        }
        for dxftype in ("LINE", "XLINE", "RAY"):
            dispatch_table[dxftype] = self.draw_line_entity
        for dxftype in ("TEXT", "ATTRIB", "ATTDEF"):
            dispatch_table[dxftype] = self.draw_text_entity
        for dxftype in ("CIRCLE", "ARC", "ELLIPSE", "SPLINE"):
            dispatch_table[dxftype] = self.draw_curve_entity
        for dxftype in ("3DFACE", "SOLID", "TRACE"):
            dispatch_table[dxftype] = self.draw_solid_entity
        for dxftype in ("POLYLINE", "LWPOLYLINE"):
            dispatch_table[dxftype] = self.draw_polyline_entity
        # Composite entities are detected by implementing the
        # __virtual_entities__() protocol.
        return dispatch_table

    def log_message(self, message: str):
        """Log given message - override to alter behavior."""
        logger.info(message)

    def skip_entity(self, entity: DXFEntity, msg: str) -> None:
        """Called for skipped entities - override to alter behavior."""
        self.log_message(f'skipped entity {str(entity)}. Reason: "{msg}"')

    def override_properties(self, entity: DXFGraphic, properties: Properties) -> None:
        """The :meth:`override_properties` filter can change the properties of
        an entity independent of the DXF attributes.

        This filter has access to the DXF attributes by the `entity` object,
        the current render context, and the resolved properties by the
        `properties` object. It is recommended to modify only the `properties`
        object in this filter.
        """

    def draw_layout(
        self,
        layout: Layout,
        finalize: bool = True,
        *,
        filter_func: Optional[FilterFunc] = None,
        layout_properties: Optional[LayoutProperties] = None,
    ) -> None:
        """Draw all entities of the given `layout`.

        Draws the entities of the layout in the default or redefined redraw-order
        and calls the :meth:`finalize` method of the backend if requested.
        The default redraw order is the ascending handle order not the order the
        entities are stored in the layout.

        The method skips invisible entities and entities for which the given
        filter function returns ``False``.

        Args:
            layout: layout to draw of type :class:`~ezdxf.layouts.Layout`
            finalize: ``True`` if the :meth:`finalize` method of the backend
                should be called automatically
            filter_func: function to filter DXf entities, the function should
                return ``False`` if a given entity should be ignored
            layout_properties: override the default layout properties

        """
        if layout_properties is not None:
            # TODO: this does not work, layer properties have to be re-evaluated!
            self.ctx.current_layout_properties = layout_properties
        else:
            self.ctx.set_current_layout(layout)
        # set background before drawing entities
        self.set_background(self.ctx.current_layout_properties.background_color)
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
        if finalize:
            self.out.finalize()

    def set_background(self, color: Color) -> None:
        policy = self.config.background_policy
        if policy == BackgroundPolicy.DEFAULT:
            pass
        elif policy == BackgroundPolicy.OFF:
            color = "#ffffff00"  # white, fully transparent
        elif policy == BackgroundPolicy.BLACK:
            color = "#000000"
        elif policy == BackgroundPolicy.WHITE:
            color = "#ffffff"
        elif policy == BackgroundPolicy.CUSTOM:
            color = self.config.custom_bg_color
        self.out.set_background(color)

    def draw_entities(
        self,
        entities: Iterable[DXFGraphic],
        *,
        filter_func: Optional[FilterFunc] = None,
    ) -> None:
        """Draw the given `entities`. The method skips invisible entities
        and entities for which the given filter function returns ``False``.

        """
        _draw_entities(self, self.ctx, entities, filter_func=filter_func)

    def draw_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        """Draw a single DXF entity.

        Args:
            entity: DXF entity inherited from DXFGraphic()
            properties: resolved entity properties

        """
        self.out.enter_entity(entity, properties)
        if not entity.is_virtual:
            # top level entity
            self._designer.set_current_entity_handle(entity.dxf.handle)
        if (
            entity.proxy_graphic
            and self.config.proxy_graphic_policy == ProxyGraphicPolicy.PREFER
        ):
            self.draw_proxy_graphic(entity.proxy_graphic, entity.doc)
        else:
            draw_method = self._dispatch.get(entity.dxftype(), None)
            if draw_method is not None:
                draw_method(entity, properties)
            # Composite entities (INSERT, DIMENSION, ...) have to implement the
            # __virtual_entities__() protocol.
            # Unsupported DXF types which have proxy graphic, are wrapped into
            # DXFGraphicProxy, which also implements the __virtual_entities__()
            # protocol.
            elif isinstance(entity, SupportsVirtualEntities):
                assert isinstance(entity, DXFGraphic)
                # The __virtual_entities__() protocol does not distinguish
                # content from DXF entities or from proxy graphic.
                # In the long run ACAD_PROXY_ENTITY should be the only
                # supported DXF entity which uses proxy graphic. Unsupported
                # DXF entities (DXFGraphicProxy) do not get to this point if
                # proxy graphic is ignored.
                if (
                    self.config.proxy_graphic_policy != ProxyGraphicPolicy.IGNORE
                    or entity.dxftype() not in self._proxy_graphic_only_entities
                ):
                    self.draw_composite_entity(entity, properties)
            else:
                self.skip_entity(entity, "unsupported")

        self.out.exit_entity(entity)

    def draw_line_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        if dxftype == "LINE":
            self._designer.draw_line(d.start, d.end, properties)

        elif dxftype in ("XLINE", "RAY"):
            start = d.start
            delta = d.unit_vector * self.config.infinite_line_length
            if dxftype == "XLINE":
                self._designer.draw_line(
                    start - delta / 2, start + delta / 2, properties
                )
            elif dxftype == "RAY":
                self._designer.draw_line(start, start + delta, properties)
        else:
            raise TypeError(dxftype)

    def draw_text_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        # Draw embedded MTEXT entity as virtual MTEXT entity:
        if isinstance(entity, BaseAttrib) and entity.has_embedded_mtext_entity:
            self.draw_mtext_entity(entity.virtual_mtext_entity(), properties)
        elif is_spatial_text(Vec3(entity.dxf.extrusion)):
            self.draw_text_entity_3d(entity, properties)
        else:
            self.draw_text_entity_2d(entity, properties)

    def get_font_face(self, properties: Properties) -> fonts.FontFace:
        font_face = properties.font
        if font_face is None:
            return self._designer.default_font_face
        return font_face

    def draw_text_entity_2d(self, entity: DXFGraphic, properties: Properties) -> None:
        if isinstance(entity, Text):
            for line, transform, cap_height in simplified_text_chunks(
                entity, self.text_engine, font_face=self.get_font_face(properties)
            ):
                self._designer.draw_text(
                    line, transform, properties, cap_height, entity.dxftype()
                )
        else:
            raise TypeError(entity.dxftype())

    def draw_text_entity_3d(self, entity: DXFGraphic, properties: Properties) -> None:
        self.skip_entity(entity, "3D text not supported")

    def draw_mtext_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        mtext = cast(MText, entity)
        if is_spatial_text(Vec3(mtext.dxf.extrusion)):
            self.skip_entity(mtext, "3D MTEXT not supported")
            return
        if mtext.has_columns or has_inline_formatting_codes(mtext.text):
            self.draw_complex_mtext(mtext, properties)
        else:
            self.draw_simple_mtext(mtext, properties)

    def draw_simple_mtext(self, mtext: MText, properties: Properties) -> None:
        """Draw the content of a MTEXT entity without inline formatting codes."""
        for line, transform, cap_height in simplified_text_chunks(
            mtext, self.text_engine, font_face=self.get_font_face(properties)
        ):
            self._designer.draw_text(
                line, transform, properties, cap_height, mtext.dxftype()
            )

    def draw_complex_mtext(self, mtext: MText, properties: Properties) -> None:
        """Draw the content of a MTEXT entity including inline formatting codes."""
        complex_mtext_renderer(self.ctx, self._designer, mtext, properties)

    def draw_curve_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        try:
            path = make_path(entity)
        except AttributeError:  # API usage error
            raise TypeError(f"Unsupported DXF type {entity.dxftype()}")
        self._designer.draw_path(path, properties)

    def draw_point_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        point = cast(Point, entity)
        pdmode = self.config.pdmode
        pdsize = self.config.pdsize
        assert pdmode is not None
        assert pdsize is not None

        # Defpoints are regular POINT entities located at the "defpoints" layer:
        if properties.layer.lower() == "defpoints":
            if not self.config.show_defpoints:
                return
            else:  # Render defpoints as dimensionless points:
                pdmode = 0

        if pdmode == 0:
            self._designer.draw_point(entity.dxf.location, properties)
        else:
            for entity in point.virtual_entities(pdsize, pdmode):
                dxftype = entity.dxftype()
                if dxftype == "LINE":
                    start = Vec3(entity.dxf.start)
                    end = entity.dxf.end
                    if start.isclose(end):
                        self._designer.draw_point(start, properties)
                    else:  # direct draw by backend is OK!
                        self._designer.draw_line(start, end, properties)
                    pass
                elif dxftype == "CIRCLE":
                    self.draw_curve_entity(entity, properties)
                else:
                    raise ValueError(dxftype)

    def draw_solid_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        if isinstance(entity, Face3d):
            dxf = entity.dxf
            try:
                # this implementation supports all features of example file:
                # examples_dxf/3dface.dxf without changing the behavior of
                # Face3d.wcs_vertices() which removes the last vertex if
                # duplicated.
                points = [dxf.vtx0, dxf.vtx1, dxf.vtx2, dxf.vtx3, dxf.vtx0]
            except AttributeError:
                # all 4 vertices are required, otherwise the entity is invalid
                # for AutoCAD
                self.skip_entity(entity, "missing required vertex attribute")
                return
            edge_visibility = entity.get_edges_visibility()
            if all(edge_visibility):
                self._designer.draw_path(from_vertices(points), properties)
            else:
                for a, b, visible in zip(points, points[1:], edge_visibility):
                    if visible:
                        self._designer.draw_line(a, b, properties)

        elif isinstance(entity, Solid):
            # set solid fill type for SOLID and TRACE
            properties.filling = Filling()
            self._designer.draw_filled_polygon(
                entity.wcs_vertices(close=False), properties
            )

        else:
            raise TypeError("API error, requires a SOLID, TRACE or 3DFACE entity")

    def draw_hatch_pattern(
        self, polygon: DXFPolygon, paths: list[Path], properties: Properties
    ):
        if polygon.pattern is None or len(polygon.pattern.lines) == 0:
            return
        ocs = polygon.ocs()
        elevation = polygon.dxf.elevation.z
        properties.linetype_pattern = tuple()
        lines: list[tuple[Vec3, Vec3]] = []

        t0 = time.perf_counter()
        max_time = self.config.hatching_timeout

        def timeout() -> bool:
            if time.perf_counter() - t0 > max_time:
                print(
                    f"hatching timeout of {max_time}s reached for {str(polygon)} - aborting"
                )
                return True
            return False

        for baseline in hatching.pattern_baselines(polygon):
            for line in hatching.hatch_paths(baseline, paths, timeout):
                line_pattern = baseline.pattern_renderer(line.distance)
                for s, e in line_pattern.render(line.start, line.end):
                    if ocs.transform:
                        s, e = ocs.to_wcs((s.x, s.y, elevation)), ocs.to_wcs(
                            (e.x, e.y, elevation)
                        )
                    lines.append((s, e))
        self._designer.draw_solid_lines(lines, properties)

    def draw_hatch_entity(
        self,
        entity: DXFGraphic,
        properties: Properties,
        *,
        loops: Optional[list[Path]] = None,
    ) -> None:
        if properties.filling is None:
            return
        filling = properties.filling
        show_only_outline = False
        if self.config.hatch_policy == HatchPolicy.IGNORE:
            return
        elif self.config.hatch_policy == HatchPolicy.SHOW_SOLID:
            filling = Filling()  # solid filling
        elif self.config.hatch_policy == HatchPolicy.SHOW_OUTLINE:
            filling = Filling()  # solid filling
            show_only_outline = True

        polygon = cast(DXFPolygon, entity)
        if filling.type == Filling.PATTERN:
            if loops is None:
                loops = hatching.hatch_boundary_paths(polygon, filter_text_boxes=True)
            self.draw_hatch_pattern(polygon, loops, properties)
            return

        # draw SOLID filling
        ocs = polygon.ocs()
        # all OCS coordinates have the same z-axis stored as vector (0, 0, z),
        # default (0, 0, 0)
        elevation = entity.dxf.elevation.z

        external_paths: list[Path]
        holes: list[Path]

        if loops is not None:  # only MPOLYGON
            external_paths, holes = winding_deconstruction(  # type: ignore
                fast_bbox_detection(loops)
            )
        else:  # only HATCH
            paths = polygon.paths.rendering_paths(polygon.dxf.hatch_style)
            polygons: list = fast_bbox_detection(
                closed_loops(paths, ocs, elevation)  # type: ignore
            )
            external_paths, holes = winding_deconstruction(polygons)  # type: ignore

        if show_only_outline:
            for p in itertools.chain(ignore_text_boxes(external_paths), holes):
                self._designer.draw_path(p, properties)
            return

        if external_paths:
            self._designer.draw_filled_paths(
                ignore_text_boxes(external_paths), holes, properties
            )
        elif holes:
            # The first path is considered the exterior path, everything else are
            # holes.
            self._designer.draw_filled_paths([holes[0]], holes[1:], properties)

    def draw_mpolygon_entity(self, entity: DXFGraphic, properties: Properties):
        def resolve_fill_color() -> str:
            return self.ctx.resolve_aci_color(entity.dxf.fill_color, properties.layer)

        polygon = cast(DXFPolygon, entity)
        ocs = polygon.ocs()
        elevation: float = polygon.dxf.elevation.z
        offset = Vec3(polygon.dxf.get("offset_vector", NULLVEC))
        # MPOLYGON does not support hatch styles, all paths are rendered.
        loops = closed_loops(polygon.paths, ocs, elevation, offset)  # type: ignore

        line_color: str = properties.color
        assert properties.filling is not None
        pattern_name: str = properties.filling.name  # normalized pattern name
        # 1. draw filling
        if polygon.dxf.solid_fill:
            properties.filling.type = Filling.SOLID
            if polygon.gradient is not None and polygon.gradient.number_of_colors > 0:
                # true color filling is stored as gradient
                properties.color = str(properties.filling.gradient_color1)
            else:
                properties.color = resolve_fill_color()
            self.draw_hatch_entity(entity, properties, loops=loops)

        # checking properties.filling.type == Filling.PATTERN is not sufficient:
        elif pattern_name and pattern_name != "SOLID":
            # line color is also pattern color: properties.color
            self.draw_hatch_entity(entity, properties, loops=loops)

        # 2. draw boundary paths
        properties.color = line_color
        # draw boundary paths as lines
        for loop in loops:
            self._designer.draw_path(loop, properties)

    def draw_wipeout_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        wipeout = cast(Wipeout, entity)
        properties.filling = Filling()
        properties.color = self.ctx.current_layout_properties.background_color
        path = wipeout.boundary_path_wcs()
        self._designer.draw_filled_polygon(path, properties)

    def draw_viewport_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        assert isinstance(entity, Viewport)
        vp = entity
        if vp.dxf.get("status", 0) < 2:  # 0= off; 1= "active viewport"
            return

        if not vp.is_top_view:
            self.log_message("Cannot render non top-view viewports")
            return
        self._designer.draw_viewport(vp, self.ctx, self._bbox_cache)

    def draw_ole2frame_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        ole2frame = cast(OLE2Frame, entity)
        bbox = ole2frame.bbox()
        if not bbox.is_empty:
            self._draw_filled_rect(bbox.rect_vertices(), OLE2FRAME_COLOR)

    def _draw_filled_rect(
        self,
        points: Iterable[Vec2],
        color: str,
    ) -> None:
        props = Properties()
        props.color = color
        # default SOLID filling
        props.filling = Filling()
        self._designer.draw_filled_polygon(Vec3.list(points), props)

    def draw_mesh_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        builder = MeshBuilder.from_mesh(entity)  # type: ignore
        self.draw_mesh_builder_entity(builder, properties)

    def draw_mesh_builder_entity(
        self, builder: MeshBuilder, properties: Properties
    ) -> None:
        for face in builder.faces_as_vertices():
            self._designer.draw_path(
                from_vertices(face, close=True), properties=properties
            )

    def draw_polyline_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        dxftype = entity.dxftype()
        if dxftype == "POLYLINE":
            e = cast(Polyface, entity)
            if e.is_polygon_mesh or e.is_poly_face_mesh:
                # draw 3D mesh or poly-face entity
                self.draw_mesh_builder_entity(
                    MeshBuilder.from_polyface(e),
                    properties,
                )
                return

        entity = cast(Union[LWPolyline, Polyline], entity)
        is_lwpolyline = dxftype == "LWPOLYLINE"

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
                entity, segments=self.config.circle_approximation_count // 2
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
                self._designer.draw_filled_polygon(points, properties)
            return

        path = make_path(entity)
        self._designer.draw_path(path, properties)

    def draw_composite_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        def draw_insert(insert: Insert):
            self.draw_entities(insert.attribs)
            # draw_entities() includes the visibility check:
            self.draw_entities(
                insert.virtual_entities(
                    skipped_entity_callback=self.skip_entity
                    # TODO: redraw_order=True?
                )
            )

        if isinstance(entity, Insert):
            self.ctx.push_state(properties)
            if entity.mcount > 1:
                for virtual_insert in entity.multi_insert():
                    draw_insert(virtual_insert)
            else:
                draw_insert(entity)
            self.ctx.pop_state()
        elif isinstance(entity, SupportsVirtualEntities):
            # draw_entities() includes the visibility check:
            try:
                self.draw_entities(virtual_entities(entity))
            except ProxyGraphicError as e:
                print(str(e))
                print(POST_ISSUE_MSG)
        else:
            raise TypeError(entity.dxftype())

    def draw_proxy_graphic(self, data: bytes, doc) -> None:
        if data:
            try:
                self.draw_entities(virtual_entities(ProxyGraphic(data, doc)))
            except ProxyGraphicError as e:
                print(str(e))
                print(POST_ISSUE_MSG)


def is_spatial_text(extrusion: Vec3) -> bool:
    # note: the magnitude of the extrusion vector has no effect on text scale
    return not math.isclose(extrusion.x, 0) or not math.isclose(extrusion.y, 0)


def closed_loops(
    paths: list[AbstractBoundaryPath],
    ocs: OCS,
    elevation: float,
    offset: Vec3 = NULLVEC,
) -> list[Path]:
    loops = []
    for boundary in paths:
        path = from_hatch_boundary_path(boundary, ocs, elevation, offset)
        assert isinstance(
            path.user_data, const.BoundaryPathState
        ), "missing attached boundary path state"
        for sub_path in path.sub_paths():
            if len(sub_path):
                sub_path.close()
                loops.append(sub_path)
    return loops


def ignore_text_boxes(paths: Iterable[Path]) -> Iterable[Path]:
    """Filters text boxes from paths if BoundaryPathState() information is
    attached.
    """
    for path in paths:
        if (
            isinstance(path.user_data, const.BoundaryPathState)
            and path.user_data.textbox
        ):
            continue  # skip text box paths
        yield path


class Designer:
    """The designer is placed between the frontend and the backend
    and adds this features:

        - automatically linetype rendering
        - VIEWPORT rendering
        - foreground color mapping according Frontend.config.color_policy

    """

    def __init__(self, frontend: Frontend, backend: BackendInterface):
        self.frontend = frontend
        self.backend = backend
        self.config = frontend.config
        self.pattern_cache: dict[PatternKey, Sequence[float]] = dict()
        self.text_engine = UnifiedTextRenderer()
        self.default_font_face = fonts.FontFace()
        self.clipper = ClippingRect()
        self.current_vp_scale = 1.0
        self._current_entity_handle: str = ""
        self._color_mapping: dict[str, str] = dict()

    @property
    def vp_ltype_scale(self) -> float:
        """The linetype pattern should look the same in all viewports
        regardless of the viewport scale.
        """
        return 1.0 / max(self.current_vp_scale, 0.0001)  # max out at 1:10000

    def get_backend_properties(self, properties: Properties) -> BackendProperties:
        try:
            color = self._color_mapping[properties.color]
        except KeyError:
            color = apply_color_policy(
                properties.color, self.config.color_policy, self.config.custom_fg_color
            )
            self._color_mapping[properties.color] = color
        return BackendProperties(
            color,
            properties.lineweight,
            properties.layer,
            properties.pen,
            self._current_entity_handle,
        )

    def set_current_entity_handle(self, handle: str) -> None:
        assert handle is not None
        self._current_entity_handle = handle

    def draw_viewport(
        self,
        vp: Viewport,
        layout_ctx: RenderContext,
        bbox_cache: Optional[ezdxf.bbox.Cache] = None,
    ) -> None:
        """Draw the content of the given viewport current viewport.
        Returns ``False`` if the backend doesn't support viewports.
        """
        if vp.doc is None:
            return
        try:
            msp_limits = vp.get_modelspace_limits()
        except ValueError:  # modelspace limits not detectable
            return
        if self.enter_viewport(vp):
            _draw_entities(
                self.frontend,
                layout_ctx.from_viewport(vp),
                filter_vp_entities(vp.doc.modelspace(), msp_limits, bbox_cache),
            )
            self.exit_viewport()

    def enter_viewport(self, vp: Viewport) -> bool:
        """Set current viewport, returns ``True`` for valid viewports."""
        self.current_vp_scale = vp.get_scale()
        m = vp.get_transformation_matrix()
        clipping_path = make_path(vp)
        if len(clipping_path):
            self.clipper.push(clipping_path, m)
            return True
        return False

    def exit_viewport(self):
        self.clipper.pop()
        self.current_vp_scale = 1.0

    def draw_point(self, pos: AnyVec, properties: Properties) -> None:
        if self.clipper.is_active:
            point = self.clipper.clip_point(pos)
            if point is None:
                return
            pos = point
        self.backend.draw_point(pos, self.get_backend_properties(properties))

    def draw_line(self, start: AnyVec, end: AnyVec, properties: Properties):
        if (
            self.config.line_policy == LinePolicy.SOLID
            or len(properties.linetype_pattern) < 2  # CONTINUOUS
        ):
            if self.clipper.is_active:
                points = self.clipper.clip_line(start, end)
                if len(points) != 2:
                    return
                start, end = points
            self.backend.draw_line(start, end, self.get_backend_properties(properties))
        else:
            renderer = linetypes.LineTypeRenderer(self.pattern(properties))
            self.draw_solid_lines(  # includes transformation
                ((s, e) for s, e in renderer.line_segment(start, end)),
                properties,
            )

    def draw_solid_lines(
        self, lines: Iterable[tuple[AnyVec, AnyVec]], properties: Properties
    ) -> None:
        if self.clipper.is_active:
            clipped_lines: list[Sequence[AnyVec]] = []
            for start, end in lines:
                points = self.clipper.clip_line(start, end)
                if points:
                    clipped_lines.append(points)
            lines = clipped_lines  # type: ignore
        self.backend.draw_solid_lines(lines, self.get_backend_properties(properties))

    def draw_path(self, path: Path | Path2d, properties: Properties):
        if (
            self.config.line_policy == LinePolicy.SOLID
            or len(properties.linetype_pattern) < 2  # CONTINUOUS
        ):
            if self.clipper.is_active:
                for clipped_path in self.clipper.clip_paths(
                    [path], self.config.max_flattening_distance
                ):
                    self.backend.draw_path(
                        clipped_path, self.get_backend_properties(properties)
                    )
                return
            self.backend.draw_path(path, self.get_backend_properties(properties))
        else:
            renderer = linetypes.LineTypeRenderer(self.pattern(properties))
            vertices = path.flattening(self.config.max_flattening_distance, segments=16)
            self.draw_solid_lines(
                ((s, e) for s, e in renderer.line_segments(vertices)),
                properties,
            )

    def draw_filled_paths(
        self,
        paths: Iterable[Path | Path2d],
        holes: Iterable[Path | Path2d],
        properties: Properties,
    ) -> None:
        if self.clipper.is_active:
            max_sagitta = self.config.max_flattening_distance
            paths = self.clipper.clip_filled_paths(paths, max_sagitta)
            holes = self.clipper.clip_filled_paths(holes, max_sagitta)
        self.backend.draw_filled_paths(
            paths, holes, self.get_backend_properties(properties)
        )

    def draw_filled_polygon(
        self, points: Iterable[AnyVec], properties: Properties
    ) -> None:
        if self.clipper.is_active:
            points = self.clipper.clip_polygon(points)
        self.backend.draw_filled_polygon(
            points, self.get_backend_properties(properties)
        )

    def pattern(self, properties: Properties) -> Sequence[float]:
        """Get pattern - implements pattern caching."""
        if self.config.line_policy == LinePolicy.SOLID:
            scale = 0.0
        else:
            scale = properties.linetype_scale * self.vp_ltype_scale

        key: PatternKey = (properties.linetype_name, scale)
        pattern_ = self.pattern_cache.get(key)
        if pattern_ is None:
            pattern_ = self.create_pattern(properties, scale)
            self.pattern_cache[key] = pattern_
        return pattern_

    def create_pattern(self, properties: Properties, scale: float) -> Sequence[float]:
        """Returns simplified linetype tuple: on-off sequence"""
        if len(properties.linetype_pattern) < 2:
            # Do not return None -> None indicates: "not cached"
            return tuple()
        else:
            min_dash_length = self.config.min_dash_length * self.vp_ltype_scale
            pattern = [
                max(e * scale, min_dash_length) for e in properties.linetype_pattern
            ]
            if len(pattern) % 2:
                pattern.pop()
            return pattern

    def draw_text(
        self,
        text: str,
        transform: Matrix44,
        properties: Properties,
        cap_height: float,
        dxftype: str = "TEXT",
    ) -> None:
        if not text.strip():
            return  # no point rendering empty strings
        text = prepare_string_for_rendering(text, dxftype)
        font_face = properties.font
        if font_face is None:
            font_face = self.default_font_face
        try:
            text_path = self.text_engine.get_text_path(text, font_face, cap_height)
        except (RuntimeError, ValueError):
            return

        transformed_path = text_path.transform(transform)
        if self.text_engine.is_stroke_font(font_face):
            self.draw_path(transformed_path, properties)
            return
        polygons = fast_bbox_detection(single_paths([transformed_path]))  # type: ignore
        external_paths, holes = winding_deconstruction(polygons)  # type: ignore
        if properties.filling is None:
            properties.filling = Filling()
        self.draw_filled_paths(external_paths, holes, properties)  # type: ignore


def filter_vp_entities(
    msp: Layout,
    limits: Sequence[float],
    bbox_cache: Optional[ezdxf.bbox.Cache] = None,
) -> Iterator[DXFGraphic]:
    """Yields all DXF entities that need to be processed by the given viewport
    `limits`. The entities may be partially of even complete outside the viewport.
    By passing the bounding box cache of the modelspace entities,
    the function can filter entities outside the viewport to speed up rendering
    time.

    There are two processing modes for the `bbox_cache`:

        1. The `bbox_cache` is``None``: all entities must be processed,
           pass through mode
        2. If the `bbox_cache` is given but does not contain an entity,
           the bounding box is computed and added to the cache.
           Even passing in an empty cache can speed up rendering time when
           multiple viewports need to be processed.

    Args:
        msp: modelspace layout
        limits: modelspace limits of the viewport, as tuple (min_x, min_y, max_x, max_y)
        bbox_cache: the bounding box cache of the modelspace entities

    """

    # WARNING: this works only with top-view viewports
    # The current state of the drawing add-on supports only top-view viewports!
    def is_visible(e):
        entity_bbox = bbox_cache.get(e)
        if entity_bbox is None:
            # compute and add bounding box
            entity_bbox = ezdxf.bbox.extents((e,), fast=True, cache=bbox_cache)
        if not entity_bbox.has_data:
            return True
        # Check for separating axis:
        if min_x >= entity_bbox.extmax.x:
            return False
        if max_x <= entity_bbox.extmin.x:
            return False
        if min_y >= entity_bbox.extmax.y:
            return False
        if max_y <= entity_bbox.extmin.y:
            return False
        return True

    if bbox_cache is None:  # pass through all entities
        yield from msp
        return

    min_x, min_y, max_x, max_y = limits
    if not bbox_cache.has_data:
        # fill cache at once
        ezdxf.bbox.extents(msp, fast=True, cache=bbox_cache)

    for entity in msp:
        if is_visible(entity):
            yield entity


def _draw_entities(
    frontend: Frontend,
    ctx: RenderContext,
    entities: Iterable[DXFGraphic],
    *,
    filter_func: Optional[FilterFunc] = None,
) -> None:
    if filter_func is not None:
        entities = filter(filter_func, entities)
    for entity in entities:
        if not isinstance(entity, DXFGraphic):
            if frontend.config.proxy_graphic_policy != ProxyGraphicPolicy.IGNORE:
                entity = DXFGraphicProxy(entity)
            else:
                frontend.skip_entity(entity, "Cannot parse DXF entity")
                continue
        properties = ctx.resolve_all(entity)
        frontend.override_properties(entity, properties)
        if properties.is_visible:
            frontend.draw_entity(entity, properties)
        else:
            frontend.skip_entity(entity, "invisible")


def prepare_string_for_rendering(text: str, dxftype: str) -> str:
    assert "\n" not in text, "not a single line of text"
    if dxftype in {"TEXT", "ATTRIB", "ATTDEF"}:
        text = replace_non_printable_characters(text, replacement="?")
        text = text.replace("\t", "?")
    elif dxftype == "MTEXT":
        text = replace_non_printable_characters(text, replacement="▯")
        text = text.replace("\t", "        ")
    else:
        raise TypeError(dxftype)
    return text


def invert_color(color: Color) -> Color:
    r, g, b = hex_to_rgb(color)
    return rgb_to_hex((255 - r, 255 - g, 255 - b))


def swap_bw(color: str) -> Color:
    color = color.lower()
    if color == "#000000":
        return "#ffffff"
    if color == "#ffffff":
        return "#000000"
    return color


def color_to_monochrome(color: Color, invert=False) -> Color:
    lum = luminance(hex_to_rgb(color))
    if invert:
        gray = round((1.0 - lum) * 255)
    else:
        gray = round(lum * 255)
    return rgb_to_hex((gray, gray, gray))


def apply_color_policy(color: Color, policy: ColorPolicy, custom_color: Color) -> Color:
    alpha = color[7:9]
    color = color[:7]
    if policy == ColorPolicy.COLOR_SWAP_BW:
        color = swap_bw(color)
    elif policy == ColorPolicy.COLOR_NEGATIVE:
        color = invert_color(color)
    elif policy == ColorPolicy.MONOCHROME_WHITE_BG:
        color = color_to_monochrome(color, invert=True)
    elif policy == ColorPolicy.MONOCHROME_BLACK_BG:
        color = color_to_monochrome(color, invert=False)
    elif policy == ColorPolicy.BLACK:
        color = "#000000"
    elif policy == ColorPolicy.WHITE:
        color = "#ffffff"
    elif policy == ColorPolicy.CUSTOM:
        fg = custom_color
        color = fg[:7]
        alpha = fg[7:9]
    return color + alpha
