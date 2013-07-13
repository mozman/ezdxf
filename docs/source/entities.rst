Common Base Class
=================

.. class:: GraphicEntity

   Common base class for all graphic entities.

.. attribute:: dxf

   (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
   :code:`object.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
   writeable.

.. attribute:: dxftype

   (read only) Get the DXF type string, like ``'LINE'`` for the line entity.

.. attribute:: handle

   (read only) Get the entity handle. (feature for experts)

.. method:: get_dxf_attrib(key, default=ValueError)

   Get DXF attribute *key*, returns *default* if key doesn't exist, or raise :class:`ValueError` if *default* is
   :class:`ValueError`::

        layer = entity.get_dxf_attrib("layer")
        # same as
        layer = entity.dxf.layer

.. method:: set_dxf_attrib(key, value)

   Set DXF attribute *key* to *value*::

       entity.set_dxf_attrib("layer", "MyLayer")
       # same as
       entity.dxf.layer = "MyLayer"


.. _Common DXF attributes for DXF R12:

Common DXF attributes for DXF R12
=================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

=========== ===========
DXFAttr     Description
=========== ===========
handle      DXF handle (feature for experts)
layer       layername as string, default is ``'0'``
linetype    linetype as string, special names ``'BYLAYER'``, ``'BYBLOCK'``,
            default is ``'BYLAYER'``
color       dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER, default is 256
paperspace  0 = entity resides in model-space, 1 = in paper-space
            (feature for experts)
extrusion   extrusion direction as 3D point
=========== ===========

.. _Common DXF attributes for DXF R13 or later:

Common DXF attributes for DXF R13 or later
==========================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

============= ===========
DXFAttr       Description
============= ===========
handle        DXF handle (feature for experts)
block_record  handle to owner, it's a BLOCK_RECORD entry (feature for experts)
layer         layername as string, default is ``'0'``
linetype      linetype as string, special names ``'BYLAYER'``, ``'BYBLOCK'``,
              default is ``'BYLAYER'``
color         dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER, default is 256
ltscale       line type scale as float, defaults to 1.0
invisible     ``1`` for invisible, ``0`` for visible
paperspace    ``0`` for entity resides in model-space, ``1`` for paper-space
              (feature for experts)
extrusion     extrusion direction as 3D point
thickness     entity thickness as float
============= ===========


Line
====

.. class:: Line(GraphicEntity)

   A line form *start* to *end*, *dxftype* is ``'LINE'``.
   Create lines in layouts and blocks by factory function :meth:`~Layout.add_line`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
start       R12     start point of line (2D/3D Point)
end         R12     end point of line (2D/3D Point)
=========== ======= ===========

Point
=====

.. class:: Point(GraphicEntity)

   A point at location *point*, *dxftype* is ``'POINT'``.
   No factory function for creating points until someone need it.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
point       R12     location of the point (2D/3D Point)
=========== ======= ===========

Circle
======

.. class:: Circle

   A circle at location *center* and *radius*, *dxftype* is ``'CIRCLE'``.
   Create circles in layouts and blocks by factory function :meth:`~Layout.add_circle`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
center      R12     center point of circle (2D/3D Point)
radius      R12     radius of circle (float)
=========== ======= ===========

Arc
===

.. class:: Arc

   An arc at location *center* and *radius* from *startangle* to *endangle*, *dxftype* is ``'ARC'``.
   Create arcs in layouts and blocks by factory function :meth:`~Layout.add_arc`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
center      R12     center point of arc (2D/3D Point)
radius      R12     radius of arc (float)
startangle  R12     start angle in degrees (float)
endangle    R12     end angle in degrees (float)
=========== ======= ===========

Text
====

.. class:: Text

Polyline
========

.. class:: Polyline

Polymesh
========

.. class:: Polymesh

Polyface
========

.. class:: Polyface

Solid
=====

.. class:: Solid

   A solid filled triangle or quadrilateral, *dxftype* is ``'SOLID'``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
   Create solids in layouts and blocks by factory function :meth:`~Layout.add_solid`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
vtx0        R12     location of the 1. point (2D/3D Point)
vtx1        R12     location of the 2. point (2D/3D Point)
vtx2        R12     location of the 3. point (2D/3D Point)
vtx3        R12     location of the 4. point (2D/3D Point)
=========== ======= ===========

Trace
=====

.. class:: Trace

   A Trace is solid filled triangle or quadrilateral, *dxftype* is ``'TRACE'``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`). I don't know the difference
   between SOLID and TRACE.
   Create traces in layouts and blocks by factory function :meth:`~Layout.add_trace`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
vtx0        R12     location of the 1. point (2D/3D Point)
vtx1        R12     location of the 2. point (2D/3D Point)
vtx2        R12     location of the 3. point (2D/3D Point)
vtx3        R12     location of the 4. point (2D/3D Point)
=========== ======= ===========

3DFace
======

.. class:: 3DFace

   (This is not a valid Python name, but it works, because all classes
   described here, do not exist in this simple form.)

   A 3DFace is real 3D solid filled triangle or quadrilateral, *dxftype* is ``'3DFACE'``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
   Create 3DFaces in layouts and blocks by factory function :meth:`~Layout.add_3Dface`.

============== ======= ===========
DXFAttr        Version Description
============== ======= ===========
vtx0           R12     location of the 1. point (2D/3D Point)
vtx1           R12     location of the 2. point (2D/3D Point)
vtx2           R12     location of the 3. point (2D/3D Point)
vtx3           R12     location of the 4. point (2D/3D Point)
invisible_edge R12     invisible edge flag (int, default = 0)

                       - 1 = first edge is invisible
                       - 2 = second edge is invisible
                       - 4 = third edge is invisible
                       - 8 = fourth edge is invisible

                       Combine values by adding them, e.g. 1+4 = first and third edge is invisible.
============== ======= ===========
