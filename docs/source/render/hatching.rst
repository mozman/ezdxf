
Hatching
========

.. module:: ezdxf.render.hatching

This module provides rendering support for hatch patterns as used in
:class:`~ezdxf.entities.Hatch` and :class:`~ezdxf.entities.MPolygon` entities.

High Level Functions
--------------------

.. autofunction:: hatch_entity

.. autofunction:: hatch_polygons

.. autofunction:: hatch_paths

Classes
-------

.. autoclass:: HatchBaseLine

    .. automethod:: hatch_line

    .. automethod:: pattern_renderer

    .. automethod:: signed_distance


.. autoclass:: HatchLine

    .. automethod:: intersect_line

    .. automethod:: intersect_cubic_bezier_curve


.. autoclass:: PatternRenderer

    .. automethod:: render


.. autoclass:: Intersection

    .. attribute:: type

        intersection type as :class:`IntersectionType` instance

    .. attribute:: p0

        (first) intersection point as :class:`~ezdxf.math.Vec2` instance

    .. attribute:: p1

        second intersection point as :class:`~ezdxf.math.Vec2` instance, only if
        :attr:`type` is COLLINEAR

.. autoclass:: IntersectionType

    .. attribute:: NONE

        no intersection

    .. attribute:: REGULAR

        regular intersection point at a polygon edge or a Bèzier curve

    .. attribute:: START

        intersection point at the start vertex of a polygon edge

    .. attribute:: END

        intersection point at the end vertex of a polygon edge

    .. attribute:: COLLINEAR

        intersection is collinear to a polygon edge

.. autoclass:: Line

    .. attribute:: start

        start point as :class:`~ezdxf.math.Vec2` instance

    .. attribute:: end

        end point as :class:`~ezdxf.math.Vec2` instance


    .. attribute:: distance

        signed normal distance to the :class:`HatchBaseLine`


Helper Functions
----------------

.. autofunction:: hatch_boundary_paths

.. autofunction:: hatch_line_distances

.. autofunction:: pattern_baselines

Exceptions
----------

.. autoclass:: HatchingError

.. autoclass:: HatchLineDirectionError

.. autoclass:: DenseHatchingLinesError