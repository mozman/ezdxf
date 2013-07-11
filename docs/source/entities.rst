Common Base Class
=================

.. class:: GraphicsEntity

   Common base class for all graphic entities.

.. attribute:: dxf

   (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
   :code:`object.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
   writeable.

.. attribute:: dxftype

   (read only) Get the DXF type string, like ``'LINE'`` for the line entity.

.. attribute:: handle

   (read only) Get the entity handle. (feature for experts)

.. _Common DXF attributes for DXF R12:

Common DXF attributes for DXF R12
=================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

=========== =================================================================
DXFAttr     Description
=========== =================================================================
handle      DXF handle (feature for experts)
layer       layername as string, default is ``'0'``
linetype    linetype as string, special names ``'BYLAYER'``, ``'BYBLOCK'``,
            default is ``'BYLAYER'``
color       dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER, default is 256
paperspace  0 = entity resides in model-space, 1 = in paper-space
            (feature for experts)
extrusion   extrusion direction as 3D point
=========== =================================================================

.. _Common DXF attributes for DXF R13 or later:

Common DXF attributes for DXF R13 or later
==========================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

============= =================================================================
DXFAttr       Description
============= =================================================================
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
============= =================================================================


Line
====

.. class:: Line(GraphicEntity)

   A line form *start* to *end*, *dxftype* is ``'LINE'``.
   Create lines in layouts and blocks by factory function :meth:`~Layout.add_line`.

=========== ======= =============================================================
DXFAttr     Version Description
=========== ======= =============================================================
start       R12     start point of line (2D/3D Point)
end         R12     end point of line (2D/3D Point)
=========== ======= =============================================================

Point
=====

.. class:: Point(GraphicEntity)

   A point at location *point*, *dxftype* is ``'POINT'``.
   No factory function for creating points until someone need it.

=========== ======= =============================================================
DXFAttr     Version Description
=========== ======= =============================================================
point       R12     location of the point (2D/3D Point)
=========== ======= =============================================================

Circle
======

.. class:: Circle

Arc
===

.. class:: Arc

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

Trace
=====

.. class:: Trace

3DFace
======

.. class:: 3DFace

    (This is not a valid Python name, but it works, because all classes
    described here, do not exist in this simple form.)
