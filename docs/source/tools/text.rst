.. _Text Tools:

Text Tools
==========

.. module:: ezdxf.tools.text

MText Support Classes
---------------------

.. class:: MTextEditor

.. autoclass:: ParagraphProperties

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

.. autofunction:: plain_mtext

.. autofunction:: text_wrap

.. autofunction:: caret_decode

.. autofunction:: is_text_vertical_stacked
