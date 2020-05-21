MText
=====

.. module:: ezdxf.entities
    :noindex:

The MTEXT entity (`DXF Reference`_) fits a multiline text in a specified width but can extend vertically to an indefinite
length. You can format individual words or characters within the :class:`MText`.

.. seealso::

    :ref:`tut_mtext`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'MTEXT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_mtext`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-5E5DB93B-F8D3-4433-ADF7-E92E250D2BAB

.. class:: MText

    .. attribute:: dxf.insert

        Insertion point (3D Point in :ref:`OCS`)

    .. attribute:: dxf.char_height

        Initial text height (float); default=1.0

    .. attribute:: dxf.width

        Reference text width (float), forces text wrapping at given width.

    .. attribute:: dxf.attachment_point

        Constants defined in :mod:`ezdxf.lldxf.const`:

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

    .. attribute:: dxf.flow_direction

        Constants defined in :mod:`ezdxf.const`:

        ============================== ======= ===========
        MText.dxf.flow_direction       Value   Description
        ============================== ======= ===========
        MTEXT_LEFT_TO_RIGHT            1       left to right
        MTEXT_TOP_TO_BOTTOM            3       top to bottom
        MTEXT_BY_STYLE                 5       by style (the flow direction is inherited from the associated text style)
        ============================== ======= ===========


    .. attribute:: dxf.style

        Text style (string); default = ``'STANDARD'``

    .. attribute:: dxf.text_direction

        X-axis direction vector in :ref:`WCS` (3D Point); default value is ``(1, 0, 0)``; if :attr:`dxf.rotation` and
        :attr:`dxf.text_direction` are present,  :attr:`dxf.text_direction` wins.

    .. attribute:: dxf.rotation

        Text rotation in degrees (float); default = ``0``

    .. attribute:: dxf.line_spacing_style

        Line spacing style (int), see table below

    .. attribute:: dxf.line_spacing_factor

        Percentage of default (3-on-5) line spacing to be applied. Valid values range from ``0.25`` to ``4.00`` (float).

        Constants defined in :mod:`ezdxf.lldxf.const`:

        ============================== ======= ===========
        MText.dxf.line_spacing_style   Value   Description
        ============================== ======= ===========
        MTEXT_AT_LEAST                 1       taller characters will override
        MTEXT_EXACT                    2       taller characters will not override
        ============================== ======= ===========

    .. attribute:: dxf.bg_fill

        Defines the background fill type. (DXF R2007)

        ============================== ======= ===========
        MText.dxf.bg_fill              Value   Description
        ============================== ======= ===========
        MTEXT_BG_OFF                   0       no background color
        MTEXT_BG_COLOR                 1       use specified color
        MTEXT_BG_WINDOW_COLOR          2       use window color (?)
        MTEXT_BG_CANVAS_COLOR          3       use canvas background color
        ============================== ======= ===========

    .. attribute:: dxf.box_fill_scale

        Determines how much border there is around the text.  (DXF R2007)

        Requires: `bg_fill`, `bg_fill_color` else AutoCAD complains

        Better use :meth:`set_bg_color`

    .. attribute:: dxf.bg_fill_color

        Background fill color as :ref:`ACI` (DXF R2007)

        Better use :meth:`set_bg_color`

    .. attribute:: dxf.bg_fill_true_color

        Background fill color as true color value (DXF R2007), also :attr:`dxf.bg_fill_color` must be present,
        else AutoCAD complains.

        Better use :meth:`set_bg_color`

    .. attribute:: dxf.bg_fill_color_name

        Background fill color as name string (?) (DXF R2007), also :attr:`dxf.bg_fill_color` must be present,
        else AutoCAD complains.

        Better use :meth:`set_bg_color`

    .. attribute:: dxf.transparency

        Transparency of background fill color (DXF R2007), not supported by AutoCAD or BricsCAD.

    .. attribute:: text

        MTEXT content as string (read/write).

        Line endings ``\n`` will be replaced by the MTEXT line endings ``\P`` at DXF export, but **not**
        vice versa ``\P`` by ``\n`` at DXF file loading.

    .. automethod:: set_location

    .. automethod:: get_rotation

    .. automethod:: set_rotation

    .. automethod:: set_bg_color

    .. automethod:: __iadd__(text: str) -> MText

    .. automethod:: append(text: str) -> MText

    .. automethod:: set_font

    .. automethod:: set_color

    .. automethod:: add_stacked_text

    .. automethod:: plain_text

    .. automethod:: transform(m: Matrix44) -> MText

.. _mtext_inline_codes:

MText Inline Codes
------------------

======= ===========
Code    Description
======= ===========
\\L     Start underline
\\l     Stop underline
\\O	    Start overstrike
\\o	    Stop overstrike
\\K	    Start strike-through
\\k	    Stop strike-through
\\P	    New paragraph (new line)
\\pxi   Control codes for bullets, numbered paragraphs and columns
\\X	    Paragraph wrap on the dimension line (only in dimensions)
\\Q	    Slanting (obliquing) text by angle - e.g. \\Q30;
\\H     Text height - e.g. \\H3x;
\\W	    Text width - e.g. \\W0.8x;
\\F	    Font selection e.g. \\Fgdt;o - GDT-tolerance
\\S	    Stacking, fractions e.g. \\SA^B or \\SX/Y or \\S1#4
\\A     Alignment

        - \\A0; = bottom
        - \\A1; = center
        - \\A2; = top

\\C     Color change

        - \\C1; = red
        - \\C2; = yellow
        - \\C3; = green
        - \\C4; = cyan
        - \\C5; = blue
        - \\C6; = magenta
        - \\C7; = white

\\T     Tracking, char.spacing - e.g. \\T2;
\\~     Non-wrapping space, hard space
{}	    Braces - define the text area influenced by the code, codes and braces can be nested up to 8 levels deep
\\	    Escape character - e.g. \\{ = "{"
======= ===========

Convenient constants defined in MText:
--------------------------------------

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
