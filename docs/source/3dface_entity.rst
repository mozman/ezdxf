3DFace
======

.. class:: 3DFace(GraphicEntity)

(This is not a valid Python name, but it works, because all classes
described here, do not exist in this simple form.)

A 3DFace is real 3D solid filled triangle or quadrilateral, dxftype is 3DFACE. Access corner points by name
(:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
Create 3DFaces in layouts and blocks by factory function :meth:`~Layout.add_3dface`.

DXF Attributes for 3DFace
-------------------------

:ref:`Common DXF attributes for DXF R12`

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: 3DFace.dxf.vtx0

location of the 1. point (3D Point in :ref:`WCS`)

.. attribute:: 3DFace.dxf.vtx1

location of the 2. point (3D Point in :ref:`WCS`)

.. attribute:: 3DFace.dxf.vtx2

location of the 3. point (3D Point in :ref:`WCS`)

.. attribute:: 3DFace.dxf.vtx3

location of the 4. point (3D Point in :ref:`WCS`)

.. attribute:: 3DFace.dxf.invisible_edge

invisible edge flag (int, default=0)

- 1 = first edge is invisible
- 2 = second edge is invisible
- 4 = third edge is invisible
- 8 = fourth edge is invisible

Combine values by adding them, e.g. 1+4 = first and third edge is invisible.

