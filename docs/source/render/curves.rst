.. module:: ezdxf.render
    :noindex:

Spline
======

.. autoclass:: Spline

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

.. autoclass:: R12Spline

    .. automethod:: __init__

    .. automethod:: render

    .. automethod:: approximate


Bezier
======

.. autoclass:: Bezier

    .. automethod:: start

    .. automethod:: append

    .. automethod:: render

EulerSpiral
===========

.. autoclass:: EulerSpiral

    .. automethod:: __init__

    .. automethod:: render_polyline

    .. automethod:: render_spline


Random Paths
============

Random path generators for testing purpose.

.. autofunction:: random_2d_path(steps=100, max_step_size=1, max_heading=pi/2, retarget=20) -> Iterable[Vec2]

.. autofunction:: random_3d_path(steps=100, max_step_size=1, max_heading=pi/2, max_pitch=pi/8, retarget=20) -> Iterable[Vec3]
