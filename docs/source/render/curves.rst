.. module:: ezdxf.render
    :noindex:

Spline
======

Render a B-spline as 2D/3D :class:`~ezdxf.entities.Polyline`, can be used with DXF R12. The advantage over
:class:`R12Spline` is the real 3D support which means the B-spline curve vertices has not to be in a
plane and no hassle with :ref:`UCS` for 3D placing.

.. class:: Spline

    .. automethod:: __init__

    .. automethod:: subdivide

    .. automethod:: render_as_fit_points

    .. automethod:: render_open_bspline

    .. automethod:: render_uniform_bspline

    .. automethod:: render_closed_bspline

    .. automethod:: render_open_rbspline

    .. automethod:: render_uniform_rbspline

    .. automethod:: render_closed_rbspline


R12Spline
=========

DXF R12 supports 2D B-splines, but Autodesk do not document the usage in the DXF Reference. The base entity for splines
in DXF R12 is the POLYLINE entity. The spline itself is always in a plane, but as any 2D entity, the spline can be
transformed into the 3D object by elevation and extrusion (:ref:`OCS`, :ref:`UCS`).

The result is not better than :class:`Spline`, it is also just a POLYLINE entity, but as with all tools, you never
know if someone needs it some day.

.. class:: R12Spline

    .. automethod:: __init__

    .. automethod:: render

    .. automethod:: approximate


Bezier
======

Render a bezier curve as 2D/3D :class:`~ezdxf.entities.Polyline`.

The :class:`Bezier` class is implemented with multiple segments, each segment is an optimized 4 point bezier curve, the
4 control points of the curve are: the start point (1) and the end point (4), point (2) is start point + start vector
and point (3) is end point + end vector. Each segment has its own approximation count.

.. class:: Bezier

    .. automethod:: start

    .. automethod:: append

    .. automethod:: render

EulerSpiral
===========

Render an `euler spiral <https://en.wikipedia.org/wiki/Euler_spiral>`_ as 3D :class:`Polyline` or :class:`Spline`.

This is a parametric curve, which always starts at the origin ``(0, 0)``.

.. class:: EulerSpiral

    .. automethod:: __init__

    .. automethod:: render_polyline

    .. automethod:: render_spline


Random Paths
============

Random path generators for testing purpose.

.. autofunction:: random_2d_path(steps=100, max_step_size=1, max_heading=pi/2, retarget=20) -> Iterable[Vec2]

.. autofunction:: random_3d_path(steps=100, max_step_size=1, max_heading=pi/2, max_pitch=pi/8, retarget=20) -> Iterable[Vector]
