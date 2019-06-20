Solid
=====

.. class:: Solid(GraphicEntity)

A solid filled triangle or quadrilateral, dxftype is SOLID. Access corner points by name
(:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
Create solids in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_solid`.

DXF Attributes for Solid
------------------------

:ref:`Common graphical DXF attributes`


.. attribute:: Solid.dxf.vtx0

location of the 1. point (2D/3D Point in :ref:`OCS`)

.. attribute:: Solid.dxf.vtx1

location of the 2. point (2D/3D Point in :ref:`OCS`)

.. attribute:: Solid.dxf.vtx2

location of the 3. point (2D/3D Point in :ref:`OCS`)

.. attribute:: Solid.dxf.vtx3

location of the 4. point (2D/3D Point in :ref:`OCS`)
