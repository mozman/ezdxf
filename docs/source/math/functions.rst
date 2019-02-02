.. _math utilities:

.. module:: ezdxf.ezmath

This utilities located in module :mod:`ezdxf.ezmath`::

    from ezdxf.ezmath import Vector


Functions
---------

.. function:: is_close_points(p1, p2)

    Returns True if all axis of p1 and p2 are close.

.. function:: bspline_control_frame(fit_points, degree=3, method='distance', power=.5)

    Generates the control points for the  B-spline control frame by `Curve Global Interpolation`_.
    Given are the fit points and the degree of the B-spline. The function provides 3 methods for generating the
    parameter vector t:

    1. method = ``uniform``, creates a uniform t vector, form 0 to 1 evenly spaced; see `uniform`_ method
    2. method = ``distance``, creates a t vector with values proportional to the fit point distances, see `chord length`_ method
    3. method = ``centripetal``, creates a t vector with values proportional to the fit point distances^power; see `centripetal`_ method


    :param fit_points: fit points of B-spline, as list of (x, y[, z]) tuples
    :param degree: degree of B-spline
    :param method: calculation method for parameter vector t
    :param power: power for centripetal method

    :returns: a :class:`BSpline` object, with :attr:`BSpline.control_points` containing the calculated control points,
              also :meth:`BSpline.knot_values` returns the used `knot`_ values.

Bulge Related Functions
-----------------------


.. function:: bulge_center(start_point, end_point, bulge)

    Calculate center of arc described by the given bulge parameters.

    :param start_point: start point as (x, y) tuple
    :param end_point: end point as (x, y) tuple
    :param bulge: bulge value as float

    :return: arc center as :class:`Vector`

.. function:: bulge_radius(start_point, end_point, bulge)

    Calculate radius of arc defined by the given bulge parameters.

    :param start_point: start point as (x, y) tuple
    :param end_point: end point as (x, y) tuple
    :param bulge: bulge value as float

    :return: arc radius as float

.. function:: arc_to_bulge(center, start_angle, end_angle, radius)

    Calculate bulge parameters from arc parameters.

    :param center: circle center point as (x, y) tuple
    :param start_angle: start angle in radians
    :param end_angle: end angle in radians
    :param radius: circle radius

    :return: (start_point, end_point, bulge)

.. function:: bulge_to_arc(start_point, end_point, bulge)

    Calculate arc parameters from bulge parameters.

    :param start_point: start point as (x, y) tuple
    :param end_point: end point as (x, y) tuple
    :param bulge: bulge value as float

    :return: (center, start_angle, end_angle, radius)

.. function:: bulge_3_points(start_point, end_point, point)

    Calculate bulge value defined by three points.

    :param start_point: start point of arc
    :param end_point: end point of arc
    :param point: arbitrary point on arc

    :return: bulge value as float

.. _Curve Global Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
