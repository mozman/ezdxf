# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING,
    List,
    Iterable,
    Union,
    Tuple,
    Optional,
    Dict,
    Callable,
    Type,
    TypeVar,
)
from functools import singledispatch, partial
import enum
from ezdxf.math import (
    ABS_TOL,
    Vec2,
    Vec3,
    NULLVEC,
    Z_AXIS,
    OCS,
    Bezier3P,
    Bezier4P,
    ConstructionEllipse,
    BSpline,
    have_bezier_curves_g1_continuity,
    fit_points_to_cad_cv,
    Vertex,
    Matrix44,
)
from ezdxf.lldxf import const
from ezdxf.entities import (
    LWPolyline,
    Polyline,
    Hatch,
    Line,
    Spline,
    Ellipse,
    Arc,
    Circle,
    Solid,
    Trace,
    Face3d,
    Viewport,
    Image,
    Helix,
    Wipeout,
    MPolygon,
    BoundaryPaths,
    BoundaryPathType,
    EdgeType,
)
from .path import Path
from .commands import Command
from . import tools
from .nesting import group_paths

if TYPE_CHECKING:
    from ezdxf.entities import TBoundaryPath, PolylinePath, EdgePath

__all__ = [
    "make_path",
    "to_lines",
    "to_polylines3d",
    "to_lwpolylines",
    "to_polylines2d",
    "to_hatches",
    "to_mpolygons",
    "to_bsplines_and_vertices",
    "to_splines_and_polylines",
    "from_hatch",
    "from_hatch_boundary_path",
    "from_hatch_edge_path",
    "from_hatch_polyline_path",
    "from_vertices",
    "from_matplotlib_path",
    "from_qpainter_path",
    "to_matplotlib_path",
    "to_qpainter_path",
    "multi_path_from_matplotlib_path",
    "multi_path_from_qpainter_path",
]

MAX_DISTANCE = 0.01
MIN_SEGMENTS = 4
G1_TOL = 1e-4
TPolygon = TypeVar("TPolygon", Hatch, MPolygon)
BoundaryFactory = Callable[[BoundaryPaths, Path, int], None]


@singledispatch
def make_path(entity, segments: int = 1, level: int = 4) -> Path:
    """Factory function to create a single :class:`Path` object from a DXF
    entity.

    Args:
        entity: DXF entity
        segments: minimal count of cubic Bézier-curves for elliptical arcs
        level: subdivide level for SPLINE approximation

    Raises:
        TypeError: for unsupported DXF types

    """
    # Complete documentation is path.rst, because Sphinx auto-function
    # renders for each overloaded function a signature, which is ugly
    # and wrong signatures for multiple overloaded function
    # e.g. 3 equal signatures for type Solid.
    raise TypeError(f"unsupported DXF type: {entity.dxftype()}")


@make_path.register(LWPolyline)
def _from_lwpolyline(lwpolyline: LWPolyline, **kwargs) -> "Path":
    path = Path()
    tools.add_2d_polyline(
        path,
        lwpolyline.get_points("xyb"),
        close=lwpolyline.closed,
        ocs=lwpolyline.ocs(),
        elevation=lwpolyline.dxf.elevation,
    )
    return path


@make_path.register(Polyline)
def _from_polyline(polyline: Polyline, **kwargs) -> "Path":
    if polyline.is_polygon_mesh or polyline.is_poly_face_mesh:
        raise TypeError("Unsupported DXF type PolyMesh or PolyFaceMesh")

    path = Path()
    if len(polyline.vertices) == 0:
        return path

    if polyline.is_3d_polyline:
        return from_vertices(polyline.points(), polyline.is_closed)

    points = [vertex.format("xyb") for vertex in polyline.vertices]
    ocs = polyline.ocs()
    if polyline.dxf.hasattr("elevation"):
        elevation = Vec3(polyline.dxf.elevation).z
    else:
        # Elevation attribute is mandatory, but you never know,
        # take elevation from first vertex.
        elevation = Vec3(polyline.vertices[0].dxf.location).z
    tools.add_2d_polyline(
        path,
        points,
        close=polyline.is_closed,
        ocs=ocs,
        elevation=elevation,
    )
    return path


@make_path.register(Helix)
@make_path.register(Spline)
def _from_spline(spline: Spline, **kwargs) -> "Path":
    level = kwargs.get("level", 4)
    path = Path()
    tools.add_spline(path, spline.construction_tool(), level=level, reset=True)
    return path


@make_path.register(Ellipse)
def _from_ellipse(ellipse: Ellipse, **kwargs) -> "Path":
    segments = kwargs.get("segments", 1)
    path = Path()
    tools.add_ellipse(
        path, ellipse.construction_tool(), segments=segments, reset=True
    )
    return path


@make_path.register(Line)
def _from_line(line: Line, **kwargs) -> "Path":
    path = Path(line.dxf.start)
    path.line_to(line.dxf.end)
    return path


@make_path.register(Arc)
def _from_arc(arc: Arc, **kwargs) -> "Path":
    segments = kwargs.get("segments", 1)
    path = Path()
    radius = abs(arc.dxf.radius)
    if radius > 1e-12:
        ellipse = ConstructionEllipse.from_arc(
            center=arc.dxf.center,
            radius=radius,
            extrusion=arc.dxf.extrusion,
            start_angle=arc.dxf.start_angle,
            end_angle=arc.dxf.end_angle,
        )
        tools.add_ellipse(path, ellipse, segments=segments, reset=True)
    return path


@make_path.register(Circle)
def _from_circle(circle: Circle, **kwargs) -> "Path":
    segments = kwargs.get("segments", 1)
    path = Path()
    radius = abs(circle.dxf.radius)
    if radius > 1e-12:
        ellipse = ConstructionEllipse.from_arc(
            center=circle.dxf.center,
            radius=radius,
            extrusion=circle.dxf.extrusion,
        )
        tools.add_ellipse(path, ellipse, segments=segments, reset=True)
    return path


@make_path.register(Face3d)
@make_path.register(Trace)
@make_path.register(Solid)
def _from_quadrilateral(solid: "Solid", **kwargs) -> "Path":
    vertices = solid.wcs_vertices()
    return from_vertices(vertices, close=True)


@make_path.register(Viewport)
def _from_viewport(vp: "Viewport", **kwargs) -> Path:
    if vp.has_clipping_path():
        handle = vp.dxf.clipping_boundary_handle
        if handle != "0" and vp.doc:  # exist
            db = vp.doc.entitydb
            if db:  # exist
                # Many DXF entities can define a clipping path:
                clipping_entity = vp.doc.entitydb.get(handle)
                if clipping_entity:  # exist
                    return make_path(clipping_entity, **kwargs)
    # Return bounding box:
    return from_vertices(vp.boundary_path(), close=True)


@make_path.register(Wipeout)
@make_path.register(Image)
def _from_image(image: "Image", **kwargs) -> Path:
    return from_vertices(image.boundary_path_wcs(), close=True)


@make_path.register(MPolygon)
@make_path.register(Hatch)
def _from_hatch(hatch: Hatch, **kwargs) -> Path:
    ocs = hatch.ocs()
    elevation = hatch.dxf.elevation.z
    offset = NULLVEC
    if isinstance(hatch, MPolygon):
        offset = hatch.dxf.get("offset_vector", NULLVEC)
    paths = [
        from_hatch_boundary_path(boundary, ocs, elevation, offset=offset)
        for boundary in hatch.paths
    ]
    return tools.to_multi_path(paths)


def from_hatch(hatch: Hatch) -> Iterable[Path]:
    """Yield all HATCH boundary paths as separated :class:`Path` objects.

    .. versionadded:: 0.16

    """
    ocs = hatch.ocs()
    elevation = hatch.dxf.elevation.z
    for boundary in hatch.paths:
        p = from_hatch_boundary_path(boundary, ocs, elevation)
        if p.has_sub_paths:
            yield from p.sub_paths()
        else:
            yield p


def from_hatch_boundary_path(
    boundary: "TBoundaryPath",
    ocs: OCS = None,
    elevation: float = 0,
    offset: Vec3 = NULLVEC,  # ocs offset!
) -> "Path":
    """Returns a :class:`Path` object from a :class:`~ezdxf.entities.Hatch`
    polyline- or edge path.
    """
    if boundary.type == BoundaryPathType.EDGE:
        p = from_hatch_edge_path(boundary, ocs, elevation)  # type: ignore
    else:
        p = from_hatch_polyline_path(boundary, ocs, elevation)  # type: ignore
    if offset and ocs is not None:  # only for MPOLYGON
        # assume offset is in OCS
        offset = ocs.to_wcs(offset.replace(z=elevation))
        p = p.transform(Matrix44.translate(offset.x, offset.y, offset.z))
    return p


def from_hatch_polyline_path(
    polyline: "PolylinePath", ocs: OCS = None, elevation: float = 0
) -> "Path":
    """Returns a :class:`Path` object from a :class:`~ezdxf.entities.Hatch`
    polyline path.
    """
    path = Path()
    tools.add_2d_polyline(
        path,
        polyline.vertices,  # List[(x, y, bulge)]
        close=polyline.is_closed,
        ocs=ocs or OCS(),
        elevation=elevation,
    )
    return path


def from_hatch_edge_path(
    edges: "EdgePath",
    ocs: OCS = None,
    elevation: float = 0,
    open_loops: bool = False,
) -> "Path":
    """Returns a :class:`Path` object from a :class:`~ezdxf.entities.Hatch`
    edge path.

    In general open loops should be ignored, but for testing it is maybe
    necessary to override this behavior, by setting `open_loops` to ``True``.
    """

    def line(edge):
        start = wcs(edge.start)
        end = wcs(edge.end)
        segment = Path(start)
        segment.line_to(end)
        return segment

    def arc(edge):
        x, y, *_ = edge.center
        # from_arc() requires OCS data:
        # Note: clockwise oriented arcs are converted to counter
        # clockwise arcs at the loading stage!
        # See: ezdxf.entities.boundary_paths.ArcEdge.load_tags()
        ellipse = ConstructionEllipse.from_arc(
            center=(x, y, elevation),
            radius=edge.radius,
            extrusion=extrusion,
            start_angle=edge.start_angle,
            end_angle=edge.end_angle,
        )
        segment = Path()
        tools.add_ellipse(segment, ellipse, reset=True)
        return segment

    def ellipse(edge):
        ocs_ellipse = edge.construction_tool()
        # ConstructionEllipse has WCS representation:
        # Note: clockwise oriented ellipses are converted to counter
        # clockwise ellipses at the loading stage!
        # See: ezdxf.entities.boundary_paths.EllipseEdge.load_tags()
        ellipse = ConstructionEllipse(
            center=wcs(ocs_ellipse.center.replace(z=elevation)),
            major_axis=wcs_tangent(ocs_ellipse.major_axis),
            ratio=ocs_ellipse.ratio,
            extrusion=extrusion,
            start_param=ocs_ellipse.start_param,
            end_param=ocs_ellipse.end_param,
        )
        segment = Path()
        tools.add_ellipse(segment, ellipse, reset=True)
        return segment

    def spline(edge):
        control_points = [wcs(p) for p in edge.control_points]
        if len(control_points) == 0:
            fit_points = [wcs(p) for p in edge.fit_points]
            if len(fit_points):
                bspline = from_fit_points(edge, fit_points)
            else:
                # No control points and no fit points:
                # DXF structure error
                return
        else:
            bspline = from_control_points(edge, control_points)
        segment = Path()
        tools.add_spline(segment, bspline, reset=True)
        return segment

    def from_fit_points(edge, fit_points):
        tangents = None
        if edge.start_tangent and edge.end_tangent:
            tangents = (
                wcs_tangent(edge.start_tangent),
                wcs_tangent(edge.end_tangent),
            )
        return fit_points_to_cad_cv(  # only a degree of 3 is supported
            fit_points,
            tangents=tangents,
        )

    def from_control_points(edge, control_points):
        return BSpline(
            control_points=control_points,
            order=edge.degree + 1,
            knots=edge.knot_values,
            weights=edge.weights if edge.weights else None,
        )

    def wcs(vertex: Vec2) -> Vec3:
        return _wcs(Vec3(vertex.x, vertex.y, elevation))

    def wcs_tangent(vertex: Vec2) -> Vec3:
        return _wcs(Vec3(vertex.x, vertex.y, 0))

    def _wcs(vec3: Vec3) -> Vec3:
        if ocs and ocs.transform:
            return ocs.to_wcs(vec3)
        else:
            return vec3

    extrusion = ocs.uz if ocs else Z_AXIS
    path = Path()
    loop: Optional[Path] = None
    for edge in edges:
        next_segment: Optional[Path] = None
        if edge.type == EdgeType.LINE:
            next_segment = line(edge)
        elif edge.type == EdgeType.ARC:
            if abs(edge.radius) > ABS_TOL:
                next_segment = arc(edge)
        elif edge.type == EdgeType.ELLIPSE:
            if not Vec2(edge.major_axis).is_null:
                next_segment = ellipse(edge)
        elif edge.type == EdgeType.SPLINE:
            next_segment = spline(edge)

        if next_segment is None:
            continue

        if loop is None:
            loop = next_segment
            continue

        if loop.end.isclose(next_segment.start):
            # end of current loop connects to the start of the next segment
            loop.append_path(next_segment)
        elif loop.end.isclose(next_segment.end):
            # end of current loop connects to the end of the next segment
            loop.append_path(next_segment.reversed())
        elif loop.start.isclose(next_segment.end):
            # start of the current loop connects to the end of the next segment
            next_segment.append_path(loop)
            loop = next_segment
        elif loop.start.isclose(next_segment.start):
            # start of the current loop connects to the start of the next segment
            loop = loop.reversed()
            loop.append_path(next_segment)  # type: ignore
        else:  # gap between current loop and next segment
            if loop.is_closed or open_loops:
                path.extend_multi_path(loop)
            loop = next_segment  # start a new loop

    if loop is not None and (loop.is_closed or open_loops):
        path.extend_multi_path(loop)
    return path  # multi path


def from_vertices(vertices: Iterable["Vertex"], close=False) -> Path:
    """Returns a :class:`Path` object from the given `vertices`."""
    _vertices = Vec3.list(vertices)
    if len(_vertices) < 2:
        return Path()
    path = Path(start=_vertices[0])
    for vertex in _vertices[1:]:
        if not path.end.isclose(vertex):
            path.line_to(vertex)
    if close:
        path.close()
    return path


def to_lwpolylines(
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[LWPolyline]:
    """Convert the given `paths` into :class:`~ezdxf.entities.LWPolyline`
    entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        iterable of :class:`~ezdxf.entities.LWPolyline` objects

    .. versionadded:: 0.16

    """
    if isinstance(paths, Path):
        paths = [paths]
    else:
        paths = list(paths)
    if len(paths) == 0:
        return []

    extrusion = Vec3(extrusion)
    reference_point = paths[0].start
    dxfattribs = dxfattribs or dict()
    if not Z_AXIS.isclose(extrusion):
        ocs, elevation = _get_ocs(extrusion, reference_point)
        paths = tools.transform_paths_to_ocs(paths, ocs)
        dxfattribs["elevation"] = elevation
        dxfattribs["extrusion"] = extrusion
    elif reference_point.z != 0:
        dxfattribs["elevation"] = reference_point.z

    for path in tools.single_paths(paths):
        if len(path) > 0:
            p = LWPolyline.new(dxfattribs=dxfattribs)
            p.append_points(path.flattening(distance, segments), format="xy")
            yield p


def _get_ocs(extrusion: Vec3, reference_point: Vec3) -> Tuple[OCS, float]:
    ocs = OCS(extrusion)
    elevation = ocs.from_wcs(reference_point).z  # type: ignore
    return ocs, elevation


def to_polylines2d(
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[Polyline]:
    """Convert the given `paths` into 2D :class:`~ezdxf.entities.Polyline`
    entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        extrusion: extrusion vector for all paths
        dxfattribs: additional DXF attribs

    Returns:
        iterable of 2D :class:`~ezdxf.entities.Polyline` objects

    .. versionadded:: 0.16

    """
    if isinstance(paths, Path):
        paths = [paths]
    else:
        paths = list(paths)
    if len(paths) == 0:
        return []

    extrusion = Vec3(extrusion)
    reference_point = paths[0].start
    dxfattribs = dxfattribs or dict()
    if not Z_AXIS.isclose(extrusion):
        ocs, elevation = _get_ocs(extrusion, reference_point)
        paths = tools.transform_paths_to_ocs(paths, ocs)
        dxfattribs["elevation"] = Vec3(0, 0, elevation)
        dxfattribs["extrusion"] = extrusion
    elif reference_point.z != 0:
        dxfattribs["elevation"] = Vec3(0, 0, reference_point.z)

    for path in tools.single_paths(paths):
        if len(path) > 0:
            p = Polyline.new(dxfattribs=dxfattribs)
            p.append_vertices(path.flattening(distance, segments))
            yield p


def to_hatches(
    paths: Iterable[Path],
    *,
    edge_path: bool = True,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    g1_tol: float = G1_TOL,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[Hatch]:
    """Convert the given `paths` into :class:`~ezdxf.entities.Hatch` entities.
    Uses LWPOLYLINE paths for boundaries without curves and edge paths, build
    of LINE and SPLINE edges, as boundary paths for boundaries including curves.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        paths: iterable of :class:`Path` objects
        edge_path: ``True`` for edge paths build of LINE and SPLINE edges,
            ``False`` for only LWPOLYLINE paths as boundary paths
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve to flatten LWPOLYLINE paths
        g1_tol: tolerance for G1 continuity check to separate SPLINE edges
        extrusion: extrusion vector to all paths
        dxfattribs: additional DXF attribs

    Returns:
        iterable of :class:`~ezdxf.entities.Hatch` objects

    .. versionadded:: 0.16

    """
    boundary_factory: BoundaryFactory
    if edge_path:
        # noinspection PyTypeChecker
        boundary_factory = partial(
            build_edge_path, distance=distance, segments=segments, g1_tol=g1_tol
        )
    else:
        # noinspection PyTypeChecker
        boundary_factory = partial(
            build_poly_path, distance=distance, segments=segments
        )

    yield from _polygon_converter(
        Hatch, paths, boundary_factory, extrusion, dxfattribs
    )


def to_mpolygons(
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[MPolygon]:
    """Convert the given `paths` into :class:`~ezdxf.entities.MPolygon` entities.
    In contrast to HATCH, MPOLYGON supports only polyline boundary paths.
    All curves will be approximated.

    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The plane elevation is the distance from the WCS origin
    to the start point of the first path.

    Args:
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve to flatten LWPOLYLINE paths
        extrusion: extrusion vector to all paths
        dxfattribs: additional DXF attribs

    Returns:
        iterable of :class:`~ezdxf.entities.MPolygon` objects

    .. versionadded:: 0.17

    """
    # noinspection PyTypeChecker
    boundary_factory: BoundaryFactory = partial(
        build_poly_path, distance=distance, segments=segments
    )
    dxfattribs = dxfattribs or dict()
    dxfattribs.setdefault("fill_color", const.BYLAYER)

    yield from _polygon_converter(
        MPolygon, paths, boundary_factory, extrusion, dxfattribs
    )


def build_edge_path(
    boundaries: BoundaryPaths,
    path: Path,
    flags: int,
    distance: float,
    segments: int,
    g1_tol: float,
):
    if path.has_curves:  # Edge path with LINE and SPLINE edges
        edge_path = boundaries.add_edge_path(flags)
        for edge in to_bsplines_and_vertices(path, g1_tol=g1_tol):
            if isinstance(edge, BSpline):
                edge_path.add_spline(
                    control_points=edge.control_points,
                    degree=edge.degree,
                    knot_values=edge.knots(),
                )
            else:  # add LINE edges
                prev = edge[0]
                for p in edge[1:]:
                    edge_path.add_line(prev, p)
                    prev = p
    else:  # Polyline boundary path
        boundaries.add_polyline_path(
            Vec2.generate(path.flattening(distance, segments)), flags=flags
        )


def build_poly_path(
    boundaries: BoundaryPaths,
    path: Path,
    flags: int,
    distance: float,
    segments: int,
):
    boundaries.add_polyline_path(
        # Vec2 removes the z-axis, which would be interpreted as bulge value!
        Vec2.generate(path.flattening(distance, segments)),
        flags=flags,
    )


def _polygon_converter(
    cls: Type[TPolygon],
    paths: Iterable[Path],
    add_boundary: BoundaryFactory,
    extrusion: "Vertex" = Z_AXIS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[TPolygon]:
    if isinstance(paths, Path):
        paths = [paths]
    else:
        paths = list(paths)
    if len(paths) == 0:
        return []

    extrusion = Vec3(extrusion)
    reference_point = paths[0].start
    dxfattribs = dxfattribs or dict()
    if not Z_AXIS.isclose(extrusion):
        ocs, elevation = _get_ocs(extrusion, reference_point)
        paths = tools.transform_paths_to_ocs(paths, ocs)
        dxfattribs["elevation"] = Vec3(0, 0, elevation)
        dxfattribs["extrusion"] = extrusion
    elif reference_point.z != 0:
        dxfattribs["elevation"] = Vec3(0, 0, reference_point.z)
    dxfattribs.setdefault("solid_fill", 1)
    dxfattribs.setdefault("pattern_name", "SOLID")
    dxfattribs.setdefault("color", const.BYLAYER)

    for group in group_paths(tools.single_paths(paths)):
        if len(group) == 0:
            continue
        polygon = cls.new(dxfattribs=dxfattribs)
        boundaries = polygon.paths
        external = group[0]
        external.close()
        add_boundary(boundaries, external, 1)
        for hole in group[1:]:
            hole.close()
            add_boundary(boundaries, hole, 0)
        yield polygon


def to_polylines3d(
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[Polyline]:
    """Convert the given `paths` into 3D :class:`~ezdxf.entities.Polyline`
    entities.

    Args:
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        dxfattribs: additional DXF attribs

    Returns:
        iterable of 3D :class:`~ezdxf.entities.Polyline` objects

    .. versionadded:: 0.16

    """
    if isinstance(paths, Path):
        paths = [paths]

    dxfattribs = dxfattribs or {}
    dxfattribs["flags"] = const.POLYLINE_3D_POLYLINE
    for path in tools.single_paths(paths):
        if len(path) > 0:
            p = Polyline.new(dxfattribs=dxfattribs)
            p.append_vertices(path.flattening(distance, segments))
            yield p


def to_lines(
    paths: Iterable[Path],
    *,
    distance: float = MAX_DISTANCE,
    segments: int = MIN_SEGMENTS,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[Line]:
    """Convert the given `paths` into :class:`~ezdxf.entities.Line` entities.

    Args:
        paths: iterable of :class:`Path` objects
        distance:  maximum distance, see :meth:`Path.flattening`
        segments: minimum segment count per Bézier curve
        dxfattribs: additional DXF attribs

    Returns:
        iterable of :class:`~ezdxf.entities.Line` objects

    .. versionadded:: 0.16

    """
    if isinstance(paths, Path):
        paths = [paths]
    dxfattribs = dxfattribs or {}
    prev_vertex = None
    for path in tools.single_paths(paths):
        if len(path) == 0:
            continue
        for vertex in path.flattening(distance, segments):
            if prev_vertex is None:
                prev_vertex = vertex
                continue
            dxfattribs["start"] = prev_vertex
            dxfattribs["end"] = vertex
            yield Line.new(dxfattribs=dxfattribs)
            prev_vertex = vertex
        prev_vertex = None


PathParts = Union[BSpline, List[Vec3]]


def to_bsplines_and_vertices(
    path: Path, g1_tol: float = G1_TOL
) -> Iterable[PathParts]:
    """Convert a :class:`Path` object into multiple cubic B-splines and
    polylines as lists of vertices. Breaks adjacent Bèzier without G1
    continuity into separated B-splines.

    Args:
        path: :class:`Path` objects
        g1_tol: tolerance for G1 continuity check

    Returns:
        :class:`~ezdxf.math.BSpline` and lists of :class:`~ezdxf.math.Vec3`

    .. versionadded:: 0.16

    """
    from ezdxf.math import bezier_to_bspline

    def to_vertices():
        points = [polyline[0][0]]
        for line in polyline:
            points.append(line[1])
        return points

    def to_bspline():
        b1 = bezier[0]
        _g1_continuity_curves = [b1]
        for b2 in bezier[1:]:
            if have_bezier_curves_g1_continuity(b1, b2, g1_tol):
                _g1_continuity_curves.append(b2)
            else:
                yield bezier_to_bspline(_g1_continuity_curves)
                _g1_continuity_curves = [b2]
            b1 = b2

        if _g1_continuity_curves:
            yield bezier_to_bspline(_g1_continuity_curves)

    curves = []
    for path in tools.single_paths([path]):
        prev = path.start
        for cmd in path:
            if cmd.type == Command.CURVE3_TO:
                curve = Bezier3P([prev, cmd.ctrl, cmd.end])  # type: ignore
            elif cmd.type == Command.CURVE4_TO:
                curve = Bezier4P([prev, cmd.ctrl1, cmd.ctrl2, cmd.end])  # type: ignore
            elif cmd.type == Command.LINE_TO:
                curve = (prev, cmd.end)
            else:
                raise ValueError
            curves.append(curve)
            prev = cmd.end

    bezier: List = []
    polyline: List = []
    for curve in curves:
        if isinstance(curve, tuple):
            if bezier:
                yield from to_bspline()
                bezier.clear()
            polyline.append(curve)
        else:
            if polyline:
                yield to_vertices()
                polyline.clear()
            bezier.append(curve)

    if bezier:
        yield from to_bspline()
    if polyline:
        yield to_vertices()


def to_splines_and_polylines(
    paths: Iterable[Path],
    *,
    g1_tol: float = G1_TOL,
    dxfattribs: Optional[Dict] = None,
) -> Iterable[Union[Spline, Polyline]]:
    """Convert the given `paths` into :class:`~ezdxf.entities.Spline` and 3D
    :class:`~ezdxf.entities.Polyline` entities.

    Args:
        paths: iterable of :class:`Path` objects
        g1_tol: tolerance for G1 continuity check
        dxfattribs: additional DXF attribs

    Returns:
        iterable of :class:`~ezdxf.entities.Line` objects

    .. versionadded:: 0.16

    """
    if isinstance(paths, Path):
        paths = [paths]
    dxfattribs = dxfattribs or {}

    for path in tools.single_paths(paths):
        for data in to_bsplines_and_vertices(path, g1_tol):
            if isinstance(data, BSpline):
                spline = Spline.new(dxfattribs=dxfattribs)
                spline.apply_construction_tool(data)
                yield spline
            else:
                attribs = dict(dxfattribs)
                attribs["flags"] = const.POLYLINE_3D_POLYLINE
                polyline = Polyline.new(dxfattribs=dxfattribs)
                polyline.append_vertices(data)
                yield polyline


# Interface to Matplotlib.path.Path


@enum.unique
class MplCmd(enum.IntEnum):
    CLOSEPOLY = 79
    CURVE3 = 3
    CURVE4 = 4
    LINETO = 2
    MOVETO = 1
    STOP = 0


def multi_path_from_matplotlib_path(mpath, curves=True) -> Path:
    """Returns a :class:`Path` object from a Matplotlib `Path`_
    (`TextPath`_)  object. (requires Matplotlib). Returns a multi-path object
    if necessary.

    .. versionadded:: 0.17

    .. _TextPath: https://matplotlib.org/3.1.1/api/textpath_api.html
    .. _Path: https://matplotlib.org/3.1.1/api/path_api.html#matplotlib.path.Path

    """
    path = Path()
    current_polyline_start = Vec3()
    for vertices, cmd in mpath.iter_segments(curves=curves):
        cmd = MplCmd(cmd)
        if cmd == MplCmd.MOVETO:
            # vertices = [x0, y0]
            current_polyline_start = Vec3(vertices)
            path.move_to(vertices)
        elif cmd == MplCmd.LINETO:
            # vertices = [x0, y0]
            path.line_to(vertices)
        elif cmd == MplCmd.CURVE3:
            # vertices = [x0, y0, x1, y1]
            path.curve3_to(vertices[2:], vertices[0:2])
        elif cmd == MplCmd.CURVE4:
            # vertices = [x0, y0, x1, y1, x2, y2]
            path.curve4_to(vertices[4:], vertices[0:2], vertices[2:4])
        elif cmd == MplCmd.CLOSEPOLY:
            # vertices = [0, 0]
            if not path.end.isclose(current_polyline_start):
                path.line_to(current_polyline_start)
        elif cmd == MplCmd.STOP:  # not used
            pass
    return path


def from_matplotlib_path(mpath, curves=True) -> Iterable[Path]:
    """Yields multiple :class:`Path` objects from a Matplotlib `Path`_
    (`TextPath`_)  object. (requires Matplotlib)

    .. versionadded:: 0.16

    .. _TextPath: https://matplotlib.org/3.1.1/api/textpath_api.html
    .. _Path: https://matplotlib.org/3.1.1/api/path_api.html#matplotlib.path.Path

    """
    path = multi_path_from_matplotlib_path(mpath, curves=curves)
    if path.has_sub_paths:
        return path.sub_paths()
    else:
        return [path]


def to_matplotlib_path(paths: Iterable[Path], extrusion: "Vertex" = Z_AXIS):
    """Convert the given `paths` into a single :class:`matplotlib.path.Path`
    object.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector.The default extrusion vector
    is the WCS z-axis. The Matplotlib :class:`Path` is a 2D object with
    :ref:`OCS` coordinates and the z-elevation is lost. (requires Matplotlib)

    Args:
        paths: iterable of :class:`Path` objects
        extrusion: extrusion vector for all paths

    Returns:
        matplotlib `Path`_ in OCS!

    .. versionadded:: 0.16

    """
    from matplotlib.path import Path as MatplotlibPath

    if not Z_AXIS.isclose(extrusion):
        paths = tools.transform_paths_to_ocs(paths, OCS(extrusion))
    else:
        paths = list(paths)
    if len(paths) == 0:
        raise ValueError("one or more paths required")

    def add_command(code: MplCmd, point: Vec3):
        codes.append(code)
        vertices.append((point.x, point.y))

    vertices: List[Tuple[float, float]] = []
    codes: List[MplCmd] = []
    for path in paths:
        add_command(MplCmd.MOVETO, path.start)
        for cmd in path:
            if cmd.type == Command.LINE_TO:
                add_command(MplCmd.LINETO, cmd.end)
            elif cmd.type == Command.MOVE_TO:
                add_command(MplCmd.MOVETO, cmd.end)
            elif cmd.type == Command.CURVE3_TO:
                add_command(MplCmd.CURVE3, cmd.ctrl)  # type: ignore
                add_command(MplCmd.CURVE3, cmd.end)
            elif cmd.type == Command.CURVE4_TO:
                add_command(MplCmd.CURVE4, cmd.ctrl1)  # type: ignore
                add_command(MplCmd.CURVE4, cmd.ctrl2)  # type: ignore
                add_command(MplCmd.CURVE4, cmd.end)

    # STOP command is currently not required
    assert len(vertices) == len(codes)
    return MatplotlibPath(vertices, codes)


# Interface to PyQt5.QtGui.QPainterPath


def multi_path_from_qpainter_path(qpath) -> Path:
    """Returns a :class:`Path` objects from a `QPainterPath`_.
    Returns a multi-path object if necessary. (requires PyQt5)

    .. versionadded:: 0.17

    .. _QPainterPath: https://doc.qt.io/qt-5/qpainterpath.html

    """
    # QPainterPath stores only cubic Bèzier curves
    path = Path()
    vertices: List[Vec3] = []
    for index in range(qpath.elementCount()):
        element = qpath.elementAt(index)
        cmd = element.type
        v = Vec3(element.x, element.y)

        if cmd == 0:  # MoveTo
            assert len(vertices) == 0
            path.move_to(v)
        elif cmd == 1:  # LineTo
            assert len(vertices) == 0
            path.line_to(v)
        elif cmd == 2:  # CurveTo
            assert len(vertices) == 0
            vertices.append(v)
        elif cmd == 3:  # CurveToDataElement
            if len(vertices) == 2:
                path.curve4_to(v, vertices[0], vertices[1])
                vertices.clear()
            else:
                vertices.append(v)
    return path


def from_qpainter_path(qpath) -> Iterable[Path]:
    """Yields multiple :class:`Path` objects from a `QPainterPath`_.
    (requires PyQt5)

    .. versionadded:: 0.16

    .. _QPainterPath: https://doc.qt.io/qt-5/qpainterpath.html

    """
    # QPainterPath stores only cubic Bèzier curves
    path = multi_path_from_qpainter_path(qpath)
    if path.has_sub_paths:
        return path.sub_paths()
    else:
        return [path]


def to_qpainter_path(paths: Iterable[Path], extrusion: "Vertex" = Z_AXIS):
    """Convert the given `paths` into a :class:`PyQt5.QtGui.QPainterPath`
    object.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector. The default extrusion vector
    is the WCS z-axis. The :class:`QPainterPath` is a 2D object with :ref:`OCS`
    coordinates and the z-elevation is lost. (requires PyQt5)

    Args:
        paths: iterable of :class:`Path` objects
        extrusion: extrusion vector for all paths

    Returns:
        `QPainterPath`_ in OCS!

    .. versionadded:: 0.16

    """
    from PyQt5.QtGui import QPainterPath
    from PyQt5.QtCore import QPointF

    if not Z_AXIS.isclose(extrusion):
        paths = tools.transform_paths_to_ocs(paths, OCS(extrusion))
    else:
        paths = list(paths)
    if len(paths) == 0:
        raise ValueError("one or more paths required")

    def qpnt(v: Vec3):
        return QPointF(v.x, v.y)

    qpath = QPainterPath()
    for path in paths:
        qpath.moveTo(qpnt(path.start))
        for cmd in path:
            if cmd.type == Command.LINE_TO:
                qpath.lineTo(qpnt(cmd.end))
            elif cmd.type == Command.MOVE_TO:
                qpath.moveTo(qpnt(cmd.end))
            elif cmd.type == Command.CURVE3_TO:
                qpath.quadTo(qpnt(cmd.ctrl), qpnt(cmd.end))  # type: ignore
            elif cmd.type == Command.CURVE4_TO:
                qpath.cubicTo(qpnt(cmd.ctrl1), qpnt(cmd.ctrl2), qpnt(cmd.end))  # type: ignore
    return qpath
