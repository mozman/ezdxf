# Copyright (c) 2020-2021, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, List, Iterable, Sequence, NamedTuple, Union
from collections import abc
from enum import Enum
import warnings
import math
from ezdxf.math import (
    Vec3, NULLVEC, Z_AXIS, OCS, Bezier4P, Matrix44, bulge_to_arc,
    cubic_bezier_from_ellipse, ConstructionEllipse, BSpline,
    has_clockwise_orientation, global_bspline_interpolation,
)

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        LWPolyline, Polyline, Vertex, Spline, Ellipse, Arc, Circle, DXFEntity,
        Line, Solid, Viewport, Image,
    )
    from ezdxf.entities.hatch import PolylinePath, EdgePath, TPath

__all__ = ['Path', 'Command', 'make_path', 'has_path_support']


class Command(Enum):
    LINE_TO = 1  # (LINE_TO, end vertex)
    CURVE4_TO = 2  # (CURVE4_TO, end vertex, ctrl1, ctrl2) cubic bezier
    CURVE3_TO = 3  # (CURVE3_TO, end vertex, ctrl1) quadratic bezier


class LineTo(NamedTuple):
    end: Vec3

    @property
    def type(self):
        return Command.LINE_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return LineTo(end=ocs.to_wcs(self.end.replace(z=elevation)))


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


class Curve3To(NamedTuple):
    end: Vec3
    ctrl1: Vec3

    @property
    def type(self):
        return Command.CURVE3_TO

    def to_wcs(self, ocs: OCS, elevation: float):
        return Curve3To(
            end=ocs.to_wcs(self.end.replace(z=elevation)),
            ctrl1=ocs.to_wcs(self.ctrl1.replace(z=elevation)),
        )


PathElement = Union[LineTo, Curve4To, Curve3To]


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

    def curve_to(self, location: 'Vertex', ctrl1: 'Vertex',
                 ctrl2: 'Vertex') -> None:
        """ Add a cubic Bèzier-curve from actual path end point to `location`,
        `ctrl1` and `ctrl2` are the control points for the cubic Bèzier-curve.
        """
        self._commands.append(Curve4To(
            end=Vec3(location), ctrl1=Vec3(ctrl1), ctrl2=Vec3(ctrl2))
        )

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
            elif cmd.type == Command.CURVE4_TO:
                path.curve_to(prev_end, cmd.ctrl2, cmd.ctrl1)
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

    def add_curves(self, curves: Iterable[Bezier4P]) -> None:
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
            self.curve_to(end, ctrl1, ctrl2)

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
            self.add_curves(curves)

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
        (see :meth:`add_curves`).

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
        self.add_curves(
            cubic_bezier_from_ellipse(ellipse, segments)
        )

    def add_spline(self, spline: BSpline, level=4, reset=True) -> None:
        """ Add a B-spline as multiple cubic Bèzier-curves.

        Non-rational B-splines of 3rd degree gets a perfect conversion to
        cubic bezier curves with a minimal count of curve segments, all other
        B-spline require much more curve segments for approximation.

        Auto-detect connection point, if none is close a line from the path
        end point to the spline start point will be added
        (see :meth:`add_curves`).

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
        self.add_curves(curves)

    def approximate(self, segments: int = 20) -> Iterable[Vec3]:
        """ Approximate path by vertices, `segments` is the count of
        approximation segments for each cubic bezier curve.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        """

        def approx_curve(s, c1, c2, e) -> Iterable[Vec3]:
            return Bezier4P((s, c1, c2, e)).approximate(segments)

        yield from self._approximate(approx_curve)

    def flattening(self, distance: float,
                   segments: int = 16) -> Iterable[Vec3]:
        """ Approximate path by vertices and use adaptive recursive flattening
        to approximate cubic Bèzier curves. The argument `segments` is the
        minimum count of approximation segments for each curve, if the distance
        from the center of the approximation segment to the curve is bigger than
        `distance` the segment will be subdivided.

        Does not yield any vertices for empty paths, where only a start point
        is present!

        Args:
            distance: maximum distance from the center of the cubic (C3)
                curve to the center of the linear (C1) curve between two
                approximation points to determine if a segment should be
                subdivided.
            segments: minimum segment count

        """

        def approx_curve(s, c1, c2, e) -> Iterable[Vec3]:
            return Bezier4P((s, c1, c2, e)).flattening(distance, segments)

        yield from self._approximate(approx_curve)

    def _approximate(self, approx_curve) -> Iterable[Vec3]:
        if not self._commands:
            return

        start = self._start
        yield start

        for cmd in self._commands:
            end_location = cmd.end
            if cmd.type == Command.LINE_TO:
                yield end_location
            elif cmd.type == Command.CURVE4_TO:
                pts = iter(
                    approx_curve(start, cmd.ctrl1, cmd.ctrl2, end_location)
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
            elif cmd.type == Command.CURVE4_TO:
                loc, ctrl1, ctrl2 = m.transform_vertices(
                    (cmd.end, cmd.ctrl1, cmd.ctrl2)
                )
                new_path.curve_to(loc, ctrl1, ctrl2)
            else:
                raise ValueError(f'Invalid command: {cmd.type}')

        return new_path


def _reverse_bezier_curves(curves: List[Bezier4P]) -> List[Bezier4P]:
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
