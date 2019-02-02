# Purpose: curve objects
# Created: 26.03.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, List, Tuple, Optional
from ezdxf.ezmath.vector import Vector
from ezdxf.ezmath.bspline import bspline_control_frame
from ezdxf.ezmath.bspline import BSpline, BSplineU, BSplineClosed
from ezdxf.ezmath.bezier4p import Bezier4P
from ezdxf.ezmath.eulerspiral import EulerSpiral as _EulerSpiral

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, GenericLayoutType, Matrix44


class Bezier:
    """
    Bezier 2d/3d curve.

    The Bezier() class is implemented with multiple segments, each segment is an optimized 4 point bezier curve, the
    4 control points of the curve are: the start point (1) and the end point (4), point (2) is start point + start vector
    and point (3) is end point + end vector. Each segment has its own approximation count.

    """

    class Segment:
        def __init__(self, start: 'Vertex', end: 'Vertex', start_tangent: 'Vertex', end_tangent: 'Vertex',
                     segments: int):
            self.start = Vector(start)
            self.end = Vector(end)
            self.start_tangent = Vector(start_tangent)  # as vector, from start point
            self.end_tangent = Vector(end_tangent)  # as vector, from end point
            self.segments = segments

        def approximate(self) -> Iterable[Vector]:
            control_points = [
                self.start,
                self.start + self.start_tangent,
                self.end + self.end_tangent,
                self.end,
            ]
            bezier = Bezier4P(control_points)
            return bezier.approximate(self.segments)

    def __init__(self):
        # fit point, first control vector, second control vector, segment count
        self.points = []  # type: List[Tuple[Vector, Optional[Vector], Optional[Vector], Optional[int]]]

    def start(self, point: 'Vertex', tangent: 'Vertex') -> None:
        """
        Set start point and start tangent.

        Args:
            point: start point
            tangent: start tangent as vector, example: (5, 0, 0) means a
                     horizontal tangent with a length of 5 drawing units
        """
        self.points.append((point, None, tangent, None))

    def append(self, point: 'Vertex', tangent1: 'Vertex', tangent2: 'Vertex' = None, segments: int = 20):
        """
        Append a control point with two control tangents.

        Args:
            point: the control point
            tangent1: first control tangent as vector *left* of point
            tangent2: second control tangent as vector *right* of point, if omitted tangent2 = -tangent1
            segments: count of line segments for polyline approximation, count of line segments from previous
            control point to this point.

        """
        tangent1 = Vector(tangent1)
        if tangent2 is None:
            tangent2 = -tangent1
        else:
            tangent2 = Vector(tangent2)
        self.points.append((point, tangent1, tangent2, int(segments)))

    def _build_bezier_segments(self) -> Iterable[Segment]:
        if len(self.points) > 1:
            for from_point, to_point in zip(self.points[:-1], self.points[1:]):
                start_point = from_point[0]
                start_tangent = from_point[2]  # tangent2
                end_point = to_point[0]
                end_tangent = to_point[1]  # tangent1
                count = to_point[3]
                yield Bezier.Segment(start_point, end_point,
                                     start_tangent, end_tangent, count)
        else:
            raise ValueError('Two or more points needed!')

    def render(self, layout: 'GenericLayoutType', force3d: bool = False, dxfattribs: dict = None) -> None:
        """
        Render curve as DXF POLYLINE entity.

        Args:
            layout: ezdxf layout object
            force3d: force 3d polyline rendering
            dxfattribs: DXF attributes for base DXF entity (POLYLINE/LWPOLYLINE)

        """
        points = []
        for segment in self._build_bezier_segments():
            points.extend(segment.approximate())
        if force3d or any(p[2] for p in points):
            layout.add_polyline3d(points, dxfattribs=dxfattribs)
        else:
            layout.add_polyline2d(points, dxfattribs=dxfattribs)


class Spline:
    def __init__(self, points: Iterable['Vertex'] = None, segments: int = 100):
        if points is None:
            points = []
        self.points = points
        self.segments = int(segments)

    def subdivide(self, segments: int = 4) -> None:
        """
        Calculate overall segment count, where segments is the sub-segment count, segments=4, means 4 line segments
        between two definition points e.g. 4 definition points and 4 segments = 12 overall segments, useful for fit
        point rendering.

        Args:
            segments: sub-segments count between two definition points

        """
        self.segments = (len(self.points) - 1) * segments

    def render_as_fit_points(self, layout: 'GenericLayoutType', degree: int = 3, method: str = 'distance',
                             power: float = .5, dxfattribs: dict = None) -> None:
        """
        Render a B-spline as 2d/3d polyline, where the definition points are fit points.

           - 2d points in -> add_polyline2d()
           - 3d points in -> add_polyline3d()

        To get vertices at fit points, use method='uniform' and use Spline.subdivide(count), where
        count is the sub-segment count, count=4, means 4 line segments between two definition points.

        Args:
            layout: ezdxf layout
            degree: degree of B-spline
            method: 'uniform', 'distance' or 'centripetal', calculation method for parameter t
            power: power for 'centripetal', default is distance ^ .5
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = bspline_control_frame(self.points, degree=degree, method=method, power=power)
        vertices = list(spline.approximate(self.segments))
        if any(vertex.z != 0. for vertex in vertices):
            layout.add_polyline3d(vertices, dxfattribs=dxfattribs)
        else:
            layout.add_polyline2d(vertices, dxfattribs=dxfattribs)

    render = render_as_fit_points

    def render_open_bspline(self, layout: 'GenericLayoutType', degree: int = 3, dxfattribs: dict = None) -> None:
        """
        Render an open uniform BSpline as 3d polyline. Definition points are control points.

        Args:
            layout: ezdxf layout
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSpline(self.points, order=degree + 1)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_uniform_bspline(self, layout: 'GenericLayoutType', degree: int = 3, dxfattribs: dict = None) -> None:
        """
        Render a uniform BSpline as 3d polyline. Definition points are control points.

        Args:
            layout: ezdxf layout
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineU(self.points, order=degree + 1)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_closed_bspline(self, layout: 'GenericLayoutType', degree: int = 3, dxfattribs: dict = None) -> None:
        """
        Render a closed uniform BSpline as 3d polyline. Definition points are control points.

        Args:
            layout: ezdxf layout
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineClosed(self.points, order=degree + 1)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_open_rbspline(self, layout: 'GenericLayoutType', weights: Iterable[float], degree: int = 3,
                             dxfattribs: dict = None) -> None:
        """
        Render a rational open uniform BSpline as 3d polyline.

        Args:
            layout: ezdxf layout
            weights: list of weights, requires a weight value for each defpoint.
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSpline(self.points, order=degree + 1, weights=weights)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_uniform_rbspline(self, layout: 'GenericLayoutType', weights: Iterable[float], degree: int = 3,
                                dxfattribs: dict = None) -> None:
        """
        Render a rational uniform BSpline as 3d polyline.

        Args:
            layout: ezdxf layout
            weights: list of weights, requires a weight value for each defpoint.
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineU(self.points, order=degree + 1, weights=weights)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_closed_rbspline(self, layout: 'GenericLayoutType', weights: Iterable[float], degree: int = 3,
                               dxfattribs: dict = None) -> None:
        """
        Render a rational BSpline as 3d polyline.

        Args:
            layout: ezdxf layout
            weights: list of weights, requires a weight value for each defpoint.
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineClosed(self.points, order=degree + 1, weights=weights)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)


class EulerSpiral:
    """
    Euler spiral (clothoid) for *curvature* (Radius of curvature).

    This is a parametric curve, which always starts at the origin.

    """

    def __init__(self, curvature: float = 1):
        self.spiral = _EulerSpiral(float(curvature))

    def render_polyline(self, layout: 'GenericLayoutType', length: float = 1, segments: int = 100,
                        matrix: 'Matrix44' = None, dxfattribs: dict = None):
        """
        Render curve as polyline.

        Args:
            layout: ezdxf layout
            length: length measured along the spiral curve from its initial position
            segments: count of line segments to use, vertex count is segments+1
            matrix: transformation matrix as ezdxf.ezmath.Matrix44
            dxfattribs: DXF attributes for POLYLINE

        Returns: DXF Polyline entity

        """
        points = self.spiral.approximate(length, segments)
        if matrix is not None:
            points = matrix.transform_vectors(points)
        return layout.add_polyline3d(list(points), dxfattribs=dxfattribs)

    def render_spline(self, layout: 'GenericLayoutType', length: float = 1, fit_points: int = 10, degree: int = 3,
                      matrix: 'Matrix44' = None, dxfattribs: dict = None):
        """
        Render curve as B-spline.

        Args:
            layout: ezdxf layout 
            length: length measured along the spiral curve from its initial position
            fit_points: count of spline fit points to use
            degree: degree of B-spline
            matrix: transformation matrix as ezdxf.ezmath.Matrix44
            dxfattribs: DXF attributes for POLYLINE

        Returns: DXF Spline entity

        """
        spline = self.spiral.bspline(length, fit_points, degree=degree)
        points = spline.control_points
        if matrix is not None:
            points = matrix.transform_vectors(points)
        return layout.add_open_spline(
            control_points=points,
            degree=spline.degree,
            knots=spline.knot_values(),
            dxfattribs=dxfattribs,
        )
