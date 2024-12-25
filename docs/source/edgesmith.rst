EdgeSmith
=========

.. module:: ezdxf.edgesmith

.. versionadded:: 1.4

Purpose of this Module
----------------------

This is a companion module to the :mod:`ezdxf.edgeminer` module:

    - create :class:`~ezdxf.edgeminer.Edge` instances from DXF primitives for processing
      by the :mod:`~ezdxf.edgeminer` module:

        - :class:`~ezdxf.entities.Line`
        - :class:`~ezdxf.entities.Arc`
        - :class:`~ezdxf.entities.Ellipse`
        - :class:`~ezdxf.entities.Spline`
        - :class:`~ezdxf.entities.LWPolyline`
        - :class:`~ezdxf.entities.Polyline`

    - create :class:`~ezdxf.entities.LWPolyline` and :class:`~ezdxf.entities.Polyline`
      entities from a sequence of :class:`~ezdxf.edgeminer.Edge` objects.
    - create :class:`~ezdxf.entities.Hatch` boundary paths from a sequence of
      :class:`~ezdxf.edgeminer.Edge` objects.
    - create :class:`ezdxf.path.Path` objects from a sequence of :class:`~ezdxf.edgeminer.Edge`
      objects.

.. seealso::

    - :ref:`tut_edges`
    - :mod:`ezdxf.edgeminer` module

.. important::

    This is the reference documentation and not a tutorial how to use this module.

Convert To Edges
----------------

This functions convert only open shapes into edges, closed shapes as circles, closed
arcs, closed ellipses, closed splines and closed polylines are ignored or return
``None``.

.. autofunction:: make_edge

.. autofunction:: edges_from_entities

Convert From Edges
------------------

.. autofunction:: lwpolyline_from_chain

.. autofunction:: polyline2d_from_chain

.. autofunction:: path_from_chain

.. autofunction:: edge_path_from_chain

.. autofunction:: polyline_path_from_chain