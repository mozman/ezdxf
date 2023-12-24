# Copyright (c) 2020-2023, Matthew Broadway
# License: MIT License
from __future__ import annotations
import math
from typing import (
    Iterable,
    cast,
    Union,
    Dict,
    Callable,
    Optional,
    TYPE_CHECKING,
)
from typing_extensions import TypeAlias
import logging
import time

import ezdxf.bbox
from ezdxf.addons.drawing.config import (
    Configuration,
    ProxyGraphicPolicy,
    HatchPolicy,
)
from ezdxf.addons.drawing.backend import BackendInterface
from ezdxf.addons.drawing.properties import (
    RenderContext,
    OLE2FRAME_COLOR,
    Properties,
    Filling,
    LayoutProperties,
)
from ezdxf.addons.drawing.config import BackgroundPolicy, TextPolicy
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.type_hints import FilterFunc
from ezdxf.addons.drawing.gfxproxy import DXFGraphicProxy
from ezdxf.addons.drawing.mtext_complex import complex_mtext_renderer
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
from ezdxf.math import Vec2, Vec3, OCS, NULLVEC
from ezdxf.path import (
    Path,
    make_path,
    from_hatch_boundary_path,
    from_vertices,
)
from ezdxf.render import MeshBuilder, TraceBuilder
from ezdxf import reorder
from ezdxf.proxygraphic import ProxyGraphic, ProxyGraphicError
from ezdxf.protocols import SupportsVirtualEntities, virtual_entities
from ezdxf.tools.text import has_inline_formatting_codes
from ezdxf.tools import text_layout
from ezdxf.lldxf import const
from ezdxf.render import hatching
from ezdxf.fonts import fonts
from .type_hints import Color

if TYPE_CHECKING:
    from .designer import Designer

__all__ = ["Frontend", "UniversalFrontend"]


TDispatchTable: TypeAlias = Dict[str, Callable[[DXFGraphic, Properties], None]]
POST_ISSUE_MSG = (
    "Please post sample DXF file at https://github.com/mozman/ezdxf/issues."
)
logger = logging.getLogger("ezdxf")


class UniversalFrontend:
    """Drawing frontend, responsible for decomposing entities into graphic
    primitives and resolving entity properties. Supports 2D and 3D backends.

    By passing the bounding box cache of the modelspace entities can speed up
    paperspace rendering, because the frontend can filter entities which are not
    visible in the VIEWPORT. Even passing in an empty cache can speed up
    rendering time when multiple viewports need to be processed.

    Args:
        ctx: the properties relevant to rendering derived from a DXF document
        designer: connection between frontend and backend
        config: settings to configure the drawing frontend and backend
        bbox_cache: bounding box cache of the modelspace entities or an empty
            cache which will be filled dynamically when rendering multiple
            viewports or ``None`` to disable bounding box caching at all

    """

    def __init__(
        self,
        ctx: RenderContext,
        designer: Designer,
        config: Configuration = Configuration(),
        bbox_cache: Optional[ezdxf.bbox.Cache] = None,
    ):
        # RenderContext contains all information to resolve resources for a
        # specific DXF document.
        self.ctx = ctx
        # the designer is the connection between frontend and backend
        self.designer = designer
        designer.set_draw_entities_callback(self.draw_entities_callback)
        self.config = ctx.update_configuration(config)
        designer.set_config(self.config)

        if self.config.pdsize is None or self.config.pdsize <= 0:
            self.log_message("relative point size is not supported")
            self.config = self.config.with_changes(pdsize=1)

        # Parents entities of current entity/sub-entity
        self.parent_stack: list[DXFGraphic] = []

        self._dispatch = self._build_dispatch_table()

        # Supported DXF entities which use only proxy graphic for rendering:
        self._proxy_graphic_only_entities: set[str] = {
            "MLEADER",  # todo: remove if MLeader.virtual_entities() is implemented
            "MULTILEADER",
            "ACAD_PROXY_ENTITY",
        }

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
        return self.designer.text_engine

    def _build_dispatch_table(self) -> TDispatchTable:
        dispatch_table: TDispatchTable = {
            "POINT": self.draw_point_entity,
            "HATCH": self.draw_hatch_entity,
            "MPOLYGON": self.draw_mpolygon_entity,
            "MESH": self.draw_mesh_entity,
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
            self.designer.finalize()

    def set_background(self, color: Color) -> None:
        policy = self.config.background_policy
        override = True
        if policy == BackgroundPolicy.DEFAULT:
            override = False
        elif policy == BackgroundPolicy.OFF:
            color = "#ffffff00"  # white, fully transparent
        elif policy == BackgroundPolicy.BLACK:
            color = "#000000"
        elif policy == BackgroundPolicy.WHITE:
            color = "#ffffff"
        elif policy == BackgroundPolicy.CUSTOM:
            color = self.config.custom_bg_color
        if override:
            self.ctx.current_layout_properties.set_colors(color)
        self.designer.set_background(color)

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

    def draw_entities_callback(
        self, ctx: RenderContext, entities: Iterable[DXFGraphic]
    ) -> None:
        _draw_entities(self, ctx, entities)

    def draw_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        """Draw a single DXF entity.

        Args:
            entity: DXF entity inherited from DXFGraphic()
            properties: resolved entity properties

        """
        self.designer.enter_entity(entity, properties)
        if not entity.is_virtual:
            # top level entity
            self.designer.set_current_entity_handle(entity.dxf.handle)
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

        self.designer.exit_entity(entity)

    def draw_line_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        d, dxftype = entity.dxf, entity.dxftype()
        if dxftype == "LINE":
            self.designer.draw_line(d.start, d.end, properties)

        elif dxftype in ("XLINE", "RAY"):
            start = d.start
            delta = d.unit_vector * self.config.infinite_line_length
            if dxftype == "XLINE":
                self.designer.draw_line(
                    start - delta / 2, start + delta / 2, properties
                )
            elif dxftype == "RAY":
                self.designer.draw_line(start, start + delta, properties)
        else:
            raise TypeError(dxftype)

    def draw_text_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        if self.config.text_policy == TextPolicy.IGNORE:
            return
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
            return self.designer.default_font_face
        return font_face

    def draw_text_entity_2d(self, entity: DXFGraphic, properties: Properties) -> None:
        if isinstance(entity, Text):
            for line, transform, cap_height in simplified_text_chunks(
                entity, self.text_engine, font_face=self.get_font_face(properties)
            ):
                self.designer.draw_text(
                    line, transform, properties, cap_height, entity.dxftype()
                )
        else:
            raise TypeError(entity.dxftype())

    def draw_text_entity_3d(self, entity: DXFGraphic, properties: Properties) -> None:
        self.skip_entity(entity, "3D text not supported")

    def draw_mtext_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        if self.config.text_policy == TextPolicy.IGNORE:
            return
        mtext = cast(MText, entity)
        if is_spatial_text(Vec3(mtext.dxf.extrusion)):
            self.skip_entity(mtext, "3D MTEXT not supported")
            return
        if mtext.has_columns or has_inline_formatting_codes(mtext.text):
            try:
                self.draw_complex_mtext(mtext, properties)
            except text_layout.LayoutError as e:
                print(f"skipping {str(mtext)} - {str(e)}")
        else:
            self.draw_simple_mtext(mtext, properties)

    def draw_simple_mtext(self, mtext: MText, properties: Properties) -> None:
        """Draw the content of a MTEXT entity without inline formatting codes."""
        for line, transform, cap_height in simplified_text_chunks(
            mtext, self.text_engine, font_face=self.get_font_face(properties)
        ):
            self.designer.draw_text(
                line, transform, properties, cap_height, mtext.dxftype()
            )

    def draw_complex_mtext(self, mtext: MText, properties: Properties) -> None:
        """Draw the content of a MTEXT entity including inline formatting codes."""
        complex_mtext_renderer(self.ctx, self.designer, mtext, properties)

    def draw_curve_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        try:
            path = make_path(entity)
        except AttributeError:  # API usage error
            raise TypeError(f"Unsupported DXF type {entity.dxftype()}")
        self.designer.draw_path(path, properties)

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
            self.designer.draw_point(entity.dxf.location, properties)
        else:
            for entity in point.virtual_entities(pdsize, pdmode):
                dxftype = entity.dxftype()
                if dxftype == "LINE":
                    start = entity.dxf.start
                    end = entity.dxf.end
                    if start.isclose(end):
                        self.designer.draw_point(start, properties)
                    else:  # direct draw by backend is OK!
                        self.designer.draw_line(start, end, properties)
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
                self.designer.draw_path(from_vertices(points), properties)
            else:
                for a, b, visible in zip(points, points[1:], edge_visibility):
                    if visible:
                        self.designer.draw_line(a, b, properties)

        elif isinstance(entity, Solid):
            # set solid fill type for SOLID and TRACE
            properties.filling = Filling()
            self.designer.draw_filled_polygon(
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

        for baseline in hatching.pattern_baselines(
            polygon,
            min_hatch_line_distance=self.config.min_hatch_line_distance,
            jiggle_origin=True,
        ):
            for line in hatching.hatch_paths(baseline, paths, timeout):
                line_pattern = baseline.pattern_renderer(line.distance)
                for s, e in line_pattern.render(line.start, line.end):
                    if ocs.transform:
                        s, e = ocs.to_wcs((s.x, s.y, elevation)), ocs.to_wcs(
                            (e.x, e.y, elevation)
                        )
                    lines.append((s, e))  # type: ignore
        self.designer.draw_solid_lines(lines, properties)

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
        hatch_policy = self.config.hatch_policy
        if hatch_policy == HatchPolicy.NORMAL:
            pass
        elif hatch_policy == HatchPolicy.IGNORE:
            return
        elif hatch_policy == HatchPolicy.SHOW_SOLID:
            filling = Filling()  # solid filling
        elif hatch_policy == HatchPolicy.SHOW_OUTLINE:
            filling = Filling()  # solid filling
            show_only_outline = True

        polygon = cast(DXFPolygon, entity)
        if filling.type == Filling.PATTERN:
            if loops is None:
                loops = hatching.hatch_boundary_paths(polygon, filter_text_boxes=True)
            try:
                self.draw_hatch_pattern(polygon, loops, properties)
            except hatching.DenseHatchingLinesError:
                pass  # fallthrough to solid fill rendering
            else:
                return

        # draw SOLID filling
        ocs = polygon.ocs()
        # all OCS coordinates have the same z-axis stored as vector (0, 0, z),
        # default (0, 0, 0)
        elevation = entity.dxf.elevation.z
        paths: list[Path]
        if loops is not None:  # only MPOLYGON
            paths = loops
        else:  # only HATCH
            boundary_paths = list(
                polygon.paths.rendering_paths(polygon.dxf.hatch_style)
            )
            paths = closed_loops(boundary_paths, ocs, elevation)
        if show_only_outline:
            for p in ignore_text_boxes(paths):
                self.designer.draw_path(p, properties)
            return
        if paths:
            self.designer.draw_filled_paths(ignore_text_boxes(paths), properties)

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
            self.designer.draw_path(loop, properties)

    def draw_wipeout_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        wipeout = cast(Wipeout, entity)
        properties.filling = Filling()
        properties.color = self.ctx.current_layout_properties.background_color
        clipping_polygon = wipeout.boundary_path_wcs()
        self.designer.draw_filled_polygon(clipping_polygon, properties)

    def draw_viewport(self, vp: Viewport) -> None:
        # the "active" viewport and invisible viewports should be filtered at this
        # stage, see function _draw_viewports()
        if vp.dxf.status < 1:
            return

        if not vp.is_top_view:
            self.log_message("Cannot render non top-view viewports")
            return
        self.designer.draw_viewport(vp, self.ctx, self._bbox_cache)

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
        self.designer.draw_filled_polygon(points, props)

    def draw_mesh_entity(self, entity: DXFGraphic, properties: Properties) -> None:
        builder = MeshBuilder.from_mesh(entity)  # type: ignore
        self.draw_mesh_builder_entity(builder, properties)

    def draw_mesh_builder_entity(
        self, builder: MeshBuilder, properties: Properties
    ) -> None:
        for face in builder.faces_as_vertices():
            self.designer.draw_path(
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
                    points = polygon
                # Set default SOLID filling for LWPOLYLINE
                properties.filling = Filling()
                self.designer.draw_filled_polygon(points, properties)
            return

        self.designer.draw_path(make_path(entity), properties)

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


class Frontend(UniversalFrontend):
    """Drawing frontend for 2D backends, responsible for decomposing entities into
    graphic primitives and resolving entity properties.

    By passing the bounding box cache of the modelspace entities can speed up
    paperspace rendering, because the frontend can filter entities which are not
    visible in the VIEWPORT. Even passing in an empty cache can speed up
    rendering time when multiple viewports need to be processed.

    Args:
        ctx: the properties relevant to rendering derived from a DXF document
        out: the 2D backend to draw to
        config: settings to configure the drawing frontend and backend
        bbox_cache: bounding box cache of the modelspace entities or an empty
            cache which will be filled dynamically when rendering multiple
            viewports or ``None`` to disable bounding box caching at all

    """

    def __init__(
        self,
        ctx: RenderContext,
        out: BackendInterface,
        config: Configuration = Configuration(),
        bbox_cache: Optional[ezdxf.bbox.Cache] = None,
    ):
        from .designer import Designer2d

        super().__init__(ctx, Designer2d(out), config, bbox_cache)


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


def _draw_entities(
    frontend: UniversalFrontend,
    ctx: RenderContext,
    entities: Iterable[DXFGraphic],
    *,
    filter_func: Optional[FilterFunc] = None,
) -> None:
    if filter_func is not None:
        entities = filter(filter_func, entities)
    viewports: list[Viewport] = []
    for entity in entities:
        if isinstance(entity, Viewport):
            viewports.append(entity)
            continue
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
    _draw_viewports(frontend, viewports)


def _draw_viewports(frontend: UniversalFrontend, viewports: list[Viewport]) -> None:
    # The VIEWPORT attributes "id" and "status" are very unreliable, maybe because of
    # the "great" documentation by Autodesk.
    # Viewport status field: (according to the DXF Reference)
    # -1 = On, but is fully off-screen, or is one of the viewports that is not
    #      active because the $MAXACTVP count is currently being exceeded.
    #  0 = Off
    # <positive value> = On and active. The value indicates the order of
    # stacking for the viewports, where 1 is the "active" viewport, 2 is the
    # next, and so on.
    viewports.sort(key=lambda e: e.dxf.status)
    # Remove all invisible viewports:
    viewports = [vp for vp in viewports if vp.dxf.status > 0]
    if not viewports:
        return
    # The "active" viewport determines how the paperspace layout is presented as a
    # whole (location & zoom state).
    # Maybe there are more than one "active" viewports, just remove the first one,
    # or there is no "active" viewport at all - in this case the "status" attribute
    # is not reliable at all - but what else is there to do?  The "active" layout should
    # have the id "1", but this information is also not reliable.
    if viewports[0].dxf.get("status", 1) == 1:
        viewports.pop(0)
    # Draw viewports in order of "status"
    for viewport in viewports:
        frontend.draw_viewport(viewport)
