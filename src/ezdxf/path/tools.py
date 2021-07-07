# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    List,
    Iterable,
    Tuple,
    Optional,
    Dict,
    Sequence,
)

import math
import itertools
from ezdxf.math import (
    Vec3,
    Z_AXIS,
    OCS,
    Matrix44,
    BoundingBox,
    ConstructionEllipse,
    cubic_bezier_from_ellipse,
    Bezier4P,
    Bezier3P,
    BSpline,
    reverse_bezier_curves,
    bulge_to_arc,
)

from ezdxf.query import EntityQuery

from .path import Path
from .commands import Command
from . import converter

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, Layout, EntityQuery

__all__ = [
    "bbox",
    "fit_paths_into_box",
    "transform_paths",
    "transform_paths_to_ocs",
    "render_lwpolylines",
    "render_polylines2d",
    "render_polylines3d",
    "render_lines",
    "render_hatches",
    "render_mpolygons",
    "render_splines_and_polylines",
    "add_bezier4p",
    "add_bezier3p",
    "add_ellipse",
    "add_2d_polyline",
    "add_spline",
    "to_multi_path",
    "single_paths",
    "have_close_control_vertices",
]

MAX_DISTANCE = 0.01
MIN_SEGMENTS = 4
G1_TOL = 1e-4
IS_CLOSE_TOL = 1e-10


def to_multi_path(paths: Iterable[Path]) -> Path:
    """Returns a multi-path object from all given paths and their sub-paths.

    .. versionadded:: 0.17

    """
    multi_path = Path()
    for p in paths:
        multi_path.extend_multi_path(p)
    return multi_path


def single_paths(paths: Iterable[Path]) -> Iterable[Path]:
    """Yields all given paths and their sub-paths as single path objects.

    .. versionadded:: 0.17

    """
    for p in paths:
        if p.has_sub_paths:
            yield from p.sub_paths()
        else:
            yield p


def transform_paths(paths: Iterable[Path], m: Matrix44) -> List[Path]:
    """Transform multiple :class:`Path` objects at once by transformation
    matrix `m`. Returns a list of the transformed :class:`Path` objects.

    Args:
        paths: iterable of :class:`Path` objects
        m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

    """

    def decompose(path: Path):
        vertices.append(path.start)
        commands.append(Command.START_PATH)
        for cmd in path:
            commands.extend(itertools.repeat(cmd.type, len(cmd)))
            vertices.extend(cmd)

    def rebuild(vertices):
        # localize variables:
        start_path, line_to, curve3_to, curve4_to, move_to = Command

        path = None
        collect = []
        for vertex, cmd in zip(vertices, commands):
            if cmd == start_path:
                if path is not None:
                    transformed_paths.append(path)
                path = Path(vertex)
            elif cmd == line_to:
                path.line_to(vertex)
            elif cmd == curve3_to:
                collect.append(vertex)
                if len(collect) == 2:
                    path.curve3_to(collect[0], collect[1])
                    collect.clear()
            elif cmd == curve4_to:
                collect.append(vertex)
                if len(collect) == 3:
                    path.curve4_to(collect[0], collect[1], collect[2])
                    collect.clear()
            elif cmd == move_to:
                path.move_to(vertex)

        if path is not None:
            transformed_paths.append(path)

    vertices = []
    commands = []
    transformed_paths = []

    for path in paths:
        decompose(path)
    if len(commands):
        rebuild(m.transform_vertices(vertices))
    return transformed_paths


def transform_paths_to_ocs(paths: Iterable[Path], ocs: OCS) -> List[Path]:
    """Transform multiple :class:`Path` objects at once from WCS to OCS.
    Returns a list of the transformed :class:`Path` objects.

    Args:
        paths: iterable of :class:`Path` objects
        ocs: OCS transformation of type :class:`~ezdxf.math.OCS`

    """
    t = ocs.matrix.copy()
    t.transpose()
    return transform_paths(paths, t)


def bbox(
    paths: Iterable[Path], flatten=0.01, segments: int = 16
) -> BoundingBox:
    """Returns the :class:`~ezdxf.math.BoundingBox` for the given paths.

    Args:
        paths: iterable of :class:`~ezdxf.path.Path` objects
        flatten: value != 0  for bounding box calculation from the flattened
            path and value == 0 for bounding box from the control vertices.
            Default value is 0.01 as max flattening distance.
        segments: minimal segment count for flattening

    """
    box = BoundingBox()
    for p in paths:
        if flatten:
            box.extend(p.flattening(distance=abs(flatten), segments=segments))
        else:
            box.extend(p.control_vertices())
    return box


def fit_paths_into_box(
    paths: Iterable[Path],
    size: Tuple[float, float, float],
    uniform: bool = True,
    source_box: BoundingBox = None,
) -> List[Path]:
    """Scale the given `paths` to fit into a box of the given `size`,
    so that all path vertices are inside this borders.
    If `source_box` is ``None`` the default source bounding box is calculated
    from the control points of the `paths`.

    `Note:` if the target size has a z-size of 0, the `paths` are
    projected into the xy-plane, same is true for the x-size, projects into
    the yz-plane and the y-size, projects into and xz-plane.

    Args:
        paths: iterable of :class:`~ezdxf.path.Path` objects
        size: target box size as tuple of x-, y- ond z-size values
        uniform: ``True`` for uniform scaling
        source_box: pass precalculated source bounding box, or ``None`` to
            calculate the default source bounding box from the control vertices

    """
    paths = list(paths)
    if len(paths) == 0:
        return paths
    if source_box is None:
        current_box = bbox(paths, flatten=0)
    else:
        current_box = source_box
    if not current_box.has_data or current_box.size == (0, 0, 0):
        return paths
    target_size = Vec3(size)
    if target_size == (0, 0, 0) or min(target_size) < 0:
        raise ValueError("invalid target size")

    if uniform:
        sx, sy, sz = _get_uniform_scaling(current_box.size, target_size)
    else:
        sx, sy, sz = _get_non_uniform_scaling(current_box.size, target_size)
    m = Matrix44.scale(sx, sy, sz)
    return transform_paths(paths, m)


def _get_uniform_scaling(current_size: Vec3, target_size: Vec3):
    TOL = 1e-6
    scale_x = math.inf
    if current_size.x > TOL and target_size.x > TOL:
        scale_x = target_size.x / current_size.x
    scale_y = math.inf
    if current_size.y > TOL and target_size.y > TOL:
        scale_y = target_size.y / current_size.y
    scale_z = math.inf
    if current_size.z > TOL and target_size.z > TOL:
        scale_z = target_size.z / current_size.z

    uniform_scale = min(scale_x, scale_y, scale_z)
    if uniform_scale is math.inf:
        raise ArithmeticError("internal error")
    scale_x = uniform_scale if target_size.x > TOL else 0
    scale_y = uniform_scale if target_size.y > TOL else 0
    scale_z = uniform_scale if target_size.z > TOL else 0
    return scale_x, scale_y, scale_z


def _get_non_uniform_scaling(current_size: Vec3, target_size: Vec3):
    TOL = 1e-6
    scale_x = 1.0
    if current_size.x > TOL:
        scale_x = target_size.x / current_size.x
    scale_y = 1.0
    if current_size.y > TOL:
        scale_y = target_size.y / current_size.y
    scale_z = 1.0
    if current_size.z > TOL:
        scale_z = target_size.z / current_size.z
    return scale_x, scale_y, scale_z


# Path to entity converter and render utilities:


def render_lwpolylines(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as
    :class:`~ezdxf.entities.LWPolyline` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    lwpolylines = list(
        converter.to_lwpolylines(
            paths,
            distance=distance,
            segments=segments,
            extrusion=extrusion,
            dxfattribs=dxfattribs,
        )
    )
    for lwpolyline in lwpolylines:
        layout.add_entity(lwpolyline)
    return EntityQuery(lwpolylines)


def render_polylines2d(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    distance: float = 0.01,
    segments: int = 4,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as 2D
    :class:`~ezdxf.entities.Polyline` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector.The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    polylines2d = list(
        converter.to_polylines2d(
            paths,
            distance=distance,
            segments=segments,
            extrusion=extrusion,
            dxfattribs=dxfattribs,
        )
    )
    for polyline2d in polylines2d:
        layout.add_entity(polyline2d)
    return EntityQuery(polylines2d)


def render_hatches(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    edge_path: bool = True,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    g1_tol: float = G1_TOL,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as
    :class:`~ezdxf.entities.Hatch` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        edge_path: ``True`` for edge paths build of LINE and SPLINE edges,
            ``False`` for only LWPOLYLINE paths as boundary paths
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve to flatten polyline paths
        g1_tol: tolerance for G1 continuity check to separate SPLINE edges
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    hatches = list(
        converter.to_hatches(
            paths,
            edge_path=edge_path,
            distance=distance,
            segments=segments,
            g1_tol=g1_tol,
            extrusion=extrusion,
            dxfattribs=dxfattribs,
        )
    )
    for hatch in hatches:
        layout.add_entity(hatch)
    return EntityQuery(hatches)


def render_mpolygons(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as
    :class:`~ezdxf.entities.MPolygon` entities. The MPOLYGON entity supports
    only polyline boundary paths. All curves will be approximated.

    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve to flatten polyline paths
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.17

    """
    polygons = list(
        converter.to_mpolygons(
            paths,
            distance=distance,
            segments=segments,
            extrusion=extrusion,
            dxfattribs=dxfattribs,
        )
    )
    for polygon in polygons:
        layout.add_entity(polygon)
    return EntityQuery(polygons)


def render_polylines3d(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as 3D
    :class:`~ezdxf.entities.Polyline` entities.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """

    polylines3d = list(
        converter.to_polylines3d(
            paths,
            distance=distance,
            segments=segments,
            dxfattribs=dxfattribs,
        )
    )
    for polyline3d in polylines3d:
        layout.add_entity(polyline3d)
    return EntityQuery(polylines3d)


def render_lines(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as
    :class:`~ezdxf.entities.Line` entities.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    lines = list(
        converter.to_lines(
            paths,
            distance=distance,
            segments=segments,
            dxfattribs=dxfattribs,
        )
    )
    for line in lines:
        layout.add_entity(line)
    return EntityQuery(lines)


def render_splines_and_polylines(
    layout: "Layout",
    paths: Iterable[Path],
    *,
    g1_tol: float = G1_TOL,
    dxfattribs: Optional[Dict] = None
) -> EntityQuery:
    """Render the given `paths` into `layout` as :class:`~ezdxf.entities.Spline`
    and 3D :class:`~ezdxf.entities.Polyline` entities.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        g1_tol: tolerance for G1 continuity check
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    entities = list(
        converter.to_splines_and_polylines(
            paths,
            g1_tol=g1_tol,
            dxfattribs=dxfattribs,
        )
    )
    for entity in entities:
        layout.add_entity(entity)
    return EntityQuery(entities)


def add_ellipse(
    path: Path, ellipse: ConstructionEllipse, segments=1, reset=True
) -> None:
    """Add an elliptical arc as multiple cubic Bèzier-curves to the given
    `path`, use :meth:`~ezdxf.math.ConstructionEllipse.from_arc` constructor
    of class :class:`~ezdxf.math.ConstructionEllipse` to add circular arcs.

    Auto-detect the connection point to the given `path`, if neither the start-
    nor the end point of the ellipse is close to the path end point, a line from
    the path end point to the ellipse start point will be added automatically
    (see :func:`add_bezier4p`).

    By default the start of an **empty** path is set to the start point of
    the ellipse, setting argument `reset` to ``False`` prevents this
    behavior.

    Args:
        path: :class:`~ezdxf.path.Path` object
        ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse`
            object
        segments: count of Bèzier-curve segments, at least one segment for
            each quarter (pi/2), ``1`` for as few as possible.
        reset: set start point to start of ellipse if path is empty

    """
    if abs(ellipse.param_span) < 1e-9:
        return
    if len(path) == 0 and reset:
        path.start = ellipse.start_point
    add_bezier4p(path, cubic_bezier_from_ellipse(ellipse, segments))


def add_bezier4p(path: Path, curves: Iterable[Bezier4P]) -> None:
    """Add multiple cubic Bèzier-curves to the given `path`.

    Auto-detect the connection point to the given `path`, if neither the start-
    nor the end point of the curves is close to the path end point, a line from
    the path end point to the start point of the first curve will be added
    automatically.

    .. versionchanged:: 0.16.2

        add linear Bézier curve segments as LINE_TO commands

    """
    rel_tol = 1e-15
    abs_tol = 0.0
    curves = list(curves)
    if not len(curves):
        return
    end = curves[-1].control_points[-1]
    if path.end.isclose(end):
        # connect to new curves end point
        curves = reverse_bezier_curves(curves)

    for curve in curves:
        start, ctrl1, ctrl2, end = curve.control_points
        if not start.isclose(path.end):
            path.line_to(start)

        # add linear bezier segments as LINE_TO commands
        if start.isclose(
            ctrl1, rel_tol=rel_tol, abs_tol=abs_tol
        ) and end.isclose(ctrl2, rel_tol=rel_tol, abs_tol=abs_tol):
            path.line_to(end)
        else:
            path.curve4_to(end, ctrl1, ctrl2)


def add_bezier3p(path: Path, curves: Iterable[Bezier3P]) -> None:
    """Add multiple quadratic Bèzier-curves to the given `path`.

    Auto-detect the connection point to the given `path`, if neither the start-
    nor the end point of the curves is close to the path end point, a line from
    the path end point to the start point of the first curve will be added
    automatically.

    .. versionchanged:: 0.16.2

        add linear Bézier curve segments as LINE_TO commands

    """
    rel_tol = 1e-15
    abs_tol = 0.0
    curves = list(curves)
    if not len(curves):
        return
    end = curves[-1].control_points[-1]
    if path.end.isclose(end):
        # connect to new curves end point
        curves = reverse_bezier_curves(curves)

    for curve in curves:
        start, ctrl, end = curve.control_points
        if not start.isclose(path.end, rel_tol=rel_tol, abs_tol=abs_tol):
            path.line_to(start)

        if start.isclose(ctrl, rel_tol=rel_tol, abs_tol=abs_tol) or end.isclose(
            ctrl, rel_tol=rel_tol, abs_tol=abs_tol
        ):
            path.line_to(end)
        else:
            path.curve3_to(end, ctrl)


def add_2d_polyline(
    path: Path,
    points: Iterable[Sequence[float]],
    close: bool,
    ocs: OCS,
    elevation: float,
) -> None:
    """Internal API to add 2D polylines which may include bulges to an
    **empty** path.

    """

    def bulge_to(p1: Vec3, p2: Vec3, bulge: float):
        if p1.isclose(p2, rel_tol=IS_CLOSE_TOL, abs_tol=0):
            return
        center, start_angle, end_angle, radius = bulge_to_arc(p1, p2, bulge)
        ellipse = ConstructionEllipse.from_arc(
            center,
            radius,
            Z_AXIS,
            math.degrees(start_angle),
            math.degrees(end_angle),
        )
        curves = list(cubic_bezier_from_ellipse(ellipse))
        curve0 = curves[0]
        cp0 = curve0.control_points[0]
        if cp0.isclose(p2, rel_tol=IS_CLOSE_TOL, abs_tol=0):
            curves = reverse_bezier_curves(curves)
        add_bezier4p(path, curves)

    if len(path):
        raise ValueError("Requires an empty path.")

    prev_point = None
    prev_bulge = 0
    for x, y, bulge in points:
        # Bulge values near 0 but != 0 cause crashes! #329
        if abs(bulge) < 1e-6:
            bulge = 0
        point = Vec3(x, y)
        if prev_point is None:
            path.start = point
            prev_point = point
            prev_bulge = bulge
            continue

        if prev_bulge:
            bulge_to(prev_point, point, prev_bulge)
        else:
            path.line_to(point)
        prev_point = point
        prev_bulge = bulge

    if close and not path.start.isclose(
        path.end, rel_tol=IS_CLOSE_TOL, abs_tol=0
    ):
        if prev_bulge:
            bulge_to(path.end, path.start, prev_bulge)
        else:
            path.line_to(path.start)

    if ocs.transform or elevation:
        path.to_wcs(ocs, elevation)


def add_spline(path: Path, spline: BSpline, level=4, reset=True) -> None:
    """Add a B-spline as multiple cubic Bèzier-curves.

    Non-rational B-splines of 3rd degree gets a perfect conversion to
    cubic bezier curves with a minimal count of curve segments, all other
    B-spline require much more curve segments for approximation.

    Auto-detect the connection point to the given `path`, if neither the start-
    nor the end point of the B-spline is close to the path end point, a line
    from the path end point to the start point of the B-spline will be added
    automatically. (see :meth:`add_bezier4p`).

    By default the start of an **empty** path is set to the start point of
    the spline, setting argument `reset` to ``False`` prevents this
    behavior.

    Args:
        path: :class:`~ezdxf.path.Path` object
        spline: B-spline parameters as :class:`~ezdxf.math.BSpline` object
        level: subdivision level of approximation segments
        reset: set start point to start of spline if path is empty

    """
    if len(path) == 0 and reset:
        path.start = spline.point(0)
    if spline.degree == 3 and not spline.is_rational and spline.is_clamped:
        curves = [Bezier4P(points) for points in spline.bezier_decomposition()]
    else:
        curves = spline.cubic_bezier_approximation(level=level)
    add_bezier4p(path, curves)


def have_close_control_vertices(
    a: Path, b: Path, *, rel_tol=1e-9, abs_tol=1e-12
) -> bool:
    """Returns ``True`` if the control vertices of given paths are close.

    .. versionadded:: 0.16.5

    """
    return all(
        cp_a.isclose(cp_b, rel_tol=rel_tol, abs_tol=abs_tol)
        for cp_a, cp_b in zip(a.control_vertices(), b.control_vertices())
    )
