.. _algebra utilities:

.. module:: ezdxf.algebra

This utilities are located at :mod:`ezdxf.algebra`, import::

    from ezdxf.algebra import Vector


Functions
---------

.. function:: ezdxf.algebra.is_close(a, b)

    Returns True if value is close to value b, uses :code:`math.isclose(a, b, abs_tol=1e-9)` for Python 3, and emulates
    this function for Python 2.7.

.. function:: ezdxf.algebra.is_close_points(p1, p2)

    Returns True if all axis of p1 and p2 are close.

.. function:: ezdxf.algebra.bspline_control_frame(fit_points, degree=3, method='distance', power=.5)

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


Vector
------

.. class:: Vector

Matrix44
--------

.. class:: Matrix44

BSpline
-------

.. class:: BSpline

    Calculate the vertices of a B-spline curve, using an uniform open `knot`_ vector (`clamped curve`_).

.. attribute:: BSpline.control_points

    Control points as list of :class:`Vector` objects

.. attribute:: BSpline.count

    Count of control points, (n + 1 in math definition).

.. attribute:: BSpline.order

    Order of B-spline = degree +  1

.. attribute:: BSpline.degree

    Degree (p) of B-spline = order - 1

.. attribute:: BSpline.max_t

    Max `knot`_ value.

.. method:: BSpline.knot_values()

    Returns a list of `knot`_ values as floats, the knot vector always has order+count values (n + p + 2 in math definition)

.. method:: BSpline.basis_values(t)

    Returns the `basis`_ vector for position t.

.. method:: BSpline.approximate(segments)

    Approximates the whole B-spline from 0 to max_t, by line segments as a list of vertices, vertices count = segments + 1

.. method:: BSpline.point(t)

    Returns the B-spline vertex at position t as (x, y[, z]) tuple.


BSplineU
--------

.. class:: BSpline(BSpline)

    Calculate the points of a B-spline curve, uniform (periodic) `knot`_ vector (`open curve`_).

BSplineClosed
-------------

.. class:: BSplineClosed(BSplineU)

    Calculate the points of a closed uniform B-spline curve (`closed curve`_).


DBSpline
--------

.. class:: DBSpline(BSpline)

    Calculate points and derivative of a B-spline curve, using an uniform open `knot`_ vector (`clamped curve`_).

.. method:: DBSpline.point(t)

    Returns the B-spline vertex, 1. derivative and 2. derivative at position t as tuple (vertex, d1, d2), each value
    is a (x, y, z) tuple.

DBSplineU
---------

.. class:: DBSplineU(DBSpline)

    Calculate points and derivative of a B-spline curve, uniform (periodic) `knot`_ vector (`open curve`_).

DBSplineClosed
--------------

.. class:: DBSplineClosed(DBSplineU)

    Calculate the points and derivative of a closed uniform B-spline curve (`closed curve`_).


.. _Curve Global Interpolation: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/CURVE-INT-global.html
.. _uniform: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-uniform.html
.. _chord length: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-chord-length.html
.. _centripetal: https://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-centripetal.html
.. _knot: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/INT-APP/PARA-knot-generation.html
.. _clamped curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve.html
.. _open curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-open.html
.. _closed curve: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-curve-closed.html
.. _basis: http://pages.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/B-spline/bspline-basis.html
