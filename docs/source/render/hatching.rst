
Hatching
========

.. module:: ezdxf.render.hatching

.. versionadded:: 0.18.1

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

.. autoclass:: HatchLine

.. autoclass:: PatternRenderer

Helper Functions
----------------

.. autofunction:: hatch_boundary_paths

.. autofunction:: pattern_baselines

Exceptions
----------

.. autoclass:: HatchingError

.. autoclass:: HatchLineDirectionError

.. autoclass:: DenseHatchingLinesError