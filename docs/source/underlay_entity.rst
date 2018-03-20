Underlay
========

.. class:: Underlay(GraphicEntity)

Introduced in DXF version R13 (AC1012), dxftype is PDFUNDERLAY, DWFUNDERLAY or DGNUNDERLAY.

Add an underlay file to the DXF file, the file itself is not embedded into the DXF file, it is always a separated file.
The (PDF)UNDERLAY entity is like a block reference, you can use it multiple times to add the underlay on different
locations with different scales and rotations. But therefore you need a also a (PDF)DEFINITION entity, see
:class:`UnderlayDefinition`.
Create :class:`Underlay` in layouts and blocks by factory function :meth:`~Layout.add_underlay`. The DXF standard
supports three different fileformats: PDF, DWF (DWFx) and DGN. An Underlay can be clipped by a rectangle or a
polygon path. The clipping coordinates are 2D OCS/ECS coordinates and in drawing units but without scaling.


DXF Attributes for Underlay
---------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: underlay.dxf.insert

Insertion point, lower left corner of the image

.. attribute:: underlay.dxf.scale_x

scaling factor in x direction (float)

.. attribute:: underlay.dxf.scale_y

scaling factor in y direction (float)

.. attribute:: underlay.dxf.scale_z

scaling factor in z direction (float)

.. attribute:: underlay.dxf.rotation

ccw rotation in degrees around the extrusion vector (float)

.. attribute:: underlay.dxf.extrusion

extrusion vector (default=0, 0, 1)

.. attribute:: underlay.dxf.underlay_def

Handle to the underlay definition entity, see :class:`UnderlayDefinition`

.. attribute:: underlay.dxf.flags

============================== ======= ===========
Underlay.dxf.flags             Value   Description
============================== ======= ===========
UNDERLAY_CLIPPING              1       clipping is on/off
UNDERLAY_ON                    2       underlay is on/off
UNDERLAY_MONOCHROME            4       Monochrome
UNDERLAY_ADJUST_FOR_BACKGROUND 8       Adjust for background
============================== ======= ===========

.. attribute:: underlay.dxf.contrast

Contrast value (20-100; default = 100)

.. attribute:: underlay.dxf.fade

Fade value (0-80; default = 0)


Underlay Attributes
-------------------


.. attribute:: Underlay.clipping

True or False (read/write)

.. attribute:: Underlay.on

True or False (read/write)

.. attribute:: Underlay.monochrome

True or False (read/write)

.. attribute:: Underlay.adjust_for_background

True or False (read/write)

.. attribute:: Underlay.scale

Scaling (x, y, z) tuple (read/write)

Underlay Methods
----------------

.. method:: Underlay.get_boundary()

Returns a list of vertices as pixel coordinates, just two values represent the lower left and the upper right
corners of the clipping rectangle, more vertices describe a clipping polygon.

.. method:: Underlay.reset_boundary()

Removes the clipping path.

.. method:: Underlay.set_boundary(vertices)

Set boundary path to vertices. 2 points describe a rectangle (lower left and upper right corner), more than 2 points
is a polygon as clipping path. Sets clipping state to 1.

.. method:: Underlay.get_underlay_def()

returns the associated (PDF)DEFINITION entity. see :class:`UnderlayDefinition`.
