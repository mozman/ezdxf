.. _Text Tools:

Text Tools
==========

.. module:: ezdxf.tools.text

MTextEditor
-----------

.. autoclass:: MTextEditor

    .. attribute:: text

        The MTEXT content as a simple string.

    .. automethod:: append

    .. automethod:: __iadd__

    .. automethod:: __str__

    .. automethod:: clear

    .. automethod:: font

    .. automethod:: height

    .. automethod:: scale_height

    .. automethod:: width_factor

    .. automethod:: char_tracking_factor

    .. automethod:: oblique

    .. automethod:: color

    .. automethod:: aci

    .. automethod:: rgb

    .. automethod:: underline

    .. automethod:: overline

    .. automethod:: strike_through

    .. automethod:: group

    .. automethod:: stack

    .. automethod:: paragraph

    .. automethod:: bullet_list

Constants stored in the :class:`MTextEditor` class:

=================== ==========
NEW_LINE            ``'\P'``
NEW_PARAGRAPH       ``'\P'``
NEW_COLUMN          ``'\N``
UNDERLINE_START     ``'\L'``
UNDERLINE_STOP      ``'\l'``
OVERSTRIKE_START    ``'\O'``
OVERSTRIKE_STOP     ``'\o'``
STRIKE_START        ``'\K'``
STRIKE_STOP         ``'\k'``
ALIGN_BOTTOM        ``'\A0;'``
ALIGN_MIDDLE        ``'\A1;'``
ALIGN_TOP           ``'\A2;'``
NBSP                ``'\~'``
TAB                 ``'^I'``
=================== ==========

.. autoclass:: ParagraphProperties(indent=0, left=0, right=0, align=DEFAULT, tab_stops=[])

    .. automethod:: tostring


.. class:: ezdxf.lldxf.const.MTextParagraphAlignment

    .. attribute:: DEFAULT

    .. attribute:: LEFT

    .. attribute:: RIGHT

    .. attribute:: CENTER

    .. attribute:: JUSTIFIED

    .. attribute:: DISTRIBUTED


Single Line Text
----------------

.. autoclass:: TextLine

    .. autoproperty:: width

    .. autoproperty:: height

    .. automethod:: stretch(alignment: str, p1: Vec3, p2: Vec3) -> None

    .. automethod:: font_measurements

    .. automethod:: baseline_vertices(insert, halign, valign, angle, scale) -> List[Vec3]

    .. automethod:: corner_vertices(insert, halign, valign, angle, scale, oblique)  -> List[Vec3]

    .. automethod:: transform_2d(vertices, insert, shift, rotation, scale, oblique) -> List[Vec3]

Functions
---------

.. autofunction:: plain_text

.. autofunction:: fast_plain_mtext

.. autofunction:: plain_mtext

.. autofunction:: text_wrap

.. autofunction:: caret_decode

.. autofunction:: is_text_vertical_stacked

.. autofunction:: is_upside_down_text_angle

.. autofunction:: upright_text_angle
