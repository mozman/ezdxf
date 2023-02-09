.. module:: ezdxf.path

Path
====

This module implements a geometric :class:`Path`, supported by several render
backends, with the goal to create such paths from DXF entities like LWPOLYLINE,
POLYLINE or HATCH and send them to the render backend,
see :mod:`ezdxf.addons.drawing`.

Minimum common interface:

- matplotlib: `PathPatch`_
    - matplotlib.path.Path() codes:
    - MOVETO
    - LINETO
    - CURVE3 - quadratic Bèzier-curve
    - CURVE4 - cubic Bèzier-curve

- PyQt: `QPainterPath`_
    - moveTo()
    - lineTo()
    - quadTo() - quadratic Bèzier-curve (converted to a cubic Bèzier-curve)
    - cubicTo() - cubic Bèzier-curve

- PyCairo: `Context`_
    - move_to()
    - line_to()
    - no support for quadratic Bèzier-curve
    - curve_to() - cubic Bèzier-curve

- SVG: `SVG-Path`_
    - "M" - absolute move to
    - "L" - absolute line to
    - "Q" - absolute quadratic Bèzier-curve
    - "C" - absolute cubic Bèzier-curve

ARC and ELLIPSE entities are approximated by multiple cubic Bézier-curves, which
are close enough for display rendering. Non-rational SPLINES of 3rd degree can
be represented exact as multiple cubic Bézier-curves, other B-splines will be
approximated. The XLINE and the RAY entities are not supported, because of their
infinite nature.

This :class:`Path` class is a full featured 3D object, although the backends
only support 2D paths.

.. hint::

    A :class:`Path` can not represent a point. A :class:`Path` with only a
    start point yields no vertices!


The usability of the :class:`Path` class expanded by the introduction
of the reverse conversion from :class:`Path` to DXF entities (LWPOLYLINE,
POLYLINE, LINE), and many other tools in `ezdxf` v0.16.
To emphasize this new usability, the :class:`Path` class has got its own
subpackage :mod:`ezdxf.path`.

.. glossary::

    Empty-Path
        Contains only a start point, the length of the path is 0 and the methods
        :meth:`Path.approximate`, :meth:`Path.flattening` and
        :meth:`Path.control_vertices` do not yield any vertices.

    Single-Path
        The :class:`Path` object contains only one path without gaps, the property
        :attr:`Path.has_sub_paths` is ``False`` and the method
        :meth:`Path.sub_paths` yields only this one path.

    Multi-Path
        The :class:`Path` object contains more than one path, the property
        :attr:`Path.has_sub_paths` is ``True`` and the method
        :meth:`Path.sub_paths` yields all paths within this object as single-path
        objects. It is not possible to detect the orientation of a multi-path
        object, therefore the methods :meth:`Path.has_clockwise_orientation`,
        :meth:`Path.clockwise` and :meth:`Path.counter_clockwise` raise a
        :class:`TypeError` exception.

.. warning::

    Always import from the top level :mod:`ezdxf.path`, never from the
    sub-modules

Factory Functions
-----------------

Functions to create :class:`Path` objects from other objects.

.. function:: make_path(entity: DXFEntity) -> Path

    Factory function to create a single :class:`Path` object from a DXF
    entity. Supported DXF types:

    - LINE
    - CIRCLE
    - ARC
    - ELLIPSE
    - SPLINE and HELIX
    - LWPOLYLINE
    - 2D and 3D POLYLINE
    - SOLID, TRACE, 3DFACE
    - IMAGE, WIPEOUT clipping path
    - VIEWPORT clipping path
    - HATCH as :term:`Multi-Path` object

    :param entity: DXF entity
    :param segments: minimal count of cubic Bézier-curves for elliptical arcs
        like CIRCLE, ARC, ELLIPSE, BULGE see :meth:`Path.add_ellipse`
    :param level: subdivide level for SPLINE approximation,
        see :meth:`Path.add_spline`

    :raises TypeError: for unsupported DXF types


.. autofunction:: from_hatch

.. autofunction:: from_vertices

.. autofunction:: from_matplotlib_path

.. autofunction:: multi_path_from_matplotlib_path

.. autofunction:: from_qpainter_path

.. autofunction:: multi_path_from_qpainter_path

Render Functions
----------------

Functions to create DXF entities from paths and add them to the modelspace, a
paperspace layout or a block definition.

.. autofunction:: render_hatches

.. autofunction:: render_lines

.. autofunction:: render_lwpolylines

.. autofunction:: render_mpolygons

.. autofunction:: render_polylines2d

.. autofunction:: render_polylines3d

.. autofunction:: render_splines_and_polylines

Entity Maker
------------

Functions to create DXF entities from paths.

.. autofunction:: to_hatches

.. autofunction:: to_lines

.. autofunction:: to_lwpolylines

.. autofunction:: to_mpolygons

.. autofunction:: to_polylines2d

.. autofunction:: to_polylines3d

.. autofunction:: to_splines_and_polylines

Tool Maker
----------

Functions to create construction tools.

.. autofunction:: to_bsplines_and_vertices

.. autofunction:: to_matplotlib_path

.. autofunction:: to_qpainter_path


Utility Functions
-----------------

.. autofunction:: add_bezier3p

.. autofunction:: add_bezier4p

.. autofunction:: add_ellipse

.. autofunction:: add_spline

.. autofunction:: bbox

.. autofunction:: chamfer

.. autofunction:: chamfer2

.. autofunction:: fillet

.. autofunction:: fit_paths_into_box

.. autofunction:: have_close_control_vertices

.. autofunction:: lines_to_curve3

.. autofunction:: lines_to_curve4

.. autofunction:: polygonal_fillet

.. autofunction:: single_paths

.. autofunction:: to_multi_path

.. autofunction:: transform_paths

.. autofunction:: transform_paths_to_ocs

.. autofunction:: triangulate

Basic Shapes
------------

.. autofunction:: elliptic_transformation

.. autofunction:: gear

.. autofunction:: helix

.. autofunction:: ngon

.. autofunction:: rect

.. autofunction:: star

.. autofunction:: unit_circle

.. autofunction:: wedge

The :mod:`~ezdxf.addons.text2path` add-on provides additional functions to
create paths from text strings and DXF text entities.


The Path Class
--------------

.. class:: Path

    .. autoproperty:: end

    .. autoproperty:: has_curves

    .. autoproperty:: has_lines

    .. autoproperty:: has_sub_paths

    .. autoproperty:: is_closed

    .. autoproperty:: start

    .. autoproperty:: user_data

    .. automethod:: append_path

    .. automethod:: approximate

    .. automethod:: clockwise

    .. automethod:: clone

    .. automethod:: close

    .. automethod:: close_sub_path

    .. automethod:: control_vertices

    .. automethod:: counter_clockwise

    .. automethod:: curve3_to

    .. automethod:: curve4_to

    .. automethod:: extend_multi_path

    .. automethod:: flattening

    .. automethod:: has_clockwise_orientation

    .. automethod:: line_to

    .. automethod:: move_to

    .. automethod:: reversed

    .. automethod:: sub_paths

    .. automethod:: transform

.. _PathPatch: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.patches.PathPatch.html#matplotlib.patches.PathPatch
.. _QPainterPath: https://doc.qt.io/qt-5/qpainterpath.html
.. _SVG-Path: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
.. _Context: https://pycairo.readthedocs.io/en/latest/reference/context.html