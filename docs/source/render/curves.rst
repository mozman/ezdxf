.. module:: ezdxf.render

Spline
======

Render B-spline as 2D/3D :class:`Polyline`, can be used with DXF R12. The advantage over :class:`R12Spline` is the real
3D support which means the B-spline curve vertices has not to be in a plane and no hassle with :ref:`UCS` for 3D
placing.

.. class:: Spline

.. method:: Spline.__init__(points=None, segments=100)

    :param points: spline definition points
    :param segments: count of line segments for approximation, vertex count is segments+1

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

R12Spline
=========

DXF R12 supports 2D B-splines, but Autodesk do not document the usage in the DXF Reference. The base entity for splines
in DXF R12 is the POLYLINE entity. The spline itself is always in a plane, but as any 2D entity, the spline can be
transformed into the 3D object by elevation and extrusion (:ref:`OCS`, :ref:`UCS`).

The result is not better than :class:`Spline`, it is also just a POLYLINE, but as with all tools, I never know if
someone needs it some day.

:class: R12Spline

.. method:: R12Spline.__init__(control_points, degree=2, closed=True)

    :param control_points: B-spline control frame vertices as (x, y) tuples
    :param degree: degree of B-spline, 2 or 3 is valid
    :param closed: True for closed curve

.. method:: R12Spline.render(layout, segments=40, ucs=None, dxfattribs=None)

    Renders the B-spline into *layout* as 2D :class:`Polyline` entity. Use an :class:`~ezdxf.ezmath.UCS` to place the
    2D spline in 3D space, see :meth:`R12Spline.approximate` for more information.

    :param layout:  ezdxf :class:`Layout`
    :param segments: count of line segments to use, vertex count is segments+1
    :param ucs: :class:`~ezdxf.ezmath.UCS` definition, control points in ucs coordinates.
    :param dxfattribs: DXF attributes for :class:`Polyline`
    :returns: the :class:`Polyline` object

.. method:: R12Spline.approximate(segments=40, ucs=None)

    :param segments: count of line segments to use, vertex count is segments+1
    :param ucs: :class:`~ezdxf.ezmath.UCS` definition, control points in ucs coordinates.
    :returns: list of vertices in :class:`~ezdxf.ezmath.OCS` as :class:`~ezdxf.ezmath.Vector` objects

    Approximate B-spline by a polyline with *segments* line segments. If *ucs* is not None, ucs defines an
    :class:`~ezdxf.ezmath.UCS`, to transformed the curve into :ref:`OCS`. The control points are placed in this UCS
    xy-plane, you shouldn't use z-axis coordinates, if so make sure all control points are a plane parallel to the OCS
    base plane (UCS xy-plane), else the result is unpredictable and depends on the used CAD application (may be crash).


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

.. method:: EulerSpiral.__init__(curvature=1)

    :param curvature: Radius of curvature

.. method:: EulerSpiral.render_polyline(layout, length=1, segments=100, matrix=None, dxfattribs=None)

    Render euler spiral as 3D :class:`Polyline` entity into layout.

    :param layout: ezdxf :class:`Layout` object
    :param length: length measured along the spiral curve from its initial position
    :param segments: count of line segments to use, vertex count is segments+1
    :param matrix: transformation matrix as :class:`~ezdxf.ezmath.Matrix44`
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}

.. method:: EulerSpiral.render_spline(layout, length=1, fit_points=10, degree=3, matrix=None, dxfattribs=None)

    Render euler spiral as :class:`Spline` entity into layout, DXF version R2000 or later required.

    :param layout: ezdxf :class:`Layout` object
    :param length: length measured along the spiral curve from its initial position
    :param fit_points: count of spline fit points to use
    :param degree: degree of spline
    :param matrix: transformation matrix as :class:`~ezdxf.ezmath.Matrix44`
    :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}
