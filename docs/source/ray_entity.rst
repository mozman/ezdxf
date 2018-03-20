Ray
===

.. class:: Ray(GraphicEntity)

Introduced in DXF version R13 (AC1012), dxftype is RAY.

A :class:`Ray` starts at a point and continues to infinity. Create :class:`Ray` in layouts and blocks by factory
function :meth:`~Layout.add_ray`.

DXF Attributes for Ray
----------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Ray.dxf.start

Start point as (3D Point)

.. attribute:: Ray.dxf.unit_vector

Unit direction vector as (3D Point)

