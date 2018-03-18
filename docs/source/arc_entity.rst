Arc
===

.. class:: Arc(GraphicEntity)

An arc at location *center* and *radius* from *start_angle* to *end_angle*, *dxftype* is ARC. The arc goes from
*start_angle* to *end_angle* in *counter clockwise* direction. Create arcs in layouts and blocks by factory function
:meth:`~Layout.add_arc`.

DXF Attributes for Arc
----------------------

.. attribute:: Arc.dxf.center

center point of arc (2D/3D Point)

.. attribute:: Arc.dxf.radius

radius of arc (float)

.. attribute:: Arc.dxf.start_angle

start angle in degrees (float)

.. attribute:: Arc.dxf.end_angle

end angle in degrees (float)
