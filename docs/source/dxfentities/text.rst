Text
====

.. class:: Text(GraphicEntity)

A simple one line text, dxftype is TEXT. Text height is in drawing units and defaults to 1, but it depends on
the rendering software what you really get. Width is a scaling factor, but it is not defined what is scaled (I
assume the text height), but it also depends on the rendering software what you get. This is one reason why DXF and
also DWG are not reliable for exchanging exact styling, they are just reliable for exchanging exact geometry.
Create text in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_text`.

DXF Attributes for Text
-----------------------

:ref:`Common DXF attributes for DXF R12`

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Text.dxf.text

the content text itself (str)

.. attribute:: Text.dxf.insert

first alignment point of text (2D/3D Point in :ref:`OCS`), relevant for the adjustments LEFT, ALIGN and FIT.

.. attribute:: Text.dxf.align_point

second alignment point of text (2D/3D Point in :ref:`OCS`), if the justification is anything other than LEFT, the second
alignment point specify also the first alignment point: (or just the second alignment point for ALIGN and FIT)

.. attribute:: Text.dxf.height

text height in drawing units (float); default=1

.. attribute:: Text.dxf.rotation

text rotation in degrees (float); default=0

.. attribute:: Text.dxf.oblique

text oblique angle (float); default=0

.. attribute:: Text.dxf.style

text style name (str); default=STANDARD

.. attribute:: Text.dxf.width

width scale factor (float); default=1

.. attribute:: Text.dxf.halign

horizontal alignment flag (int), use :meth:`Text.set_pos` and :meth:`Text.get_align`; default=0

.. attribute:: Text.dxf.valign

vertical alignment flag (int), use :meth:`Text.set_pos` and :meth:`Text.get_align`; default=0

.. attribute:: Text.dxf.text_generation_flag

text generation flags (int)

- 2 = text is backward (mirrored in X)
- 4 = text is upside down (mirrored in Y)

Text Methods
------------

.. method:: Text.set_pos(p1, p2=None, align=None)

:param p1: first alignment point as (x, y[, z])-tuple
:param p2: second alignment point as (x, y[, z])-tuple, required for ALIGNED and FIT else ignored
:param str align: new alignment, None for preserve existing alignment.

Set text alignment, valid positions are:

============   =============== ================= =====
Vert/Horiz     Left            Center            Right
============   =============== ================= =====
Top            TOP_LEFT        TOP_CENTER        TOP_RIGHT
Middle         MIDDLE_LEFT     MIDDLE_CENTER     MIDDLE_RIGHT
Bottom         BOTTOM_LEFT     BOTTOM_CENTER     BOTTOM_RIGHT
Baseline       LEFT            CENTER            RIGHT
============   =============== ================= =====

Special alignments are, ALIGNED and FIT, they require a second alignment point, the text
is justified with the vertical alignment `Baseline` on the virtual line between these two points.

- ALIGNED: Text is stretched or compressed to fit exactly between `p1` and `p2` and the text height is also adjusted to
  preserve height/width ratio.
- FIT: Text is stretched or compressed to fit exactly between `p1` and `p2` but only the text width is adjusted, the
  text height is fixed by the `height` attribute.
- MIDDLE: also a `special` adjustment, but the result is the same as for MIDDLE_CENTER.

.. method:: Text.get_pos()

Returns a tuple (`align`, `p1`, `p2`), `align` is the alignment method, `p1` is the alignment point, `p2` is only
relevant if `align` is ALIGNED or FIT, else it's None.

.. method:: Text.get_align()

Returns the actual text alignment as string, see tables above.

.. method:: Text.set_align(align='LEFT')

Just for experts: Sets the text alignment without setting the alignment points, set adjustment points `insert`
and `alignpoint` manually.
