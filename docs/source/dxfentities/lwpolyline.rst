LWPolyline
==========

.. class:: LWPolyline(GraphicEntity)

    Introduced in DXF version R13 (AC1012), dxftype is LWPOLYLINE.

    A lightweight polyline is defined as a single graphic entity. The :class:`LWPolyline` differs from the old-style
    :class:`Polyline`, which is defined as a group of subentities. :class:`LWPolyline` display faster (in AutoCAD) and
    consume less disk space and RAM. Create :class:`LWPolyline` in layouts and blocks by factory function
    :meth:`~Layout.add_lwpolyline`. :class:`LWPolyline` is a planar element, therefore all points in :ref:`OCS` as (x, y)
    tuples (:attr:`~LWPolyline.dxf.elevation` is the z-axis value).

Bulge Value
-----------

    The bulge value is used to create arc shaped line segments. The bulge defines the ratio of the arc sagitta (versine)
    to half line segment length, a bulge value of 1 defines a semicircle.

    The sign of the bulge value defines the side of the bulge:

    - positive value (> 0): bulge is right of line (count clockwise)
    - negative value (< 0): bulge is left of line (clockwise)
    - 0 = no bulge

Start Width And End Width
-------------------------

    The start width and end width values defines the width in drawing units for the following line segment.
    To use the default width value for a line segment set value to 0.

Width and Bulge Values at Last Point
------------------------------------

    The width and bulge values of the last vertex has only a meaning if the polyline is closed, and they apply
    to the last line segment from the last vertex to the first vertex.

.. seealso::

    :ref:`tut_lwpolyline`


DXF Attributes for LWPolyline
-----------------------------

    :ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: LWPolyline.dxf.elevation

    :ref:`OCS` z-axis value for all polyline points, default=0

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

.. attribute:: LWPolyline.lwpoints

    Returns :class:`LWPolylinePoints` object.

LWPolyline Methods
------------------

.. method:: LWPolyline.get_points()

    Returns all polyline points as list of tuples (x, y, start_width, end_width, bulge) (deprecated). New way is to use
    :attr:`LWPolyline.lwpoints` or use the context manager :meth:`LWPolyline.points`.

    start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present).

    All points in :ref:`OCS` as (x, y) tuples (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.get_rstrip_points()

    Generates points without appending zeros: yields (x1, y1), (x2, y2) instead of (x1, y1, 0, 0, 0), (x2, y2, 0, 0, 0).

.. method:: LWPolyline.set_points(points)

    Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
    Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

    All points in :ref:`OCS` as (x, y) tuples (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.points()

    Context manager for polyline points. Returns a list of tuples (x, y, start_width, end_width, bulge)

    start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present). Setting/Appending
    points accepts (x, y, [start_width, [end_width, [bulge]]]) tuples. Set start_width, end_width to 0 to be ignored
    (x, y, 0, 0, bulge).

    All points in :ref:`OCS` as (x, y) tuples (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.vertices()

    Yield all polyline points as (x, y) tuples in :ref:`OCS` (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.vertices_in_wcs()

    Yield all polyline points as (x, y, z) tuples in :ref:`WCS`.

.. method:: LWPolyline.rstrip_points()

    Context manager for polyline points without appending zeros.

.. method:: LWPolyline.append_points(points)

    Append additional *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
    Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

    All points in :ref:`OCS` as (x, y) tuples (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.clear()

    Remove all points.

.. method:: LWPolyline.__len__()

    Number of polyline vertices.

.. method:: LWPolyline.__getitem__(index)

    Get point at position *index* as (x, y, start_width, end_width, bulge) tuple. start_width, end_width and bulge is 0 if
    not present (0 is the DXF default value if not present), supports extended slicing.

.. method:: LWPolyline.__setitem__(index, value)

    Set point at position *index* as (x, y, [start_width, [end_width, [bulge]]]) tuple. If start_width or end_width is 0 or
    left off the default value is used. If the bulge value is left off, bulge is 0 by default (straight line). Does NOT
    support extend slicing.

.. method:: LWPolyline.__delitem__(index)

    Delete point at position *index*, supports extended slicing.

LWPolylinePoints
----------------

    A list like object to store :class:`LWPolyline` vertices, start width, end width and bulge values in
    a :code:`array.array('d')` flat list.

    Supports most standard list operations like indexing, iteration, insert, append, extend and so on.

.. class:: LWPolylinePoints(VertexArray)

    For attributes and methods see :class:`~ezdxf.lldxf.VertexArray`
