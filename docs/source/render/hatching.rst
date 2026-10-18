
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

Bounded Rendering
-----------------

High-level hatching and pattern rendering use a :class:`HatchingControl` with
defaults of 1,000,000 work items and 1,000,000 output segments. Work includes
boundary elements, attempted intersections, storing and processing intersections,
and dash elements, including gaps. Internal hatch distances are generated lazily.
The public :func:`hatch_line_distances` helper continues to return a list.

Pass the same ``control`` to multiple calls to share these limits and a
``terminate`` callback. Cancellation is checked inside intersection and dash loops
at least every 64 work items. It stops iteration; exhausting a budget raises
:class:`HatchingLimitError`. Completed lines may already have been yielded. Set a
limit to ``None`` to explicitly opt out of that limit.

These limits bound core loop work, not a strict whole-entity elapsed time:
boundary-to-path conversion precedes the frontend timer, and sorting an
intersection group is an indivisible operation.

The drawing frontend exposes these limits as ``Configuration.hatching_max_work``
and ``Configuration.hatching_max_segments``. It retains completed lines and
reports an aborted hatch when either limit is reached. The default preserves a
single backend stroke operation, including its transparency blending; the output
buffer is bounded by the segment limit.

Existing minimum-line-distance fallback policies are unchanged.

Classes
-------

.. autoclass:: HatchingControl

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

.. autoclass:: HatchingLimitError
