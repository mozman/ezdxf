MText
=====

.. class:: MText(GraphicEntity)

Introduced in DXF version R13 (AC1012), extended in DXF version R2007 (AC1021), dxftype is MTEXT.

Multiline text fits a specified width but can extend vertically to an indefinite length. You can format individual
words or characters within the MText. Create :class:`MText` in layouts and blocks by factory function
:meth:`~Layout.add_mtext`.

.. seealso::

    :ref:`tut_mtext`

DXF Attributes for MText
------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: MText.dxf.insert

Insertion point (3D Point)

.. attribute:: MText.dxf.char_height

Initial text height (float); default=1.0

.. attribute:: MText.dxf.width

Reference rectangle width (float)

.. attribute:: MText.dxf.attachment_point

Constants defined in :mod:`ezdxf.const`:

============================== =======
MText.dxf.attachment_point     Value
============================== =======
MTEXT_TOP_LEFT                 1
MTEXT_TOP_CENTER               2
MTEXT_TOP_RIGHT                3
MTEXT_MIDDLE_LEFT              4
MTEXT_MIDDLE_CENTER            5
MTEXT_MIDDLE_RIGHT             6
MTEXT_BOTTOM_LEFT              7
MTEXT_BOTTOM_CENTER            8
MTEXT_BOTTOM_RIGHT             9
============================== =======

.. attribute:: MText.dxf.flow_direction

Constants defined in :mod:`ezdxf.const`:

============================== ======= ===========
MText.dxf.flow_direction       Value   Description
============================== ======= ===========
MTEXT_LEFT_TO_RIGHT            1       left to right
MTEXT_TOP_TO_BOTTOM            3       top to bottom
MTEXT_BY_STYLE                 5       by style (the flow direction is inherited from the associated text style)
============================== ======= ===========


.. attribute:: MText.dxf.style

Text style (string); default='STANDARD'

.. attribute:: MText.dxf.text_direction

X-axis direction vector in WCS (3D Point); default=(1, 0, 0); if rotation and text_direction are present,
text_direction wins

.. attribute:: MText.dxf.rotation

Text rotation in degrees (float); default=0

.. attribute:: MText.dxf.line_spacing_style

line spacing style (int), see table below

.. attribute:: MText.dxf.line_spacing_factor

Percentage of default (3-on-5) line spacing to be applied. Valid values range from 0.25 to 4.00 (float)

Constants defined in :mod:`ezdxf.const`:

============================== ======= ===========
MText.dxf.line_spacing_style   Value   Description
============================== ======= ===========
MTEXT_AT_LEAST                 1       taller characters will override
MTEXT_EXACT                    2       taller characters will not override
============================== ======= ===========

MText Methods
-------------

.. method:: MText.get_text()

Returns content of :class:`MText` as string.

.. method:: MText.set_text(text)

Set *text* as :class:`MText` content.

.. method:: MText.set_location(insert, rotation=None, attachment_point=None)

Set DXF attributes *insert*, *rotation* and *attachment_point*, *None* for *rotation* or *attachment_point*
preserves the existing value.

.. method:: MText.get_rotation()

Get text rotation in degrees, independent if it is defined by *rotation* or *text_direction*

.. method:: MText.set_rotation(angle)

Set DXF attribute *rotation* to *angle* (in degrees) and deletes *text_direction* if present.

.. method:: MText.edit_data()

Context manager for :class:`MText` content::

    with mtext.edit_data() as data:
        data += "append some text" + data.NEW_LINE

        # or replace whole text
        data.text = "Replacement for the existing text."

MTextData
---------

.. class:: MTextData

Temporary object to manage the :class:`MText` content. Create context object by :meth:`MText.edit_data`.

.. seealso::

    :ref:`tut_mtext`

.. attribute:: MTextData.text

Represents the :class:`MText` content, treat it like a normal string. (read/write)

.. method:: MTextData.__iadd__(text)

Append *text* to the :attr:`MTextData.text` attribute.

.. method:: MTextData.append(text)

Synonym for :meth:`MTextData.__iadd__`.

.. method:: MTextData.set_font(name, bold=False, italic=False, codepage=1252, pitch=0)

Change actual font inline.

.. method:: MTextData.set_color(color_name)

Set text color to ``red``, ``yellow``, ``green``, ``cyan``, ``blue``, ``magenta`` or ``white``.

Convenient constants defined in MTextData:
------------------------------------------

=================== ===========
Constant            Description
=================== ===========
UNDERLINE_START     start underline text (:code:`b += b.UNDERLINE_START`)
UNDERLINE_STOP      stop underline text (:code:`b += b.UNDERLINE_STOP`)
UNDERLINE           underline text (:code:`b += b.UNDERLINE % "Text"`)
OVERSTRIKE_START    start overstrike
OVERSTRIKE_STOP     stop overstrike
OVERSTRIKE          overstrike text
STRIKE_START        start strike trough
STRIKE_STOP         stop strike trough
STRIKE              strike trough text
GROUP_START         start of group
GROUP_END           end of group
GROUP               group text
NEW_LINE            start in new line (:code:`b += "Text" + b.NEW_LINE`)
NBSP                none breaking space (:code:`b += "Python" + b.NBSP + "3.4"`)
=================== ===========
