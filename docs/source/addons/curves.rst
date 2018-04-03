.. module:: ezdxf.addons

These entities render to :class:`Polyline` entities for usage with DXF version R12, which do not support :class:`Ellipse` and
:class:`Spline`. If you are using DXF version R2000 or later there is no need for using :class:`Ellipse` or :class:`Spline`.

Ellipse
=======

Render ellipse as 2D :class:`Polyline`.

.. class:: Ellipse

.. method:: Ellipse.__init__(center=(0, 0), rx=1.0, ry=1.0, startangle=0., endangle=360., rotation=0., segments=100)

    :param center: center point as (x, y) tuple.
    :param rx: radius in x-axis
    :param ry: radius in y-axis
    :param start_angle: start angle in degrees
    :param end_angle: end angle in degrees
    :param rotation: rotation angle in degrees
    :param segments: count of line segments,

.. method:: Ellipse.render(layout, dxfattribs=None)

    Render ellipse as 2D :class:`Polyline` entity into layout.

    :param layout: ezdxf :class:`Layout` object
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}

Spline
======

Render B-spline as 2D/3D :class:`Polyline`.

.. class:: Spline

.. method:: Spline.__init__(points=None, segments=100)

    :param points: spline definition points
    :param segemnts: count of line segemnts for approximation, vertex count is segments+1

.. method:: Spline.render_as_fit_points(layout, degree=3, method='distance', power=.5, dxfattribs=None)

    Render a B-spline as 2d/3d polyline, where the definition points are fit points.

       - 2d points in -> add_polyline2d()
       - 3d points in -> add_polyline3d()

    To get vertices at fit points, use method='uniform' and use Spline.subdivide(count), where
    count is the sub-segment count, count=4, means 4 line segments between two definition points.


    :param layout: ezdxf :class:`Layout` object
    :param degree: degree of B-spline
    :param method: 'uniform', 'distance' or 'centripetal', calculation method for parameter t
    :param power: power for 'centripetal', default is distance ^ .5
    :param dxfattribs: DXF attributes for :class:`Polyline`

.. method:: Spline.render_open_bspline(layout, degree=3, dxfattribs=None)

    Render an open uniform BSpline as 3D :class:`Polyline`. Definition points are control points.

    :param layout: ezdxf :class:`Layout` object
    :param degree: degree of B-spline, (order = degree + 1)
    :param dxfattribs: DXF attributes for :class:`Polyline`

.. method:: Spline.render_uniform_bspline(layout, degree=3, dxfattribs=None):

    Render a uniform BSpline as 3D :class:`Polyline`. Definition points are control points.

    :param layout: ezdxf :class:`Layout` object
    :param degree: degree of B-spline, (order = degree + 1)
    :param dxfattribs: DXF attributes for :class:`Polyline`

.. method:: Spline.render_closed_bspline(layout, degree=3, dxfattribs=None)

    Render a closed uniform BSpline as 3D :class:`Polyline`. Definition points are control points.

    :param layout: ezdxf :class:`Layout` object
    :param degree: degree of B-spline, (order = degree + 1)
    :param dxfattribs: DXF attributes for :class:`Polyline`

.. method:: Spline.render_open_rbspline(layout, weights, degree=3, dxfattribs=None)

    Render a rational open uniform BSpline as 3D :class:`Polyline`. Definition points are control points.

    :param layout: ezdxf :class:`Layout` object
    :param weights: list of weights, requires a weight value for each defpoint.
    :param degree: degree of B-spline, (order = degree + 1)
    :param dxfattribs: DXF attributes for :class:`Polyline`

.. method:: Spline.render_uniform_rbspline(layout, weights, degree=3, dxfattribs=None)

    Render a rational uniform BSpline as 3D :class:`Polyline`. Definition points are control points.

    :param layout: ezdxf :class:`Layout` object
    :param weights: list of weights, requires a weight value for each defpoint.
    :param degree: degree of B-spline, (order = degree + 1)
    :param dxfattribs: DXF attributes for :class:`Polyline`

.. method:: Spline.render_closed_rbspline(layout, weights, degree=3, dxfattribs=None)

    Render a rational BSpline as 3D :class:`Polyline`. Definition points are control points.

    :param layout: ezdxf :class:`Layout` object
    :param weights: list of weights, requires a weight value for each defpoint.
    :param degree: degree of B-spline, (order = degree + 1)
    :param dxfattribs: DXF attributes for :class:`Polyline`


Bezier
======

Render bezier curve as 3D :class:`Polyline`.

The :class:`Bezier` class is implemented with multiple segments, each segment is an optimized 4 point bezier curve, the
4 control points of the curve are: the start point (1) and the end point (4), point (2) is start point + start vector
and point (3) is end point + end vector. Each segment has its own approximation count.

.. class:: Bezier

.. method:: Bezier.start(point, tangent)

    Set start point and start tangent.

    :param point: start point as (x, y, z) tuple
    :param tangent: start tangent as vector, also (x, y, z) tuple

.. method:: Bezier.append(point, tangent1, tangent2=None, segments=20):

    Append a control point with two control tangents.

    :param point: the control point as (x, y, z) tuple
    :param tangent1: first control tangent as vector *left* of point
    :param tangent2: second control tangent as vector *right* of point, if omitted tangent2 = -tangent1
    :param segments: count of line segments for polyline approximation, count of line segments from previous control point to this point.

.. method:: Bezier.render(layout, force3d=False, dxfattribs=None)

    Render bezier curve as 2D or 3D :class:`Polyline` entity into layout.

    :param layout: ezdxf :class:`Layout` object
    :param force3d: force rendering as 3D :class:`Polyline`
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}

EulerSpiral
===========

Render `euler spiral <https://en.wikipedia.org/wiki/Euler_spiral>`_ as 3D :class:`Polyline` or :class:`Spline`.

.. class:: EulerSpiral

.. method:: EulerSpiral.render(layout, segments=100, dxfattribs=None)

    Render euler spiral as 3D :class:`Polyline` entity into layout.

    :param layout: ezdxf :class:`Layout` object
    :param segments: count of line segments to use, vertex count is segments+1
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}

.. method:: EulerSpiral.render_spline(layout, segments=10, degree=3, dxfattribs=None)

    Render euler spiral as :class:`Spline` entity into layout, DXF version R2000 or later required.

    :param layout: ezdxf :class:`Layout` object
    :param segments: count of spline fit points to use
    :param degree: degree of spline
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}
