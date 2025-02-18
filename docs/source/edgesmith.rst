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

Make Edges
----------

This functions convert open shapes into 2D edges, closed shapes as circles, closed
arcs, closed ellipses, closed splines and closed polylines are ignored or return
``None``.

.. function:: make_edge_2d(entity: DXFEntity, *, gap_tol=GAP_TOL) -> ezdxf.edgeminer.Edge | None

    Makes an :class:`~ezdxf.edgeminer.Edge` instance from the following DXF entity types:

    - :class:`~ezdxf.entities.Line` (length accurate)
    - :class:`~ezdxf.entities.Arc` (length accurate)
    - :class:`~ezdxf.entities.Ellipse` (length approximated)
    - :class:`~ezdxf.entities.Spline` (length approximated as straight lines between
      control points)
    - :class:`~ezdxf.entities.LWPolyline` (length of bulges as straight line from
      start- to end point)
    - :class:`~ezdxf.entities.Polyline` (length of bulges as straight line from
      start- to end point)

    The start- and end points of the edge is projected onto the xy-plane. Returns
    ``None`` if the entity has a closed shape or cannot be represented as an edge.

.. autofunction:: edges_from_entities_2d

Build From Edges
----------------

ARC, LWPOLYLINE, POLYLINE and ELLIPSE entities must have an extrusion vector
of (0, 0, 1) (WCS Z-Axis). Entities with an inverted extrusion vector (0, 0, -1) will be
treated as a 3D curve and approximated by a polyline projected onto the xy-plane.
The :mod:`ezdxf.upright` module can convert such inverted extrusion vectors to (0, 0, 1).

Curve Approximation
~~~~~~~~~~~~~~~~~~~

For some target entities curves have to be approximated by polylines.
This process is also called flattening and is controlled by the parameter
:attr:`max_sagitta`. (`Wikipedia <https://en.wikipedia.org/wiki/Sagitta_(geometry)>`_)

The :attr:`max_sagitta` argument defines the maximum distance from the center of the
curve segment to the center of the line segment between two approximation points to
determine if a segment should be subdivided. The default value is -1 and uses a 1/100
of the approximated length of the curve as :attr:`max_sagitta`.

.. image:: gfx/es-max-sagitta.png

The good choice for a :attr:`max_sagitta` depends on the output resolution and is maybe
not known at the time of processing the data. E.g. for a printer/plotter a
:attr:`max_sagitta` of around 1/300 inch (300 dpi) is maybe a good choice.
The convertion from output units to drawing units depends on the scale and is the task
of the package user.

All flattened curves will be projected onto the xy-plane of the :ref:`WCS`.

.. autofunction:: lwpolyline_from_chain

.. autofunction:: polyline2d_from_chain

.. autofunction:: edge_path_from_chain

.. autofunction:: polyline_path_from_chain

.. autofunction:: path2d_from_chain

Helper Functions
----------------

.. function:: is_closed_entity(entity: DXFEntity) -> bool

    Returns ``True`` if the given entity represents a closed loop.

    Tests the following DXF entities:

        - CIRCLE
        - ARC
        - ELLIPSE
        - SPLINE
        - LWPOLYLINE
        - POLYLINE
        - HATCH
        - SOLID
        - TRACE

    Returns ``False`` for all other DXF entities.

.. function:: is_pure_2d_entity(entity: DXFEntity) -> bool

    Returns ``True`` if the given entity represents a pure 2D entity in the
    xy-plane of the :ref:`WCS`.

    - All vertices must be in the xy-plane of the :ref:`WCS`.
    - Thickness must be 0.
    - The extrusion vector must be (0, 0, 1).
    - Entities with inverted extrusions vectors (0, 0, -1) are **not** pure 2D entities.
      The :mod:`ezdxf.upright` module can be used to revert inverted extrusion vectors
      back to (0, 0, 1).

    Tests the following DXF entities:

        - LINE
        - CIRCLE
        - ARC
        - ELLIPSE
        - SPLINE
        - LWPOLYLINE
        - POLYLINE
        - HATCH
        - SOLID
        - TRACE

    Returns ``False`` for all other DXF entities.

.. autofunction:: filter_edge_entities

.. autofunction:: filter_2d_entities

.. autofunction:: filter_open_edges

.. autofunction:: bounding_box_2d

.. autofunction:: loop_area

.. autofunction:: is_inside_polygon_2d

.. autofunction:: intersecting_edges_2d

.. class:: IntersectingEdge

    NamedTuple as return type of :func:`intersecting_edges_2d`.

    .. attribute:: edge

        Intersecting edge as :class:`~ezdxf.edgeminer.Edge`; alias for field 0.

    .. attribute:: distance

        Distance from intersection point to point `p1` as float; alias for field 1.


Global Constants
----------------

.. code-block:: Python

    GAP_TOL = 1e-9
    LEN_TOL = 1e-9  # length and distance
    DEG_TOL = 1e-9  # angles in degree
    RAD_TOL = 1e-7  # angles in radians
