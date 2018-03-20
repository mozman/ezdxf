LWPolyline
==========

.. class:: LWPolyline(GraphicEntity)

Introduced in DXF version R13 (AC1012), dxftype is LWPOLYLINE.

A lightweight polyline is defined as a single graphic entity. The :class:`LWPolyline` differs from the old-style
:class:`Polyline`, which is defined as a group of subentities. :class:`LWPolyline` display faster (in AutoCAD) and
consume less disk space and RAM. Create :class:`LWPolyline` in layouts and blocks by factory function
:meth:`~Layout.add_lwpolyline`. LWPolylines are planar elements, therefore all coordinates have no value for the
z axis.

.. seealso::

    :ref:`tut_lwpolyline`

DXF Attributes for LWPolyline
-----------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: LWPolyline.dxf.elevation

z-axis value in WCS is the polyline elevation (float), default=0

.. attribute:: LWPolyline.dxf.flags

Constants defined in :mod:`ezdxf.const`:

============================== ======= ===========
LWPolyline.dxf.flags           Value   Description
============================== ======= ===========
LWPOLYLINE_CLOSED              1       polyline is closed
LWPOLYLINE_PLINEGEN            128     ???
============================== ======= ===========

.. attribute:: LWPolyline.dxf.const_width

constant line width (float), default=0

.. attribute:: LWPolyline.dxf.count

number of vertices


LWPolyline Attributes
---------------------


.. attribute:: LWPolyline.closed

*True* if polyline is closed else *False*.  A closed polyline has a connection from the last vertex
to the first vertex. (read/write)

LWPolyline Methods
------------------

.. method:: LWPolyline.get_points()

Returns all polyline points as list of tuples (x, y, start_width, end_width, bulge).

start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present).

.. method:: LWPolyline.get_rstrip_points()

Generates points without appending zeros: yields (x1, y1), (x2, y2) instead of (x1, y1, 0, 0, 0), (x2, y2, 0, 0, 0).

.. method:: LWPolyline.set_points(points)

Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

.. method:: LWPolyline.points()

Context manager for polyline points. Returns a list of tuples (x, y, start_width, end_width, bulge)

start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present). Setting/Appending
points accepts (x, y, [start_width, [end_width, [bulge]]]) tuples. Set start_width, end_width to 0 to be ignored
(x, y, 0, 0, bulge).

.. method:: LWPolyline.rstrip_points()

Context manager for polyline points without appending zeros.

.. method:: LWPolyline.append_points(points)

Append additional *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

.. method:: LWPolyline.discard_points()

Remove all points.

.. method:: LWPolyline.__len__()

Number of polyline vertices.

.. method:: LWPolyline.__getitem__(index)

Get point at position *index* as (x, y, start_width, end_width, bulge) tuple. Actual implementation is very slow!
start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present).
