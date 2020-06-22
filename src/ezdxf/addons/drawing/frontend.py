# Created: 06.2020
# Copyright (c) 2020, Matthew Broadway
# License: MIT License
import copy
import math
from math import radians
from typing import Set, Optional, Iterable, cast, Union, Callable, Tuple, List

from ezdxf.addons.drawing.backend_interface import DrawingBackend
from ezdxf.addons.drawing.colors import ColorContext, VIEWPORT_COLOR
from ezdxf.addons.drawing.text import simplified_text_chunks
from ezdxf.addons.drawing.type_hints import LayerName, Color
from ezdxf.addons.drawing.utils import normalize_angle, get_rotation_direction_from_extrusion_vector, \
    get_draw_angles, get_tri_or_quad_points
from ezdxf.entities import DXFGraphic, Insert, MText, Dimension, Polyline, LWPolyline, Face3d, Mesh, Solid, Trace, \
    Spline, Hatch, Attrib, Text
from ezdxf.layouts import Layout
from ezdxf.math import Vector

INFINITE_LINE_LENGTH = 25

LINE_ENTITY_TYPES = {'LINE', 'XLINE', 'RAY', 'MESH'}
TEXT_ENTITY_TYPES = {'TEXT', 'MTEXT', 'ATTRIB'}
CURVE_ENTITY_TYPES = {'CIRCLE', 'ARC', 'ELLIPSE', 'SPLINE'}
MISC_ENTITY_TYPES = {'POINT', '3DFACE', 'SOLID', 'TRACE', 'MESH', 'HATCH', 'VIEWPORT'}
COMPOSITE_ENTITY_TYPES = {'INSERT', 'POLYLINE', 'LWPOLYLINE'}  # and DIMENSION*


def _draw_line_entity(entity: DXFGraphic, color: Color, out: DrawingBackend) -> None:
    d, dxftype = entity.dxf, entity.dxftype()

    if dxftype == 'LINE':
        out.draw_line(d.start, d.end, color)

    elif dxftype in ('XLINE', 'RAY'):
        start = d.start
        delta = Vector(d.unit_vector.x, d.unit_vector.y, 0) * INFINITE_LINE_LENGTH
        if dxftype == 'XLINE':
            out.draw_line(start - delta / 2, start + delta / 2, color)
        elif dxftype == 'RAY':
            out.draw_line(start, start + delta, color)

    elif dxftype == 'MESH':
        entity = cast(Mesh, entity)
        data = entity.get_data()  # unpack into more readable format
        points = [Vector(x, y, z) for x, y, z in data.vertices]
        for a, b in data.edges:
            out.draw_line(points[a], points[b], color)

    else:
        raise TypeError(dxftype)


def _draw_text_entity(entity: DXFGraphic, color: Color, out: DrawingBackend) -> None:
    d, dxftype = entity.dxf, entity.dxftype()

    if dxftype in ('TEXT', 'MTEXT', 'ATTRIB'):
        entity = cast(Union[Text, MText, Attrib], entity)
        for line, transform, cap_height in simplified_text_chunks(entity, out):
            out.draw_text(line, transform, color, cap_height)
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


def _draw_curve_entity(entity: DXFGraphic, color: Color, out: DrawingBackend) -> None:
    d, dxftype = entity.dxf, entity.dxftype()

    if dxftype == 'CIRCLE':
        center = _get_arc_wcs_center(entity)
        diameter = 2 * d.radius
        out.draw_arc(center, diameter, diameter, 0, None, color)

    elif dxftype == 'ARC':
        center = _get_arc_wcs_center(entity)
        diameter = 2 * d.radius
        direction = get_rotation_direction_from_extrusion_vector(d.extrusion)
        draw_angles = get_draw_angles(direction, radians(d.start_angle), radians(d.end_angle))
        out.draw_arc(center, diameter, diameter, 0, draw_angles, color)

    elif dxftype == 'ELLIPSE':
        # 'param' angles are anticlockwise around the extrusion vector
        # 'param' angles are relative to the major axis angle
        # major axis angle always anticlockwise in global frame
        major_axis_angle = normalize_angle(math.atan2(d.major_axis.y, d.major_axis.x))
        width = 2 * d.major_axis.magnitude
        height = d.ratio * width  # ratio == height / width
        direction = get_rotation_direction_from_extrusion_vector(d.extrusion)
        draw_angles = get_draw_angles(direction, d.start_param, d.end_param)
        out.draw_arc(d.center, width, height, major_axis_angle, draw_angles, color)

    elif dxftype == 'SPLINE':
        entity = cast(Spline, entity)
        spline = entity.construction_tool()
        if out.has_spline_support:
            out.draw_spline(spline, color)
        else:
            points = list(spline.approximate(segments=100))
            out.start_polyline()
            for a, b in zip(points, points[1:]):
                out.draw_line(a, b, color)
            out.end_polyline()

    else:
        raise TypeError(dxftype)


def _draw_misc_entity(entity: DXFGraphic, color: Color, out: DrawingBackend) -> None:
    d, dxftype = entity.dxf, entity.dxftype()

    if dxftype == 'POINT':
        out.draw_point(d.location, color)

    elif dxftype in ('3DFACE', 'SOLID', 'TRACE'):
        # TRACE is the same thing as SOLID according to the documentation
        # https://ezdxf.readthedocs.io/en/stable/dxfentities/trace.html
        # except TRACE has OCS coordinates and SOLID has WCS coordinates.
        entity = cast(Union[Face3d, Solid, Trace], entity)
        points = get_tri_or_quad_points(entity)
        if dxftype == 'TRACE' and d.hasattr('extrusion'):
            ocs = entity.ocs()
            points = list(ocs.points_to_wcs(points))
        if dxftype in ('SOLID', 'TRACE'):
            out.draw_filled_polygon(points, color)
        else:
            for a, b in zip(points, points[1:]):
                out.draw_line(a, b, color)

    elif dxftype == 'HATCH':
        entity = cast(Hatch, entity)
        if out.has_hatch_support:
            out.draw_hatch(entity, color)
            return

        ocs = entity.ocs()
        # all OCS coordinates have the same z-axis stored as vector (0, 0, z), default (0, 0, 0)
        elevation = entity.dxf.elevation.z
        paths = copy.deepcopy(entity.paths)
        paths.polyline_to_edge_path(just_with_bulge=False)
        paths.all_to_line_edges(spline_factor=10)
        for p in paths:
            assert p.PATH_TYPE == 'EdgePath'
            vertices = []
            last_vertex = None
            for e in p.edges:
                assert e.EDGE_TYPE == 'LineEdge'
                # WCS transformation is only done if the extrusion vector is != (0, 0, 1)
                # else to_wcs() returns just the input - no big speed penalty!
                # Simple projection into xy-plane by just removing the z-axis from
                # WCS vector, assuming we do not support 3D hatches!?
                v = ocs.to_wcs(Vector(e.start[0], e.start[1], elevation)).replace(z=0.0)
                if last_vertex is not None and not last_vertex.isclose(v):
                    print(f'warning: hatch edges not contiguous: {last_vertex} -> {e.start}, {e.end}')
                    vertices.append(last_vertex)
                vertices.append(v)
                last_vertex = ocs.to_wcs(Vector(e.end[0], e.end[1], elevation)).replace(z=0.0)
            if vertices:
                if last_vertex.isclose(vertices[0]):
                    vertices.append(last_vertex)
                out.draw_filled_polygon(vertices, color)

    elif dxftype == 'VIEWPORT':
        view_vector: Vector = d.view_direction_vector
        mag = view_vector.magnitude
        if math.isclose(mag, 0.0):
            print('warning: viewport with null view vector')
            return
        view_vector /= mag
        if not math.isclose(view_vector.dot(Vector(0, 0, 1)), 1.0):
            print(f'cannot render viewport with non-perpendicular view direction: {d.view_direction_vector}')
            return

        cx, cy = d.center.x, d.center.y
        dx = d.width / 2
        dy = d.height / 2
        minx, miny = cx - dx, cy - dy
        maxx, maxy = cx + dx, cy + dy
        points = [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]
        out.draw_filled_polygon([Vector(x, y, 0) for x, y in points], VIEWPORT_COLOR)

    else:
        raise TypeError(dxftype)


def _draw_composite_entity(entity: DXFGraphic,
                           colors: ColorContext,
                           out: DrawingBackend,
                           parent_stack: List[DXFGraphic],
                           **kwargs) -> None:
    dxftype = entity.dxftype()

    if dxftype == 'INSERT':
        entity = cast(Insert, entity)
        colors.push_state(colors.get_entity_color(entity), entity.dxf.layer.lower())
        parent_stack.append(entity)
        for attrib in entity.attribs:
            draw_entity(attrib, colors, out, parent_stack, **kwargs)
        try:
            children = list(entity.virtual_entities())
        except Exception as e:
            print(f'Exception {type(e)}({e}) failed to get children of insert entity: {e}')
            return
        for child in children:
            draw_entity(child, colors, out, parent_stack, **kwargs)
        parent_stack.pop()
        colors.pop_state()

    elif 'DIMENSION' in dxftype:  # several different dxftypes
        if not isinstance(entity, Dimension):
            print(f'warning: ignoring unknown DIMENSION entitiy {dxftype} {type(entity)}')
            return
        entity = cast(Dimension, entity)

        children = []
        try:
            for child in entity.virtual_entities():
                child.transparency = 0.0  # defaults to 1.0 (fully transparent)
                children.append(child)
        except Exception as e:
            print(f'Exception {type(e)}({e}) failed to get children of dimension entity: {e}')
            return

        parent_stack.append(entity)
        for child in children:
            draw_entity(child, colors, out, parent_stack, **kwargs)
        parent_stack.pop()

    elif dxftype in ('LWPOLYLINE', 'POLYLINE'):
        entity = cast(Union[LWPolyline, Polyline], entity)
        parent_stack.append(entity)
        out.start_polyline()
        for child in entity.virtual_entities():
            draw_entity(child, colors, out, parent_stack, **kwargs)
        parent_stack.pop()

        out.set_current_entity(entity, tuple(parent_stack))
        out.end_polyline()
        out.set_current_entity(None)

    else:
        raise TypeError(dxftype)


def draw_entity(entity: DXFGraphic, colors: ColorContext, out: DrawingBackend, parent_stack: List[DXFGraphic],
                *, visible_layers: Optional[Set[LayerName]] = None) -> None:
    """
    Args:
        visible_layers: warning: unlike draw_entities, this function does not convert layer names to lowercase,
          so the user of this function must ensure that they convert the layer names beforehand.
    """
    if not _is_visible(entity, visible_layers, colors.insert_layer):
        return

    color = colors.get_entity_color(entity)
    dxftype = entity.dxftype()
    out.set_current_entity(entity, tuple(parent_stack))
    if dxftype in LINE_ENTITY_TYPES:
        _draw_line_entity(entity, color, out)
    elif dxftype in TEXT_ENTITY_TYPES:
        _draw_text_entity(entity, color, out)
    elif dxftype in CURVE_ENTITY_TYPES:
        _draw_curve_entity(entity, color, out)
    elif dxftype in MISC_ENTITY_TYPES:
        _draw_misc_entity(entity, color, out)
    elif dxftype in COMPOSITE_ENTITY_TYPES or 'DIMENSION' in dxftype:
        _draw_composite_entity(entity, colors, out, parent_stack, visible_layers=visible_layers)
    else:
        out.ignored_entity(entity, colors)
    out.set_current_entity(None)


def _is_visible(entity: DXFGraphic, visible_layers: Optional[Set[LayerName]], insert_layer: Optional[LayerName]) -> bool:
    if visible_layers is None:
        return True
    layer = entity.dxf.layer.lower()
    if insert_layer is not None and layer == '0':
        return insert_layer in visible_layers
    else:
        return layer in visible_layers


def draw_entities(entities: Iterable[DXFGraphic], colors: ColorContext, out: DrawingBackend,
                  visible_layers: Optional[Set[LayerName]] = None) -> None:
    if visible_layers is not None:
        visible_layers = {l.lower() for l in visible_layers}
    for entity in entities:
        draw_entity(entity, colors, out, [], visible_layers=visible_layers)


def draw_layout(layout: Layout,
                out: DrawingBackend,
                visible_layers: Optional[Set[LayerName]] = None,
                finalise: bool = True) -> None:
    colors = ColorContext(layout)
    entities = layout.entity_space
    draw_entities(entities, colors, out, visible_layers)
    out.set_background(colors.get_layout_background_color(layout))
    if finalise:
        out.finalize()


