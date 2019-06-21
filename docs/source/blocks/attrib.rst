Attrib
======

.. class:: Attrib

The :class:`Attrib` entity represents a text value associated with a tag. In most cases an :class:`Attrib` is
appended to an :class:`Insert` entity, but it can also appear as standalone entity.

DXF Attributes for Attrib
-------------------------

:ref:`Common graphical DXF attributes`

.. attribute:: Attrib.dxf.text

Attribute content as text (str)

.. attribute:: Attrib.dxf.insert

First alignment point of text (2D/3D Point in :ref:`OCS`), relevant for the adjustments LEFT, ALIGN and FIT.

.. attribute:: Attrib.dxf.tag

Tag to identify the attribute (str)

.. attribute:: Attrib.dxf.align_point

Second alignment point of text (2D/3D Point in :ref:`OCS`), if the justification is anything other than LEFT, the second
alignment point specify also the first alignment point: (or just the second alignment point for ALIGN and FIT)

.. attribute:: Attrib.dxf.height

Text height in drawing units (float), default is 1

.. attribute:: Attrib.dxf.rotation

Text rotation in degrees (float), default is 0

.. attribute:: Attrib.dxf.oblique

Text oblique angle (float), default is 0

.. attribute:: Attrib.dxf.style

Text style name (str), default is STANDARD

.. attribute:: Attrib.dxf.width

Width scale factor (float), default is 1

.. attribute:: Attrib.dxf.halign

Horizontal alignment flag (int), use :meth:`Attrib.set_pos` and :meth:`Attrib.set_align`

.. attribute:: Attrib.dxf.valign

Vertical alignment flag (int), use :meth:`Attrib.set_pos` and :meth:`Attrib.set_align`

.. attribute:: Attrib.dxf.text_generation_flag

Text generation flags (int)

- 2 = text is backward (mirrored in X)
- 4 = text is upside down (mirrored in Y)


Attrib Attributes
-----------------

.. attribute:: Attrib.is_invisibe

(read/write) Attribute is invisible (does not appear).

.. attribute:: Attrib.is_const

(read/write) This is a constant attribute.

.. attribute:: Attrib.is_verify

(read/write) Verification is required on input of this attribute. (CAD application feature)

.. attribute:: Attrib.is_preset

(read/write) No prompt during insertion. (CAD application feature)

Attrib Methods
--------------

.. method:: Attrib.get_pos()

see method :meth:`Text.get_pos`.

.. method:: Attrib.set_pos(p1, p2=None, align=None)

see method :meth:`Text.set_pos`.

.. method:: Attrib.get_align()

see method :meth:`Text.get_align`.

.. method:: Attrib.set_align(align='LEFT')

see method :meth:`Text.set_align`.


