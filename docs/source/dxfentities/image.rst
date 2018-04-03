Image
=====

.. class:: Image(GraphicEntity)

Introduced in DXF version R13 (AC1012), dxftype is IMAGE.

Add a raster image to the DXF file, the file itself is not embedded into the DXF file, it is always a separated file.
The IMAGE entity is like a block reference, you can use it multiple times to add the image on different locations
with different scales and rotations. But therefore you need a also a IMAGEDEF entity, see :class:`ImageDef`.
Create :class:`Image` in layouts and blocks by factory function :meth:`~Layout.add_image`. ezdxf creates only
images in the XY-plan. You can place images in the 3D space too, but then you have to set the *u_pixel* and
the *v_pixel* vectors by yourself.


DXF Attributes for Image
------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Image.dxf.insert

Insertion point, lower left corner of the image (3D Point in :ref:`WCS`).

.. attribute:: Image.dxf.u_pixel

U-vector of a single pixel (points along the visual bottom of the image, starting at the insertion point) (x, y, z) tuple

.. attribute:: Image.dxf.v_pixel

V-vector of a single pixel (points along the visual left side of the image, starting at the insertion point) (x, y, z) tuple

.. attribute:: Image.dxf.image_size

Image size in pixels

.. attribute:: Image.dxf.image_def

Handle to the image definition entity, see :class:`ImageDef`

.. attribute:: Image.dxf.flags

=========================== ======= ===========
Image.dxf.flags             Value   Description
=========================== ======= ===========
Image.SHOW_IMAGE            1       Show image
Image.SHOW_WHEN_NOT_ALIGNED 2       Show image when not aligned with screen
Image.USE_CLIPPING_BOUNDARY 4       Use clipping boundary
Image.USE_TRANSPARENCY      8       Transparency is on
=========================== ======= ===========

.. attribute:: Image.dxf.clipping

Clipping state: 0 = Off; 1 = On

.. attribute:: Image.dxf.brightness

Brightness value (0-100; default = 50)

.. attribute:: Image.dxf.contrast

Contrast value (0-100; default = 50)

.. attribute:: Image.dxf.fade

Fade value (0-100; default = 0)

.. attribute:: Image.dxf.clipping_boundary_type

Clipping boundary type. 1 = Rectangular; 2 = Polygonal

.. attribute:: Image.dxf.count_boundary_points

Number of clip boundary vertices

.. attribute:: Image.dxf.clip_mode

Clip mode: 0 = Outside; 1 = Inside (R2000)


Image Methods
-------------

.. method:: Image.get_boundary()

Returns a list of vertices as pixel coordinates, lower left corner is (0, 0) and upper right corner is (ImageSizeX,
ImageSizeY), independent from the absolute location of the image in WCS.

.. method:: Image.reset_boundary()

Reset boundary path to the default rectangle [(0, 0), (ImageSizeX, ImageSizeY)].

.. method:: Image.set_boundary(vertices)

Set boundary path to vertices. 2 points describe a rectangle (lower left and upper right corner), more than 2 points
is a polygon as clipping path. Sets clipping state to 1 and also sets the Image.USE_CLIPPING_BOUNDARY flag.

.. method:: Image.get_image_def()

returns the associated IMAGEDEF entity. see :class:`ImageDef`.

