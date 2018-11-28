LWPolyline
==========

.. class:: LWPolyline(GraphicEntity)

    Introduced in DXF version R13 (AC1012), dxftype is LWPOLYLINE.

    A lightweight polyline is defined as a single graphic entity. The :class:`LWPolyline` differs from the old-style
    :class:`Polyline`, which is defined as a group of subentities. :class:`LWPolyline` display faster (in AutoCAD) and
    consume less disk space and RAM. Create :class:`LWPolyline` in layouts and blocks by factory function
    :meth:`~Layout.add_lwpolyline`. :class:`LWPolyline` is a planar element, therefore all points in :ref:`OCS` as (x, y)
    tuples (:attr:`~LWPolyline.dxf.elevation` is the z-axis value).

    Since *ezdxf* v0.8.9 :class:`LWPolyline` stores point data as packed data (:code:`array.array()`).

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


.. _format codes:

User Defined Point Format Codes
-------------------------------


    ==== ================
    Code Point Component
    ==== ================
       x x coordinate
       y y coordinate
       s start width
       e end width
       b bulge value
       v (x, y) as tuple
    ==== ================


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

    number of vertices (read only), same as :code:`len(polyline)`


LWPolyline Attributes
---------------------


.. attribute:: LWPolyline.closed

    *True* if polyline is closed else *False*. A closed polyline has a connection from the last vertex
    to the first vertex. (read/write)


LWPolyline Methods
------------------

.. method:: LWPolyline.get_points(format='xyseb')

    :param format: format string, see `format codes`_

    Returns all polyline points as list of tuples (x, y, start_width, end_width, bulge), format specifies a user defined
    point format.

    start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present).

    All points in :ref:`OCS` as (x, y) tuples (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.set_points(points, format='xyseb')

    :param format: format string, see `format codes`_

    Replace existing polyline points by new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
    tuples. Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

    All points in :ref:`OCS` as (x, y) tuples (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.points(format='xyseb')

    :param format: format string, see `format codes`_

    Context manager for polyline points. Returns a standard Python list of points, according to the format string.

    All coordinates in :ref:`OCS`.

.. method:: LWPolyline.vertices()

    Yield all polyline points as (x, y) tuples in :ref:`OCS` (:attr:`~LWpolyline.dxf.elevation` is the z-axis value).

.. method:: LWPolyline.vertices_in_wcs()

    Yield all polyline points as (x, y, z) tuples in :ref:`WCS`.

.. method:: LWPolyline.append(point, format='xyseb')

    :param format: format string, see `format codes`_

    Append new point, format specifies a user defined point format.

    All coordinates in :ref:`OCS`.

.. method:: LWPolyline.append_points(points, format='xyseb')

    :param points: iterable of point, point is (x, y, [start_width, [end_width, [bulge]]]) tuple
    :param format: format string, see `format codes`_

    Append new points, points is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
    Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

    All coordinates in :ref:`OCS`.

.. method:: LWPolyline.insert(pos, point, format='xyseb')

    :param pos: insertion position for new point
    :param point: new polyline point
    :param format: format string, see `format codes`_

    Insert new point in front of position *pos*, format specifies a user defined point format.

    All coordinates in :ref:`OCS`.

.. method:: LWPolyline.clear()

    Remove all points.

.. method:: LWPolyline.__len__()

    Number of polyline points.

.. method:: LWPolyline.__getitem__(index)

    Get point at position *index* as (x, y, start_width, end_width, bulge) tuple. start_width, end_width and bulge is
    0 if not present (0 is the DXF default value if not present), supports extended slicing. Point format is fixed as
    'xyseb'.

    All coordinates in :ref:`OCS`.

.. method:: LWPolyline.__setitem__(index, value)

    Set point at position *index* as (x, y, [start_width, [end_width, [bulge]]]) tuple. If start_width or end_width is 0 or
    left off the default value is used. If the bulge value is left off, bulge is 0 by default (straight line). Does NOT
    support extend slicing. Point format is fixed as 'xyseb'.

    All coordinates in :ref:`OCS`.

.. method:: LWPolyline.__delitem__(index)

    Delete point at position *index*, supports extended slicing.
