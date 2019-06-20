Trace
=====

.. class:: Trace(GraphicEntity)

A Trace is solid filled triangle or quadrilateral, dxftype is TRACE. Access corner points by name
(:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`). I don't know the difference
between SOLID and TRACE.
Create traces in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_trace`.

DXF Attributes for Trace
------------------------

:ref:`Common graphical DXF attributes`


.. attribute:: Trace.dxf.vtx0

location of the 1. point (2D/3D Point in :ref:`OCS`)

.. attribute:: Trace.dxf.vtx1

location of the 2. point (2D/3D Point in :ref:`OCS`)

.. attribute:: Trace.dxf.vtx2

location of the 3. point (2D/3D Point in :ref:`OCS`)

.. attribute:: Trace.dxf.vtx3

location of the 4. point (2D/3D Point in :ref:`OCS`)

