AttDef
======

.. class:: Attdef

The :class:`Attdef` entity is a place holder in the :class:`Block` definition, which will be used to create an
appended :class:`Attrib` entity for an :class:`Insert` entity.

DXF Attributes for AttDef
-------------------------

:ref:`Common graphical DXF attributes`

.. attribute:: AttDef.dxf.text

The default text prompted by CAD programs (str)

.. attribute:: AttDef.dxf.insert

First alignment point of text (2D/3D Point in :ref:`OCS`), relevant for the adjustments LEFT, ALIGN and FIT.

.. attribute:: AttDef.dxf.tag

Tag to identify the attribute (str)

.. attribute:: AttDef.dxf.align_point

Second alignment point of text (2D/3D Point in :ref:`OCS`), if the justification is anything other than LEFT, the second alignment
point specify also the first alignment point: (or just the second alignment point for ALIGN and FIT)

.. attribute:: AttDef.dxf.height

Text height in drawing units (float), default is 1

.. attribute:: AttDef.dxf.rotation

Text rotation in degrees (float), default is 0

.. attribute:: AttDef.dxf.oblique

Text oblique angle (float), default is 0

.. attribute:: AttDef.dxf.style

Text style name (str), default is ``STANDARD``

.. attribute:: AttDef.dxf.width

Width scale factor (float), default is 1

.. attribute:: AttDef.dxf.halign

Horizontal alignment flag (int), use :meth:`Attdef.set_pos` and :meth:`Attdef.set_align`

.. attribute:: AttDef.dxf.valign

Vertical alignment flag (int), use :meth:`Attdef.set_pos` and :meth:`Attdef.set_align`

.. attribute:: AttDef.dxf.text_generation_flag

Text generation flags (int)

- 2 = text is backward (mirrored in X)
- 4 = text is upside down (mirrored in Y)

.. attribute:: AttDef.dxf.prompt

Text prompted by CAD programs at placing a block reference containing this :class:`Attdef`

.. attribute:: AttDef.dxf.field_length

Just relevant to CAD programs for validating user input

AttDef Attributes
-----------------

.. attribute:: Attdef.is_invisible

(read/write) Attribute is invisible (does not appear).

.. attribute:: Attdef.is_const

(read/write) This is a constant attribute.

.. attribute:: Attdef.is_verify

(read/write) Verification is required on input of this attribute. (CAD application feature)

.. attribute:: Attdef.is_preset

(read/write) No prompt during insertion. (CAD application feature)

AttDef Methods
--------------

.. method:: Attdef.get_pos()

see method :meth:`Text.get_pos`.

.. method:: Attdef.set_pos(p1, p2=None, align=None)

see method :meth:`Text.set_pos`.

.. method:: Attdef.get_align()

see method :meth:`Text.get_align`.

.. method:: Attdef.set_align(align='LEFT')

see method :meth:`Text.set_align`.
