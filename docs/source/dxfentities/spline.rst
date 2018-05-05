Spline
======

.. class:: Spline(GraphicEntity)

    Introduced in DXF version R13 (AC1012), dxftype is SPLINE.

    A spline curve, all coordinates have to be 3D coordinates even the spline is only a 2D planar curve.

    The spline curve is defined by a set of *fit points*, the spline curve passes all these fit points.
    The *control points* defines a polygon which influences the form of the curve, the first control point should be
    identical with the first fit point and the last control point should be identical the last fit point.

    Don't ask me about the meaning of *knot values* or *weights* and how they influence the spline curve, I don't know
    it, ask your math teacher or the internet. I think the *knot values* can be ignored, they will be calculated by the
    CAD program that processes the DXF file and the weights determines the influence 'strength' of the *control points*,
    in normal case the weights are all 1 and can be left off.

    To create a :class:`Spline` curve you just need a bunch of *fit points*, *control point*, *knot_values* and *weights*
    are optional (tested with AutoCAD 2010). If you add additional data, be sure that you know what you do.

    Create :class:`Spline` in layouts and blocks by factory function :meth:`~Layout.add_spline`.

    For more information about spline mathematics go to `Wikipedia`_.

.. _Wikipedia: https://en.wikipedia.org/wiki/Spline_%28mathematics%29

DXF Attributes for Spline
-------------------------

    All points in :ref:`WCS` as (x, y, z) tuples

    :ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Spline.dxf.degree

    Degree of the spline curve (int)

.. attribute:: Spline.dxf.flags

    Bit coded option flags, constants defined in :mod:`ezdxf.const`:

    =================== ======= ===========
    Spline.dxf.flags    Value   Description
    =================== ======= ===========
    CLOSED_SPLINE       1       Spline is closed
    PERIODIC_SPLINE     2
    RATIONAL_SPLINE     4
    PLANAR_SPLINE       8
    LINEAR_SPLINE       16      planar bit is also set
    =================== ======= ===========

.. attribute:: Spline.dxf.n_knots

    Count of knot values (int), automatically set by ezdxf (read only)

.. attribute:: Spline.dxf.n_fit_points

    Count of fit points (int), automatically set by ezdxf (read only)

.. attribute:: Spline.dxf.n_control_points

    Count of control points (int), automatically set by ezdxf (read only)

.. attribute:: Spline.dxf.knot_tolerance

    Knot tolerance (float); default=1e-10

.. attribute:: Spline.dxf.fit_tolerance

    Fit tolerance (float); default=1e-10

.. attribute:: Spline.dxf.control_point_tolerance

    Control point tolerance (float); default=1e-10

.. attribute:: Spline.dxf.start_tangent

    Start tangent vector as (3D Point in :ref:`WCS`)

.. attribute:: Spline.dxf.end_tangent

    End tangent vector as (3D Point in :ref:`WCS`)

.. seealso::

    :ref:`tut_spline`

Spline Attributes
-----------------

.. attribute:: Spline.closed

    True if spline is closed else False.  A closed spline has a connection from the last control point
    to the first control point. (read/write)

.. attribute:: Spline.control_points

    Returns the control points as :class:`ControlPoints` object in :ref:`WCS`.

.. attribute:: Spline.fit_points

    Returns the fit points as :class:`FitPoints` object in :ref:`WCS`.

.. attribute:: Spline.knot_values

    Returns the knot values as :code:`array.array('f')`.

.. attribute:: Spline.weights

    Returns the control point weights as :code:`array.array('f')`.

Spline Methods
--------------

.. method:: Spline.set_control_points(points)

    Set control points, *points* is a list (container or generator) of (x, y, z) tuples in :ref:`WCS`.

.. method:: Spline.set_fit_points(points)

    Set fit points, *points* is a list (container or generator) of (x, y, z) tuples in :ref:`WCS`.

.. method:: Spline.set_knot_values(values)

    Set knot values, *values* is a list (container or generator) of *floats*.

.. method:: Spline.set_weights(values)

    Set weights, *values* is a list (container or generator) of *floats*.

.. method:: Spline.set_open_uniform(control_points, degree=3)

    Open B-spline with uniform knot vector, start and end at your first and last control points.

.. method:: Spline.set_uniform(control_points, degree=3)

    B-spline with uniform knot vector, does NOT start and end at your first and last control points.

.. method:: Spline.set_periodic(control_points, degree=3)

    Closed B-spline with uniform knot vector, start and end at your first control point.

.. method:: Spline.set_open_rational(control_points, weights, degree=3)

    Open rational B-spline with uniform knot vector, start and end at your first and last control points, and has
    additional control possibilities by weighting each control point.

.. method:: Spline.set_uniform_rational(control_points, weights, degree=3)

    Rational B-spline with uniform knot vector, does NOT start and end at your first and last control points, and
    has additional control possibilities by weighting each control point.

.. method:: Spline.set_periodic_rational(control_points, weights, degree=3)

    Closed rational B-spline with uniform knot vector, start and end at your first control point, and has
    additional control possibilities by weighting each control point.

.. method:: Spline.edit_data()

    Context manager for all spline data, returns :class:`SplineData`.

    Fit points, control points, knot values and weights can be manipulated as lists by using the general context manager
    :meth:`Spline.edit_data`::

        with spline.edit_data() as spline_data:
            # spline_data contains list like objects: add, change or delete items as you want
            # fit_points and control_points have to be (x, y, z) tuples
            # knot_values and weights have to be numbers
            spline_data.fit_points.append((200, 300, 0))  # append a fit point
            # on exit the context manager sets spline data automatically and updates all counters

SplineData
----------

.. class:: SplineData

.. attribute:: SplineData.fit_points

    :class:`FitPoints` object  with list like behavior.

.. attribute:: SplineData.control_points

    :class:`ControlPoints` object with list like behavior.

.. attribute:: SplineData.knot_values

    :class:`Spline` knot values as :code:`array.array('f')`.

.. attribute:: SplineData.weights

    :class:`Spline` weights as :code:`array.array('f')`.


ControlPoints
-------------

    A list like object to store vertices as :code:`array.array('d')` flat list.

    Supports most standard list operations like indexing, iteration, insert, append, extend and so on.

.. class:: ControlPoints(VertexArray)

    For attributes and methods see :class:`~ezdxf.lldxf.VertexArray`


FitPoints
---------

.. class:: FitPoints(VertexArray)

    Same as :class:`ControlPoints`.

    For attributes and methods see :class:`~ezdxf.lldxf.VertexArray`
