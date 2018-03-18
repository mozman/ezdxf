ImageDef
========

.. class:: ImageDef(DXFObject)

Introduced in DXF version R13 (AC1012), dxftype is IMAGEDEF.

:class:`ImageDef` defines an image, which can be placed by the :class:`Image` entity. Create :class:`ImageDef` by
the :class:`Drawing` factory function :meth:`~Drawing.add_image_def`.


DXF Attributes for ImageDef
---------------------------

.. attribute:: ImageDef.dxf.filename

Relative (to the DXF file) or absolute path to the image file as string

.. attribute:: ImageDef.dxf.image_size

Image size in pixel as (x, y) tuple

.. attribute:: ImageDef.dxf.pixel_size

Default size of one pixel in AutoCAD units (x, y) tuple

.. attribute:: ImageDef.dxf.loaded

Default = 1

.. attribute:: ImageDef.dxf.resolution_units

- 0 = No units
- 2 = Centimeters
- 5 = Inch
- default is 0

