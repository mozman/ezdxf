Style
=====

.. class:: Style

Defines a text style, can be used by entities: :class:`Text`, :class:`Attrib` and :class:`Attdef`

DXF Attributes for Style
------------------------

.. attribute:: Style.dxf.handle

DXF handle (feature for experts)

.. attribute:: Style.dxf.owner

requires DXF R13 or later

.. attribute:: Style.dxf.name

Style name (str)

.. attribute:: Style.dxf.flags

Style flags (feature for experts)

.. attribute:: Style.dxf.height

Fixed height in drawing units, 0 for not fixed (float)

.. attribute:: Style.dxf.width

Width factor (float), default is 1

.. attribute:: Style.dxf.oblique

Oblique angle in degrees, 0 is vertical (float)

.. attribute:: Style.dxf.text_generation_flags

Text generations flags (int)

- 2 = text is backward (mirrored in X)
- 4 = text is upside down (mirrored in Y)

.. attribute:: Style.dxf.last_height

Last height used in drawing units (float)

.. attribute:: Style.dxf.font

Primary font file name (str)

.. attribute:: Style.dxf.bigfont

Big font name, blank if none (str)

