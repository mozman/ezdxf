Ellipse
=======

.. class:: Ellipse(GraphicEntity)

Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ELLIPSE.

An ellipse with center point at location *center* and a major axis *major_axis* as vector. *ratio* is the ratio of
minor axis to major axis. *start_param* and *end_param* defines start and end point of the ellipse, a full ellipse
goes from 0 to 2*pi. The ellipse goes from start to end param in *counter clockwise* direction. Create ellipses in
layouts and blocks by factory function :meth:`~Layout.add_ellipse`.

:attr:`Ellipse.dxf.extrusion` is supported, but does not establish an :ref:`OCS`, it is used to create an 3D entity by
extruding the base ellipse.

DXF Attributes for Ellipse
--------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Ellipse.dxf.center

center point of circle (2D/3D Point in :ref:`WCS`)

.. attribute:: Ellipse.dxf.major_axis

Endpoint of major axis, relative to the center (tuple of float)

.. attribute:: Ellipse.dxf.ratio

Ratio of minor axis to major axis (float)

.. attribute:: Ellipse.dxf.start_param

Start parameter (this value is 0.0 for a full ellipse) (float)

.. attribute:: Ellipse.dxf.end_param

End parameter (this value is 2*pi for a full ellipse) (float)

