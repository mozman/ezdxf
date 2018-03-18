Shape
=====

.. class:: Shape(GraphicEntity)

Shapes (dxftype is SHAPE) are objects that you use like blocks. Shapes are stored in external shape files
(\*.SHX). You can specify the scale and rotation for each shape reference as you add it. You can not create shapes
with *ezdxf*, you can just insert shape references.

Create a :class:`Shape` reference in layouts and blocks by factory function :meth:`~Layout.add_shape`.

DXF Attributes for Shape
------------------------

.. attribute:: Shape.dxf.insert

Insertion point as (2D/3D Point)

.. attribute:: Shape.dxf.name

Shape name

.. attribute:: Shape.dxf.size

Shape size

.. attribute:: Shape.dxf.rotation

Rotation angle in degrees; default=0

.. attribute:: Shape.dxf.xscale

Relative X scale factor; default=1

.. attribute:: Shape.dxf.oblique

Oblique angle; default=0

