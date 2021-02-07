# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import (
    TYPE_CHECKING, List, Iterable, Sequence, NamedTuple, Union, Tuple,
    Optional, Dict, Callable,
)
from collections import abc
import enum
import warnings
import math
import itertools
from ezdxf.math import (
    Vec2, Vec3, NULLVEC, Z_AXIS, OCS, Bezier3P, Bezier4P, Matrix44,
    bulge_to_arc, cubic_bezier_from_ellipse, ConstructionEllipse, BSpline,
    has_clockwise_orientation, global_bspline_interpolation, BoundingBox,
    have_bezier_curves_g1_continuity, AnyBezier,
)
from ezdxf.lldxf import const
from ezdxf.query import EntityQuery
from ezdxf.entities import LWPolyline, Polyline, Hatch, Line, Spline

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        Vertex, Ellipse, Arc, Circle, DXFEntity,
        Solid, Viewport, Image, Layout, EntityQuery,
    )
    from ezdxf.entities.hatch import PolylinePath, EdgePath, TPath

__all__ = [
    'Path', 'Command', 'make_path', 'has_path_support', 'from_matplotlib_path',
    'bbox', 'fit_paths_into_box', 'transform_paths', 'transform_paths_to_ocs',
    'to_lines', 'to_polylines3d', 'to_lwpolylines', 'to_polylines2d',
    'to_hatches', 'to_bsplines_and_vertices', 'to_splines_and_polylines',
    'render_lwpolylines', 'render_polylines2d', 'render_polylines3d',
    'render_lines', 'render_hatches', 'render_splines_and_polylines'
]

MAX_DISTANCE = 0.01
MIN_SEGMENTS = 4
G1_TOL = 1e-4


@enum.unique
class Command(enum.IntEnum):
    START_PATH = -1  # external command, not use in Path()
    LINE_TO = 1  # (LINE_TO, end vertex)
    CURVE3_TO = 2  # (CURVE3_TO, end vertex, ctrl) quadratic bezier
    CURVE4_TO = 3  # (CURVE4_TO, end vertex, ctrl1, ctrl2) cubic bezier


class LineTo(NamedTuple):
    end: Vec3

    @property
    def type(self):
        return Command.LINE_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return LineTo(end=ocs.to_wcs(self.end.replace(z=elevation)))


class Curve3To(NamedTuple):
    end: Vec3
    ctrl: Vec3

    @property
    def type(self):
        return Command.CURVE3_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return Curve3To(
            end=ocs.to_wcs(self.end.replace(z=elevation)),
            ctrl=ocs.to_wcs(self.ctrl.replace(z=elevation)),
        )


class Curve4To(NamedTuple):
    end: Vec3
    ctrl1: Vec3
    ctrl2: Vec3

    @property
    def type(self):
        return Command.CURVE4_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return Curve4To(
            end=ocs.to_wcs(self.end.replace(z=elevation)),
            ctrl1=ocs.to_wcs(self.ctrl1.replace(z=elevation)),
            ctrl2=ocs.to_wcs(self.ctrl2.replace(z=elevation)),
        )


AnyCurve = (Command.CURVE3_TO, Command.CURVE4_TO)
PathElement = Union[LineTo, Curve3To, Curve4To]


class Path(abc.Sequence):
    def __init__(self, start: 'Vertex' = NULLVEC):
        self._start = Vec3(start)
        self._commands: List[PathElement] = []

    def __len__(self) -> int:
        return len(self._commands)

    def __getitem__(self, item) -> PathElement:
        return self._commands[item]

    def __iter__(self) -> Iterable[PathElement]:
        return iter(self._commands)

    def __copy__(self) -> 'Path':
        """ Returns a new copy of :class:`Path` with shared immutable data. """
        copy = Path(self._start)
        # immutable data
        copy._commands = list(self._commands)
        return copy

    clone = __copy__

    @property
    def start(self) -> Vec3:
        """ :class:`Path` start point, resetting the start point of an empty
        path is possible.
        """
        return self._start

    @start.setter
    def start(self, location: 'Vertex') -> None:
        if len(self._commands):
            raise ValueError('Requires an empty path.')
        else:
            self._start = Vec3(location)

    @property
    def end(self) -> Vec3:
        """ :class:`Path` end point. """
        if self._commands:
            return self._commands[-1].end
        else:
            return self._start

    @property
    def is_closed(self) -> bool:
        """ Returns ``True`` if the start point is close to the end point. """
        return self._start.isclose(self.end)

    @property
    def has_lines(self) -> bool:
        """ Returns ``True`` if the path has any line segments. """
        return any(cmd.type == Command.LINE_TO for cmd in self._commands)

    @property
    def has_curves(self) -> bool:
        """ Returns ``True`` if the path has any curve segments. """
        return any(cmd.type in AnyCurve for cmd in self._commands)

    @classmethod
    def from_vertices(cls, vertices: Iterable['Vertex'], close=False) -> 'Path':
        """ Returns a :class:`Path` from vertices.  """
        vertices = Vec3.list(vertices)
        if len(vertices) < 2:
            return cls()
        path = cls(start=vertices[0])
        for vertex in vertices[1:]:
            path.line_to(vertex)
        if close:
            path.close()
        return path

    @classmethod
    def from_lwpolyline(cls, lwpolyline: 'LWPolyline') -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.LWPolyline`
        entity, all vertices transformed to WCS.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(lwpolyline),'
            'will be removed in v0.17.', DeprecationWarning)
        return make_path(lwpolyline)

    @classmethod
    def from_polyline(cls, polyline: 'Polyline') -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Polyline`
        entity, all vertices transformed to WCS.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(polyline),'
            'will be removed in v0.17.', DeprecationWarning)
        return make_path(polyline)

    def _to_wcs(self, ocs: OCS, elevation: float):
        self._start = ocs.to_wcs(self._start.replace(z=elevation))
        for i, cmd in enumerate(self._commands):
            self._commands[i] = cmd.to_wcs(ocs, elevation)

    @classmethod
    def from_spline(cls, spline: 'Spline', level: int = 4) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Spline`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(polyline),'
            'will be removed in v0.17.', DeprecationWarning)
        return make_path(spline, level=level)

    @classmethod
    def from_ellipse(cls, ellipse: 'Ellipse', segments: int = 1) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Ellipse`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(ellipse),'
            'will be removed in v0.17.', DeprecationWarning)
        return make_path(ellipse, segments=segments)

    @classmethod
    def from_arc(cls, arc: 'Arc', segments: int = 1) -> 'Path':
        """ Returns a :class:`Path` from an :class:`~ezdxf.entities.Arc`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(arc),'
            'will be removed in v0.17.', DeprecationWarning)
        return make_path(arc, segments=segments)

    @classmethod
    def from_circle(cls, circle: 'Circle', segments: int = 1) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Circle`.

        .. deprecated:: 0.15.2
            replaced by factory function :func:`make_path()`

        """
        warnings.warn(
            'use factory function make_path(circle),'
            'will be removed in v0.17.', DeprecationWarning)
        return make_path(circle, segments=segments)

    @classmethod
    def from_hatch_boundary_path(cls, boundary: 'TPath', ocs: OCS = None,
                                 elevation: float = 0) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Hatch`
        polyline- or edge path.
        """
        if boundary.PATH_TYPE == 'EdgePath':
            return cls.from_hatch_edge_path(boundary, ocs, elevation)
        else:
            return cls.from_hatch_polyline_path(boundary, ocs, elevation)

    @classmethod
    def from_hatch_polyline_path(cls, polyline: 'PolylinePath', ocs: OCS = None,
                                 elevation: float = 0) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Hatch`
        polyline path.
        """
        path = cls()
        path.add_2d_polyline(
            polyline.vertices,  # List[(x, y, bulge)]
            close=polyline.is_closed,
            ocs=ocs or OCS(),
            elevation=elevation,
        )
        return path

    @classmethod
    def from_hatch_edge_path(cls, edges: 'EdgePath', ocs: OCS = None,
                             elevation: float = 0) -> 'Path':
        """ Returns a :class:`Path` from a :class:`~ezdxf.entities.Hatch` edge
        path.
        """

        def add_line_edge(edge):
            start = wcs(edge.start)
            end = wcs(edge.end)
            if len(path):
                if path.end.isclose(start):
                    # path-end -> line-end
                    path.line_to(end)
                elif path.end.isclose(end):
                    # path-end (==line-end) -> line-start
                    path.line_to(start)
                else:
                    # path-end -> edge-start -> edge-end
                    path.line_to(start)
                    path.line_to(end)
            else:  # start path
                path.start = start
                path.line_to(end)

        def add_arc_edge(edge):
            x, y, *_ = edge.center
            # from_arc() requires OCS data:
            ellipse = ConstructionEllipse.from_arc(
                center=(x, y, elevation),
                radius=edge.radius,
                extrusion=extrusion,
                start_angle=edge.start_angle,
                end_angle=edge.end_angle,
            )
            path.add_ellipse(ellipse, reset=not bool(path))

        def add_ellipse_edge(edge):
            ocs_ellipse = edge.construction_tool()
            # ConstructionEllipse has WCS representation:
            ellipse = ConstructionEllipse(
                center=wcs(ocs_ellipse.center.replace(z=elevation)),
                major_axis=wcs(ocs_ellipse.major_axis),
                ratio=ocs_ellipse.ratio,
                extrusion=extrusion,
                start_param=ocs_ellipse.start_param,
                end_param=ocs_ellipse.end_param,
            )
            path.add_ellipse(ellipse, reset=not bool(path))

        def add_spline_edge(edge):
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
            path.add_spline(bspline, reset=not bool(path))

        def from_fit_points(edge, fit_points):
            tangents = None
            if edge.start_tangent and edge.end_tangent:
                tangents = (
                    wcs(edge.start_tangent),
                    wcs(edge.end_tangent)
                )
            return global_bspline_interpolation(
                fit_points,
                degree=edge.degree,
                tangents=tangents,
            )

        def from_control_points(edge, control_points):
            return BSpline(
                control_points=control_points,
                order=edge.degree + 1,
                knots=edge.knot_values,
                weights=edge.weights if edge.weights else None
            )

        def wcs(vertex):
            if ocs and ocs.transform:
                return ocs.to_wcs((vertex.x, vertex.y, elevation))
            else:
                return Vec3(vertex)

        extrusion = ocs.uz if ocs else Z_AXIS
        path = Path()
        for edge in edges:
            if edge.EDGE_TYPE == "LineEdge":
                add_line_edge(edge)
            elif edge.EDGE_TYPE == "ArcEdge":
                if not math.isclose(edge.radius, 0):
                    add_arc_edge(edge)
            elif edge.EDGE_TYPE == "EllipseEdge":
                if not NULLVEC.isclose(edge.major_axis):
                    add_ellipse_edge(edge)
            elif edge.EDGE_TYPE == "SplineEdge":
                add_spline_edge(edge)

        return path

    def control_vertices(self):
        """ Yields all path control vertices in consecutive order. """
        if len(self):
            yield self.start
            for cmd in self._commands:
                if cmd.type == Command.LINE_TO:
                    yield cmd.end
                elif cmd.type == Command.CURVE3_TO:
                    yield cmd.ctrl
                    yield cmd.end
                elif cmd.type == Command.CURVE4_TO:
                    yield cmd.ctrl1
                    yield cmd.ctrl2
                    yield cmd.end

    def has_clockwise_orientation(self) -> bool:
        """ Returns ``True`` if 2D path has clockwise orientation, ignores
        z-axis of all control vertices.
        """
        return has_clockwise_orientation(self.control_vertices())

    def line_to(self, location: 'Vertex') -> None:
        """ Add a line from actual path end point to `location`.
        """
        self._commands.append(LineTo(end=Vec3(location)))

    def curve3_to(self, location: 'Vertex', ctrl: 'Vertex') -> None:
        """ Add a quadratic Bèzier-curve from actual path end point to
        `location`, `ctrl` is the control point for the quadratic Bèzier-curve.
        """
        self._commands.append(Curve3To(end=Vec3(location), ctrl=Vec3(ctrl)))

    def curve4_to(self, location: 'Vertex', ctrl1: 'Vertex',
                  ctrl2: 'Vertex') -> None:
        """ Add a cubic Bèzier-curve from actual path end point to `location`,
        `ctrl1` and `ctrl2` are the control points for the cubic Bèzier-curve.
        """
        self._commands.append(Curve4To(
            end=Vec3(location), ctrl1=Vec3(ctrl1), ctrl2=Vec3(ctrl2))
        )

    curve_to = curve4_to  # TODO: 2021-01-30, remove compatibility alias

    def close(self) -> None:
        """ Close path by adding a line segment from the end point to the start
        point.
        """
        if not self.is_closed:
            self.line_to(self.start)

    def reversed(self) -> 'Path':
        """ Returns a new :class:`Path` with reversed segments and control
        vertices.
        """
        if len(self) == 0:
            return Path()

        path = Path(start=self.end)
        for index in range(len(self) - 1, -1, -1):
            cmd = self[index]
            if index > 0:
                prev_end = self[index - 1].end
            else:
                prev_end = self.start

            if cmd.type == Command.LINE_TO:
                path.line_to(prev_end)
            elif cmd.type == Command.CURVE3_TO:
                path.curve3_to(prev_end, cmd.ctrl)
            elif cmd.type == Command.CURVE4_TO:
                path.curve4_to(prev_end, cmd.ctrl2, cmd.ctrl1)
        return path

    def clockwise(self) -> 'Path':
        """ Returns new :class:`Path` in clockwise orientation. """
        if self.has_clockwise_orientation():
            return self.clone()
        else:
            return self.reversed()

    def counter_clockwise(self) -> 'Path':
        """ Returns new :class:`Path` in counter-clockwise orientation. """
        if self.has_clockwise_orientation():
            return self.reversed()
        else:
            return self.clone()

    def add_curves4(self, curves: Iterable[Bezier4P]) -> None:
        """ Add multiple cubic Bèzier-curves to the path.

        Auto-detect if the path end point is connected to the start- or
        end point of the curves, if none of them is close to the path end point
        a line from the path end point to the curves start point will be added.

        """
        curves = list(curves)
        if not len(curves):
            return
        end = curves[-1].control_points[-1]
        if self.end.isclose(end):
            # connect to new curves end point
            curves = _reverse_bezier_curves(curves)

        for curve in curves:
            start, ctrl1, ctrl2, end = curve.control_points
            if not start.isclose(self.end, abs_tol=1e-9):
                self.line_to(start)
            self.curve4_to(end, ctrl1, ctrl2)

    add_curves = add_curves4  # TODO: 2021-01-30, remove compatibility alias

    def add_curves3(self, curves: Iterable[Bezier3P]) -> None:
        """ Add multiple quadratic Bèzier-curves to the path.

        Auto-detect if the path end point is connected to the start- or
        end point of the curves, if none of them is close to the path end point
        a line from the path end point to the curves start point will be added.

        """
        curves = list(curves)
        if not len(curves):
            return
        end = curves[-1].control_points[-1]
        if self.end.isclose(end):
            # connect to new curves end point
            curves = _reverse_bezier_curves(curves)

        for curve in curves:
            start, ctrl, end = curve.control_points
            if not start.isclose(self.end, abs_tol=1e-9):
                self.line_to(start)
            self.curve3_to(end, ctrl)

    def add_2d_polyline(self, points: Iterable[Sequence[float]], close: bool,
                        ocs: OCS, elevation: float) -> None:
        """ Internal API to add 2D polylines which may include bulges. """

        def bulge_to(p1: Vec3, p2: Vec3, bulge: float):
            if p1.isclose(p2):
                return
            center, start_angle, end_angle, radius = bulge_to_arc(p1, p2, bulge)
            ellipse = ConstructionEllipse.from_arc(
                center, radius, Z_AXIS,
                math.degrees(start_angle),
                math.degrees(end_angle),
            )
            curves = list(cubic_bezier_from_ellipse(ellipse))
            curve0 = curves[0]
            cp0 = curve0.control_points[0]
            if cp0.isclose(p2):
                curves = _reverse_bezier_curves(curves)
            self.add_curves4(curves)

        prev_point = None
        prev_bulge = 0
        for x, y, bulge in points:
            # Bulge values near 0 but != 0 cause crashes! #329
            if abs(bulge) < 1e-6:
                bulge = 0
            point = Vec3(x, y)
            if prev_point is None:
                self._start = point
                prev_point = point
                prev_bulge = bulge
                continue

            if prev_bulge:
                bulge_to(prev_point, point, prev_bulge)
            else:
                self.line_to(point)
            prev_point = point
            prev_bulge = bulge

        if close and not self.start.isclose(self.end):
            if prev_bulge:
                bulge_to(self.end, self.start, prev_bulge)
            else:
                self.line_to(self.start)

        if ocs.transform or elevation:
            self._to_wcs(ocs, elevation)

    def add_ellipse(self, ellipse: ConstructionEllipse, segments=1,
                    reset=True) -> None:
        """ Add an elliptical arc as multiple cubic Bèzier-curves, use
        :meth:`~ezdxf.math.ConstructionEllipse.from_arc` constructor of class
        :class:`~ezdxf.math.ConstructionEllipse` to add circular arcs.

        Auto-detect connection point, if none is close a line from the path
        end point to the ellipse start point will be added
        (see :meth:`add_curves4`).

        By default the start of an **empty** path is set to the start point of
        the ellipse, setting argument `reset` to ``False`` prevents this
        behavior.

        Args:
            ellipse: ellipse parameters as :class:`~ezdxf.math.ConstructionEllipse`
                object
            segments: count of Bèzier-curve segments, at least one segment for
                each quarter (pi/2), ``1`` for as few as possible.
            reset: set start point to start of ellipse if path is empty

        """
        if abs(ellipse.param_span) < 1e-9:
            return
        if len(self) == 0 and reset:
            self.start = ellipse.start_point
        self.add_curves4(
            cubic_bezier_from_ellipse(ellipse, segments)
        )

    def add_spline(self, spline: BSpline, level=4, reset=True) -> None:
        """ Add a B-spline as multiple cubic Bèzier-curves.

        Non-rational B-splines of 3rd degree gets a perfect conversion to
        cubic bezier curves with a minimal count of curve segments, all other
        B-spline require much more curve segments for approximation.

        Auto-detect connection point, if none is close a line from the path
        end point to the spline start point will be added
        (see :meth:`add_curves4`).

        By default the start of an **empty** path is set to the start point of
        the spline, setting argument `reset` to ``False`` prevents this
        behavior.

        Args:
            spline: B-spline parameters as :class:`~ezdxf.math.BSpline` object
            level: subdivision level of approximation segments
            reset: set start point to start of spline if path is empty

        """
        if len(self) == 0 and reset:
            self.start = spline.point(0)
        if spline.degree == 3 and not spline.is_rational and spline.is_clamped:
            curves = [Bezier4P(points) for points in
                      spline.bezier_decomposition()]
        else:
            curves = spline.cubic_bezier_approximation(level=level)
        self.add_curves4(curves)

    def approximate(self, segments: int = 20) -> Iterable[Vec3]:
        """ Approximate path by vertices, `segments` is the count of
        approximation segments for each Bézier curve.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        """

        def approx_curve3(s, c, e) -> Iterable[Vec3]:
            return Bezier3P((s, c, e)).approximate(segments)

        def approx_curve4(s, c1, c2, e) -> Iterable[Vec3]:
            return Bezier4P((s, c1, c2, e)).approximate(segments)

        yield from self._approximate(approx_curve3, approx_curve4)

    def flattening(self, distance: float,
                   segments: int = 16) -> Iterable[Vec3]:
        """ Approximate path by vertices and use adaptive recursive flattening
        to approximate Bèzier curves. The argument `segments` is the
        minimum count of approximation segments for each curve, if the distance
        from the center of the approximation segment to the curve is bigger than
        `distance` the segment will be subdivided.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        Args:
            distance: maximum distance from the center of the curve to the
                center of the line segment between two approximation points to
                determine if a segment should be subdivided.
            segments: minimum segment count per Bézier curve

        """

        def approx_curve3(s, c, e) -> Iterable[Vec3]:
            return Bezier3P((s, c, e)).flattening(distance, segments)

        def approx_curve4(s, c1, c2, e) -> Iterable[Vec3]:
            return Bezier4P((s, c1, c2, e)).flattening(distance, segments)

        yield from self._approximate(approx_curve3, approx_curve4)

    def _approximate(self, approx_curve3, approx_curve4) -> Iterable[Vec3]:
        if not self._commands:
            return

        start = self._start
        yield start

        for cmd in self._commands:
            end_location = cmd.end
            if cmd.type == Command.LINE_TO:
                yield end_location
            elif cmd.type == Command.CURVE3_TO:
                pts = iter(
                    approx_curve3(start, cmd.ctrl, end_location)
                )
                next(pts)  # skip first vertex
                yield from pts
            elif cmd.type == Command.CURVE4_TO:
                pts = iter(
                    approx_curve4(start, cmd.ctrl1, cmd.ctrl2, end_location)
                )
                next(pts)  # skip first vertex
                yield from pts
            else:
                raise ValueError(f'Invalid command: {cmd.type}')
            start = end_location

    def transform(self, m: 'Matrix44') -> 'Path':
        """ Returns a new transformed path.

        Args:
             m: transformation matrix of type :class:`~ezdxf.math.Matrix44`

        """
        new_path = self.__class__(m.transform(self.start))
        for cmd in self._commands:

            if cmd.type == Command.LINE_TO:
                new_path.line_to(m.transform(cmd.end))
            elif cmd.type == Command.CURVE3_TO:
                loc, ctrl = m.transform_vertices(
                    (cmd.end, cmd.ctrl)
                )
                new_path.curve3_to(loc, ctrl)
            elif cmd.type == Command.CURVE4_TO:
                loc, ctrl1, ctrl2 = m.transform_vertices(
                    (cmd.end, cmd.ctrl1, cmd.ctrl2)
                )
                new_path.curve4_to(loc, ctrl1, ctrl2)
            else:
                raise ValueError(f'Invalid command: {cmd.type}')

        return new_path


def _reverse_bezier_curves(curves: List[AnyBezier]) -> List[AnyBezier]:
    curves = list(c.reverse() for c in curves)
    curves.reverse()
    return curves


def _from_lwpolyline(lwpolyline: 'LWPolyline', **kwargs) -> 'Path':
    """ Returns a Path from a LWPolyline. """
    path = Path()
    path.add_2d_polyline(
        lwpolyline.get_points('xyb'),
        close=lwpolyline.closed,
        ocs=lwpolyline.ocs(),
        elevation=lwpolyline.dxf.elevation,
    )
    return path


def _from_polyline(polyline: 'Polyline', **kwargs) -> 'Path':
    """ Returns a Path from a 2D/3D Polyline. """
    path = Path()
    if len(polyline.vertices) == 0 or \
            polyline.is_polygon_mesh or \
            polyline.is_poly_face_mesh:
        return path

    if polyline.is_3d_polyline:
        return Path.from_vertices(polyline.points(), polyline.is_closed)

    points = [vertex.format('xyb') for vertex in polyline.vertices]
    ocs = polyline.ocs()
    if polyline.dxf.hasattr('elevation'):
        elevation = Vec3(polyline.dxf.elevation).z
    else:
        # Elevation attribute is mandatory, but you never know,
        # take elevation from first vertex.
        elevation = Vec3(polyline.vertices[0].dxf.location).z
    path.add_2d_polyline(
        points,
        close=polyline.is_closed,
        ocs=ocs,
        elevation=elevation,
    )
    return path


def _from_spline(spline: 'Spline', **kwargs) -> 'Path':
    """ Returns a Path from a Spline. """
    level = kwargs.get('level', 4)
    path = Path()
    path.add_spline(spline.construction_tool(), level=level, reset=True)
    return path


def _from_ellipse(ellipse: 'Ellipse', **kwargs) -> 'Path':
    """ Returns a Path from an Ellipse. """
    segments = kwargs.get('segments', 1)
    path = Path()
    path.add_ellipse(ellipse.construction_tool(),
                     segments=segments,
                     reset=True)
    return path


def _from_line(line: 'Line', **kwargs) -> 'Path':
    """ Returns a Path from a Line. """
    path = Path(line.dxf.start)
    path.line_to(line.dxf.end)
    return path


def _from_arc(arc: 'Arc', **kwargs) -> 'Path':
    """ Returns a Path from an Arc. """
    segments = kwargs.get('segments', 1)
    path = Path()
    radius = abs(arc.dxf.radius)
    if not math.isclose(radius, 0):
        ellipse = ConstructionEllipse.from_arc(
            center=arc.dxf.center,
            radius=radius,
            extrusion=arc.dxf.extrusion,
            start_angle=arc.dxf.start_angle,
            end_angle=arc.dxf.end_angle,
        )
        path.add_ellipse(ellipse, segments=segments, reset=True)
    return path


def _from_circle(circle: 'Circle', **kwargs) -> 'Path':
    """ Returns a Path from a Circle. """
    segments = kwargs.get('segments', 1)
    path = Path()
    radius = abs(circle.dxf.radius)
    if not math.isclose(radius, 0):
        ellipse = ConstructionEllipse.from_arc(
            center=circle.dxf.center,
            radius=radius,
            extrusion=circle.dxf.extrusion,
        )
        path.add_ellipse(ellipse, segments=segments, reset=True)
    return path


def _from_quadrilateral(solid: 'Solid', **kwargs) -> 'Path':
    """ Returns a from a Solid, Trace or Face3d. """
    vertices = solid.wcs_vertices()
    return Path.from_vertices(vertices, close=True)


def _from_viewport(vp: 'Viewport', **kwargs) -> Path:
    if vp.has_clipping_path():
        handle = vp.dxf.clipping_boundary_handle
        if handle != '0' and vp.doc:  # exist
            db = vp.doc.entitydb
            if db:  # exist
                # Many DXF entities can define a clipping path:
                clipping_entity = vp.doc.entitydb.get(handle)
                if clipping_entity:  # exist
                    return make_path(clipping_entity, **kwargs)
    # Return bounding box:
    return Path.from_vertices(vp.boundary_path(), close=True)


def _from_image(image: 'Image', **kwargs) -> Path:
    return Path.from_vertices(image.boundary_path_wcs(), close=True)


_FACTORIES = {
    "ARC": _from_arc,
    "CIRCLE": _from_circle,
    "ELLIPSE": _from_ellipse,
    "LINE": _from_line,
    "LWPOLYLINE": _from_lwpolyline,
    "POLYLINE": _from_polyline,
    "SPLINE": _from_spline,
    "HELIX": _from_spline,
    "SOLID": _from_quadrilateral,
    "TRACE": _from_quadrilateral,
    "3DFACE": _from_quadrilateral,
    "VIEWPORT": _from_viewport,
    "IMAGE": _from_image,
    "WIPEOUT": _from_image,
}


def has_path_support(e: 'DXFEntity') -> bool:
    """ Returns ``True`` if DXF entity `e` is convertible into a :class:`Path`
    object.

    .. versionadded:: 0.16

    """
    dxftype = e.dxftype()
    if dxftype == "POLYLINE":
        # PolygonMesh and PolyFaceMesh is not supported by Path()
        return e.is_2d_polyline() or e.is_3d_polyline()
    else:
        return dxftype in _FACTORIES


def make_path(e: 'DXFEntity', segments: int = 1, level: int = 4) -> Path:
    """ Factory function to create :class:`Path` objects from DXF entities:

    - LINE
    - CIRCLE
    - ARC
    - ELLIPSE
    - SPLINE and HELIX
    - LWPOLYLINE
    - 2D and 3D POLYLINE
    - SOLID, TRACE, 3DFACE
    - IMAGE, WIPEOUT clipping path
    - VIEWPORT clipping path

    Args:
        e: DXF entity
        segments: minimal count of cubic Bézier-curves for elliptical arcs:
            CIRCLE, ARC, ELLIPSE, see :meth:`Path.add_ellipse`
        level: subdivide level for SPLINE approximation,
            see :meth:`Path.add_spline`

    .. versionadded:: 0.16

    """
    dxftype = e.dxftype()
    try:
        converter = _FACTORIES[dxftype]
    except KeyError:
        raise TypeError(f'Unsupported DXF type {dxftype}')
    return converter(e, segments=segments, level=level)


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


def to_lwpolylines(
        paths: Iterable[Path], *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> Iterable[LWPolyline]:
    """ Convert given `paths` into :class:`~ezdxf.entities.LWPolyline` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The plane elevation is defined by the distance of the
    start point of the first path to the WCS origin.

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
    if not extrusion.isclose(Z_AXIS):
        ocs, elevation = _get_ocs(extrusion, reference_point)
        paths = transform_paths_to_ocs(paths, ocs)
        dxfattribs['elevation'] = elevation
        dxfattribs['extrusion'] = extrusion
    elif reference_point.z != 0:
        dxfattribs['elevation'] = reference_point.z

    for path in paths:
        p = LWPolyline.new(dxfattribs=dxfattribs)
        p.append_points(path.flattening(distance, segments), format='xy')
        yield p


def _get_ocs(extrusion: Vec3, referenc_point: Vec3) -> Tuple[OCS, float]:
    ocs = OCS(extrusion)
    elevation = ocs.from_wcs(referenc_point).z
    return ocs, elevation


def to_polylines2d(
        paths: Iterable[Path],
        *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> Iterable[Polyline]:
    """ Convert given `paths` into 2D :class:`~ezdxf.entities.Polyline` entities.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The plane elevation is defined by the distance of the
    start point of the first path to the WCS origin.

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
    if not extrusion.isclose(Z_AXIS):
        ocs, elevation = _get_ocs(extrusion, reference_point)
        paths = transform_paths_to_ocs(paths, ocs)
        dxfattribs['elevation'] = Vec3(0, 0, elevation)
        dxfattribs['extrusion'] = extrusion
    elif reference_point.z != 0:
        dxfattribs['elevation'] = Vec3(0, 0, reference_point.z)

    for path in paths:
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
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> Iterable[Hatch]:
    """ Convert given `paths` into :class:`~ezdxf.entities.Hatch` entities.
    Uses LWPOLYLINE paths for boundaries without curves and edge paths build
    of LINE and SPLINE edges as boundary paths for boundaries including curves.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The plane elevation is defined by the distance of the
    start point of the first path to the WCS origin.

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

    def build_edge_path(hatch: Hatch, path: Path, flags: int):
        if path.has_curves:  # Edge path with LINE and SPLINE edges
            edge_path = hatch.paths.add_edge_path(flags)
            for edge in to_bsplines_and_vertices(
                    path, g1_tol=g1_tol):
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
            hatch.paths.add_polyline_path(
                Vec2.generate(path.flattening(distance, segments)), flags=flags)

    def build_poly_path(hatch: Hatch, path: Path, flags: int):
        hatch.paths.add_polyline_path(
            # Vec2 removes the z-axis, which would be interpreted as bulge value!
            Vec2.generate(path.flattening(distance, segments)), flags=flags)

    if edge_path:
        boundary_factory = build_edge_path
    else:
        boundary_factory = build_poly_path

    yield from _hatch_converter(paths, boundary_factory, extrusion, dxfattribs)


def _hatch_converter(
        paths: Iterable[Path],
        add_boundary: Callable[[Hatch, Path, int], None],
        extrusion: 'Vertex' = Z_AXIS,
        dxfattribs: Optional[Dict] = None) -> Iterable[Hatch]:
    from .nesting import group_paths
    if isinstance(paths, Path):
        paths = [paths]
    else:
        paths = list(paths)
    if len(paths) == 0:
        return []

    extrusion = Vec3(extrusion)
    reference_point = paths[0].start
    dxfattribs = dxfattribs or dict()
    if not extrusion.isclose(Z_AXIS):
        ocs, elevation = _get_ocs(extrusion, reference_point)
        paths = transform_paths_to_ocs(paths, ocs)
        dxfattribs['elevation'] = Vec3(0, 0, elevation)
        dxfattribs['extrusion'] = extrusion
    elif reference_point.z != 0:
        dxfattribs['elevation'] = Vec3(0, 0, reference_point.z)
    dxfattribs.setdefault('solid_fill', 1)
    dxfattribs.setdefault('pattern_name', 'SOLID')
    dxfattribs.setdefault('color', const.BYLAYER)

    for group in group_paths(paths):
        if len(group) == 0:
            continue
        hatch = Hatch.new(dxfattribs=dxfattribs)
        external = group[0]
        external.close()
        add_boundary(hatch, external, 1)
        for hole in group[1:]:
            hole.close()
            add_boundary(hatch, hole, 0)
        yield hatch


def to_polylines3d(
        paths: Iterable[Path],
        *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        dxfattribs: Optional[Dict] = None) -> Iterable[Polyline]:
    """ Convert given `paths` into 3D :class:`~ezdxf.entities.Polyline` entities.

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
    dxfattribs['flags'] = const.POLYLINE_3D_POLYLINE
    for path in paths:
        p = Polyline.new(dxfattribs=dxfattribs)
        p.append_vertices(path.flattening(distance, segments))
        yield p


def to_lines(
        paths: Iterable[Path],
        *,
        distance: float = MAX_DISTANCE,
        segments: int = MIN_SEGMENTS,
        dxfattribs: Optional[Dict] = None) -> Iterable[Line]:
    """ Convert given `paths` into :class:`~ezdxf.entities.Line` entities.

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
    for path in paths:
        for vertex in path.flattening(distance, segments):
            if prev_vertex is None:
                prev_vertex = vertex
                continue
            dxfattribs['start'] = prev_vertex
            dxfattribs['end'] = vertex
            yield Line.new(dxfattribs=dxfattribs)
            prev_vertex = vertex
        prev_vertex = None


PathParts = Union[BSpline, List[Vec3]]


def to_bsplines_and_vertices(path: Path,
                             g1_tol: float = G1_TOL) -> Iterable[PathParts]:
    """ Convert a :class:`Path` object into multiple cubic B-splines and
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

    prev = path.start
    curves = []
    for cmd in path:
        if cmd.type == Command.CURVE3_TO:
            curve = Bezier3P([prev, cmd.ctrl, cmd.end])
        elif cmd.type == Command.CURVE4_TO:
            curve = Bezier4P([prev, cmd.ctrl1, cmd.ctrl2, cmd.end])
        elif cmd.type == Command.LINE_TO:
            curve = (prev, cmd.end)
        else:
            raise ValueError
        curves.append(curve)
        prev = cmd.end

    bezier = []
    polyline = []
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
        dxfattribs: Optional[Dict] = None) -> Iterable[Union[Spline, Polyline]]:
    """ Convert given `paths` into :class:`~ezdxf.entities.Spline` and 3D
    :class:`ezdxf.entities.Polyline` entities.

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

    for path in paths:
        for data in to_bsplines_and_vertices(path, g1_tol):
            if isinstance(data, BSpline):
                spline = Spline.new(dxfattribs=dxfattribs)
                spline.apply_construction_tool(data)
                yield spline
            else:
                attribs = dict(dxfattribs)
                attribs['flags'] = const.POLYLINE_3D_POLYLINE
                polyline = Polyline.new(dxfattribs=dxfattribs)
                polyline.append_vertices(data)
                yield polyline


# Interface to matplotlib.path.Path

@enum.unique
class MplCmd(enum.IntEnum):
    CLOSEPOLY = 79
    CURVE3 = 3
    CURVE4 = 4
    LINETO = 2
    MOVETO = 1
    STOP = 0


def from_matplotlib_path(mpath, curves=True) -> Iterable[Path]:
    """ Yields multiple :class:`Path` objects from a matplotlib `Path`_
    (`TextPath`_)  object. (requires matplotlib)

    .. versionadded:: 0.16

    .. _TextPath: https://matplotlib.org/3.1.1/api/textpath_api.html
    .. _Path: https://matplotlib.org/3.1.1/api/path_api.html#matplotlib.path.Path

    """
    path = None
    for vertices, cmd in mpath.iter_segments(curves=curves):
        cmd = MplCmd(cmd)
        if cmd == MplCmd.MOVETO:  # each "moveto" creates new path
            if path is not None:
                yield path
            path = Path(vertices)
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
            if not path.is_closed:
                path.line_to(path.start)
            yield path
            path = None
        elif cmd == MplCmd.STOP:  # not used
            break

    if path is not None:
        yield path


def to_matplotlib_path(paths: Iterable[Path], extrusion: 'Vertex' = Z_AXIS):
    """ Convert given `paths` into a single :class:`matplotlib.path.Path` object.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
    is the WCS z-axis. The matplotlib :class:`Path` is a 2D object with
    :ref:`OCS` coordinates and the z-elevation is lost. (requires matplotlib)

    Args:
        paths: iterable of :class:`Path` objects
        extrusion: extrusion vector for all paths

    Returns:
        matplotlib `Path`_ in OCS!

    .. versionadded:: 0.16

    """
    from matplotlib.path import Path as MatplotlibPath
    if not extrusion.isclose(Z_AXIS):
        paths = transform_paths_to_ocs(paths, OCS(extrusion))
    else:
        paths = list(paths)
    if len(paths) == 0:
        raise ValueError('one or more paths required')

    def add_command(code: MplCmd, point: Vec3):
        codes.append(code)
        vertices.append((point.x, point.y))

    vertices = []
    codes = []
    for path in paths:
        add_command(MplCmd.MOVETO, path.start)
        for cmd in path:
            if cmd.type == Command.LINE_TO:
                add_command(MplCmd.LINETO, cmd.end)
            elif cmd.type == Command.CURVE3_TO:
                add_command(MplCmd.CURVE3, cmd.ctrl)
                add_command(MplCmd.CURVE3, cmd.end)
            elif cmd.type == Command.CURVE4_TO:
                add_command(MplCmd.CURVE4, cmd.ctrl1)
                add_command(MplCmd.CURVE4, cmd.ctrl2)
                add_command(MplCmd.CURVE4, cmd.end)

    # STOP command is currently not required
    assert len(vertices) == len(codes)
    return MatplotlibPath(vertices, codes)


# Interface to PyQt5.QtGui.QPainterPath


def from_qpainter_path(qpath) -> Iterable[Path]:
    """ Yields multiple :class:`Path` objects from a `QPainterPath`_.
    (requires PyQt5)

    .. versionadded:: 0.16

    .. _QPainterPath: https://doc.qt.io/qt-5/qpainterpath.html

    """
    # QPainterPath stores only cubic Bèzier curves
    path = None
    vertices = list()
    for index in range(qpath.elementCount()):
        element = qpath.elementAt(index)
        cmd = element.type
        v = Vec3(element.x, element.y)

        if cmd == 0:  # MoveTo, each "moveto" creates new path
            if path is not None:
                yield path
            assert len(vertices) == 0
            path = Path(v)
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

    if path is not None:
        yield path


def to_qpainter_path(paths: Iterable[Path], extrusion: 'Vertex' = Z_AXIS):
    """ Convert given `paths` into a :class:`PyQt5.QtGui.QPainterPath` object.
    The `extrusion` vector is applied to all paths, all vertices are projected
    onto the plane normal to this extrusion vector, the default extrusion vector
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
    if not extrusion.isclose(Z_AXIS):
        paths = transform_paths_to_ocs(paths, OCS(extrusion))
    else:
        paths = list(paths)
    if len(paths) == 0:
        raise ValueError('one or more paths required')

    def qpnt(v: Vec3):
        return QPointF(v.x, v.y)

    qpath = QPainterPath()
    for path in paths:
        qpath.moveTo(qpnt(path.start))
        for cmd in path:
            if cmd.type == Command.LINE_TO:
                qpath.lineTo(qpnt(cmd.end))
            elif cmd.type == Command.CURVE3_TO:
                qpath.quadTo(qpnt(cmd.ctrl), qpnt(cmd.end))
            elif cmd.type == Command.CURVE4_TO:
                qpath.cubicTo(qpnt(cmd.ctrl1), qpnt(cmd.ctrl2), qpnt(cmd.end))
    return qpath
