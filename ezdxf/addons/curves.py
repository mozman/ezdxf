# Purpose: curve objects
# Created: 26.03.2010, 2018 adapted for ezdxf
# Copyright (c) 2010-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from math import sin, cos, radians, fmod
from ezdxf.algebra.vector import Vector
from ezdxf.algebra.base import is_close
from ezdxf.algebra.bspline import bspline_control_frame
from ezdxf.algebra.bspline import BSpline, BSplineU, BSplineClosed
from ezdxf.algebra.bezier4p import Bezier4P
from ezdxf.algebra.clothoid import Clothoid as _ClothoidValues


class Ellipse(object):
    def __init__(self, center=(0., 0., 0.), rx=1.0, ry=1.0, startangle=0., endangle=360., rotation=0., segments=100):
        self.center = Vector(center)
        self.rx = float(rx)
        self.ry = float(ry)
        self.startangle = float(startangle)
        self.endangle = float(endangle)
        self.rotation = float(rotation)
        self.segments = int(segments)

    def render(self, layout, dxfattribs=None):
        def curve_point(alpha):
            point = self.center + Vector(cos(alpha) * self.rx, sin(alpha) * self.ry)
            return point.rot_z_deg(self.rotation)

        def normalize_angle(angle):
            angle = fmod(angle, 360.)
            if angle < 0:
                angle += 360.
            return angle

        points = []
        delta = (self.endangle - self.startangle) / self.segments
        for segment in range(self.segments):
            alpha = self.startangle + delta * segment
            points.append(curve_point(radians(alpha)))

        if dxfattribs is None:
            dxfattribs = {}
        dxfattribs['closed'] = is_close(self.startangle, normalize_angle(self.endangle))
        layout.add_polyline2d(points, dxfattribs=dxfattribs)


class Bezier(object):
    """
    Bezier 2d/3d curve.

    The Bezier() class is implemented with multiple segments, each segment is an optimized 4 point bezier curve, the
    4 control points of the curve are: the start point (1) and the end point (4), point (2) is start point + start vector
    and point (3) is end point + end vector. Each segment has its own approximation count.

    """
    class Segment(object):
        def __init__(self, start, end, start_tangent, end_tangent, segments):
            self.start = Vector(start)
            self.end = Vector(end)
            self.start_tangent = Vector(start_tangent)  # as vector, from start point
            self.end_tangent = Vector(end_tangent)  # as vector, from end point
            self.segments = segments

        def approximate(self):
            control_points = [
                self.start,
                self.start + self.start_tangent,
                self.end + self.end_tangent,
                self.end,
            ]
            bezier = Bezier4P(control_points)
            return bezier.approximate(self.segments)

    def __init__(self):
        self.points = []

    def start(self, point, tangent):
        """
        Set start point and start tangent.

        Args:
            point: start point
            tangent: start tangent as vector, example: (5, 0, 0) means a
                     horizontal tangent with a length of 5 drawing units
        """
        self.points.append((point, None, tangent, None))

    def append(self, point, tangent1, tangent2=None, segments=20):
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

    def _build_bezier_segments(self):
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

    def render(self, layout, force3d=False, dxfattribs=None):
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


class Spline(object):
    def __init__(self, points=None, segments=100):
        if points is None:
            points = []
        self.points = points
        self.segments = int(segments)

    def subdivide(self, segments=4):
        """
        Calculate overall segment count, where segments is the sub-segment count, segments=4, means 4 line segments
        between two definition points e.g. 4 definition points and 4 segments = 12 overall segments, useful for fit
        point rendering.

        Args:
            segments: sub-segments count between two definition points

        """
        self.segments = (len(self.points)-1) * segments

    def render_as_fit_points(self, layout, degree=3, method='distance', power=.5, dxfattribs=None):
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

    def render_open_bspline(self, layout, degree=3, dxfattribs=None):
        """
        Render aa open uniform BSpline as 3d polyline. Definition points are control points.

        Args:
            layout: ezdxf layout
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSpline(self.points, order=degree+1)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_uniform_bspline(self, layout, degree=3, dxfattribs=None):
        """
        Render a uniform BSpline as 3d polyline. Definition points are control points.

        Args:
            layout: ezdxf layout
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineU(self.points, order=degree+1)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_closed_bspline(self, layout, degree=3, dxfattribs=None):
        """
        Render a closed uniform BSpline as 3d polyline. Definition points are control points.

        Args:
            layout: ezdxf layout
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineClosed(self.points, order=degree+1)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_open_rbspline(self, layout, weights, degree=3, dxfattribs=None):
        """
        Render a rational open uniform BSpline as 3d polyline.

        Args:
            layout: ezdxf layout
            weights: list of weights, requires a weight value for each defpoint.
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSpline(self.points, order=degree+1, weights=weights)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_uniform_rbspline(self, layout, weights, degree=3, dxfattribs=None):
        """
        Render a rational uniform BSpline as 3d polyline.

        Args:
            layout: ezdxf layout
            weights: list of weights, requires a weight value for each defpoint.
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineU(self.points, order=degree+1, weights=weights)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)

    def render_closed_rbspline(self, layout, weights, degree=3, dxfattribs=None):
        """
        Render a rational BSpline as 3d polyline.

        Args:
            layout: ezdxf layout
            weights: list of weights, requires a weight value for each defpoint.
            degree: B-spline degree (order = degree + 1)
            dxfattribs: DXF attributes for POLYLINE

        """
        spline = BSplineClosed(self.points, order=degree+1, weights=weights)
        layout.add_polyline3d(list(spline.approximate(self.segments)), dxfattribs=dxfattribs)


class Clothoid(object):
    def __init__(self, start=(0, 0), rotation=0., length=1., paramA=1.0, mirror=''):
        self.start = Vector(start)
        self.rotation = float(rotation)
        self.length = float(length)
        self.paramA = float(paramA)
        self.mirrorx = 'x' in mirror.lower()
        self.mirrory = 'y' in mirror.lower()

    def render(self, layout, segments=100,  dxfattribs=None):
        clothoid = _ClothoidValues(self.paramA)
        points = clothoid.approximate(self.length, segments)
        layout.add_polyline3d(list(self.transform(points)), dxfattribs=dxfattribs)

    def transform(self, points):
        rotation = radians(self.rotation)
        for point in points:
            if self.mirrorx:
                point = Vector(point[0], -point[1])
            if self.mirrory:
                point = Vector(-point[0], point[1])
            yield self.start + point.rot_z_rad(rotation)

    def render_spline(self, layout, segments=10, dxfattribs=None):
        clothoid = _ClothoidValues(self.paramA)
        spline = clothoid.bspline(self.length, segments)
        points = self.transform(spline.control_points)
        layout.add_open_spline(
            control_points=points,
            degree=spline.degree,
            knots=spline.knot_values(),
            dxfattribs=dxfattribs,
        )
