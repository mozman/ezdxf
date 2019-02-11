Circle
======

.. class:: Circle(GraphicEntity)

A circle at location *center* and *radius*, *dxftype* is CIRCLE.
Create circles in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_circle`.

DXF Attributes for Circle
-------------------------

:ref:`Common DXF attributes for DXF R12`

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Circle.dxf.center

center point of circle (2D/3D Point in :ref:`OCS`)

.. attribute:: Circle.dxf.radius

radius of circle (float)
