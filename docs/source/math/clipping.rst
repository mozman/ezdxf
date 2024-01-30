
.. module:: ezdxf.math.clipping

.. _math_clipping:

Clipping
========

Clipping module: :mod:`ezdxf.math.clipping`

.. autofunction:: greiner_hormann_union

.. autofunction:: greiner_hormann_difference

.. autofunction:: greiner_hormann_intersection

.. autoclass:: ConvexClippingPolygon2d

    .. automethod:: clip_polygon

    .. automethod:: clip_polyline

    .. automethod:: clip_line

    .. automethod:: is_inside

.. autoclass:: ClippingRect2d

    .. automethod:: clip_polygon

    .. automethod:: clip_polyline

    .. automethod:: clip_line

    .. automethod:: is_inside
