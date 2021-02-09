# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable, Tuple, Optional, Dict

import math
import itertools
from ezdxf.math import  Vec3, Z_AXIS, OCS,Matrix44, BoundingBox

from ezdxf.query import EntityQuery

from .path import Path, Command

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, Layout, EntityQuery

__all__ = [
    'bbox', 'fit_paths_into_box', 'transform_paths', 'transform_paths_to_ocs',
    'render_lwpolylines', 'render_polylines2d', 'render_polylines3d',
    'render_lines', 'render_hatches', 'render_splines_and_polylines'
]

MAX_DISTANCE = 0.01
MIN_SEGMENTS = 4
G1_TOL = 1e-4


def transform_paths(paths: Iterable[Path], m: Matrix44) -> List[Path]:
    """ Transform multiple :class:`Path` objects at once. Returns a list of
    the transformed :class:`Path` objects.

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
        path = None
        collect = []
        for vertex, cmd in zip(vertices, commands):
            if cmd == Command.START_PATH:
                if path is not None:
                    transformed_paths.append(path)
                path = Path(vertex)
            elif cmd == Command.LINE_TO:
                path.line_to(vertex)
            elif cmd == Command.CURVE3_TO:
                collect.append(vertex)
                if len(collect) == 2:
                    path.curve3_to(collect[0], collect[1])
                    collect.clear()
            elif cmd == Command.CURVE4_TO:
                collect.append(vertex)
                if len(collect) == 3:
                    path.curve4_to(collect[0], collect[1], collect[2])
                    collect.clear()
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
    """ Transform multiple :class:`Path` objects at once from WCS to OCS.
    Returns a list of the transformed :class:`Path` objects.

    Args:
        paths: iterable of :class:`Path` objects
        ocs: OCS transformation of type :class:`~ezdxf.math.OCS`

    """
    t = ocs.matrix.copy()
    t.transpose()
    return transform_paths(paths, t)


def bbox(paths: Iterable[Path], precise=True,
         distance: float = 0.01,
         segments: int = 16) -> BoundingBox:
    """ Returns the :class:`~ezdxf.math.BoundingBox` for given paths.

    Args:
        paths: iterable of :class:`~ezdxf.render.path.Path` objects
        precise: ``True`` for bounding box of the flattened path and ``False``
            for bounding box of the control vertices.
        distance: flattening distance, default is 0.01
        segments: minimal segment count for flattening

    """
    box = BoundingBox()
    for p in paths:
        if precise:
            box.extend(p.flattening(distance, segments=segments))
        else:
            box.extend(p.control_vertices())
    return box


def fit_paths_into_box(paths: Iterable[Path],
                       size: Tuple[float, float, float],
                       uniform: bool = True,
                       source_box: BoundingBox = None) -> List[Path]:
    """ Scale the given `paths` to fit into a box of the given `size`,
    so that all path vertices are inside this borders.
    If `source_box` is ``None`` the default source bounding box is calculated
    from the control points of the `paths`.

    `Note:` if the target size has a z-size of 0, the `paths` are
    projected into the xy-plane, same is true for the x-size, projects into
    the yz-plane and the y-size, projects into and xz-plane.

    Args:
        paths: iterable of :class:`~ezdxf.render.path.Path` objects
        size: target box size as tuple of x-, y- ond z-size values
        uniform: ``True`` for uniform scaling
        source_box: pass precalculated source bounding box, or ``None`` to
            calculate the default source bounding box from the control vertices

    """
    paths = list(paths)
    if len(paths) == 0:
        return paths
    if source_box is None:
        current_box = bbox(paths, precise=False)
    else:
        current_box = source_box
    if not current_box.has_data or current_box.size == (0, 0, 0):
        return paths
    target_size = Vec3(size)
    if target_size == (0, 0, 0) or min(target_size) < 0:
        raise ValueError('invalid target size')

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
        raise ArithmeticError('internal error')
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
        layout: 'Layout',
        paths: Iterable[Path],
        *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> EntityQuery:
    """ Render given `paths` into `layout` as
    :class:`~ezdxf.entities.LWPolyline` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The plane elevation is defined by the distance of the
    start point of the first path to the WCS origin.

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
    lwpolylines = list(to_lwpolylines(
        paths,
        distance=distance,
        segments=segments,
        extrusion=extrusion,
        dxfattribs=dxfattribs,
    ))
    for lwpolyline in lwpolylines:
        layout.add_entity(lwpolyline)
    return EntityQuery(lwpolylines)


def render_polylines2d(
        layout: 'Layout',
        paths: Iterable[Path],
        *,
        distance: float = 0.01,
        segments: int = 4,
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> EntityQuery:
    """ Render given `paths` into `layout` as 2D
    :class:`~ezdxf.entities.Polyline` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The plane elevation is defined by the distance of the
    start point of the first path to the WCS origin.

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
    polylines2d = list(to_polylines2d(
        paths,
        distance=distance,
        segments=segments,
        extrusion=extrusion,
        dxfattribs=dxfattribs,
    ))
    for polyline2d in polylines2d:
        layout.add_entity(polyline2d)
    return EntityQuery(polylines2d)


def render_hatches(
        layout: 'Layout',
        paths: Iterable[Path],
        *,
        edge_path: bool = True,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        g1_tol: float = G1_TOL,
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> EntityQuery:
    """ Render given `paths` into `layout` as
    :class:`~ezdxf.entities.Hatch` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The plane elevation is defined by the distance of the
    start point of the first path to the WCS origin.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        edge_path: ``True`` for edge paths build of LINE and SPLINE edges,
            ``False`` for only LWPOLYLINE paths as boundary paths
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve to flatten LWPOLYLINE paths
        g1_tol: tolerance for G1 continuity check to separate SPLINE edges
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    hatches = list(to_hatches(
        paths,
        edge_path=edge_path,
        distance=distance,
        segments=segments,
        g1_tol=g1_tol,
        extrusion=extrusion,
        dxfattribs=dxfattribs,
    ))
    for hatch in hatches:
        layout.add_entity(hatch)
    return EntityQuery(hatches)


def render_polylines3d(
        layout: 'Layout',
        paths: Iterable[Path],
        *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        dxfattribs: Optional[Dict] = None) -> EntityQuery:
    """ Render given `paths` into `layout` as 3D
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

    polylines3d = list(to_polylines3d(
        paths,
        distance=distance,
        segments=segments,
        dxfattribs=dxfattribs,
    ))
    for polyline3d in polylines3d:
        layout.add_entity(polyline3d)
    return EntityQuery(polylines3d)


def render_lines(
        layout: 'Layout',
        paths: Iterable[Path],
        *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        dxfattribs: Optional[Dict] = None) -> EntityQuery:
    """ Render given `paths` into `layout` as
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
    lines = list(to_lines(
        paths,
        distance=distance,
        segments=segments,
        dxfattribs=dxfattribs,
    ))
    for line in lines:
        layout.add_entity(line)
    return EntityQuery(lines)


def render_splines_and_polylines(
        layout: 'Layout',
        paths: Iterable[Path],
        *,
        g1_tol: float = G1_TOL,
        dxfattribs: Optional[Dict] = None) -> EntityQuery:
    """ Render given `paths` into `layout` as :class:`~ezdxf.entities.Spline`
    and 3D :class:`ezdxf.entities.Polyline` entities.

    Args:
        layout: the modelspace, a paperspace layout or a block definition
        paths: iterable of :class:`Path` objects
        g1_tol: tolerance for G1 continuity check
        dxfattribs: additional DXF attribs

    Returns:
        created entities in an :class:`~ezdxf.query.EntityQuery` object

    .. versionadded:: 0.16

    """
    entities = list(to_splines_and_polylines(
        paths,
        g1_tol=g1_tol,
        dxfattribs=dxfattribs,
    ))
    for entity in entities:
        layout.add_entity(entity)
    return EntityQuery(entities)
