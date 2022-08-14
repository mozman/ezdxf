Text
====

.. module:: ezdxf.entities
    :noindex:

The single line TEXT entity (`DXF Reference`_). The :attr:`~Text.dxf.style`
attribute stores the associated :class:`Textstyle` entity as string,
which defines the basic font properties. The text size is stored as cap height
in the :attr:`~Text.dxf.height` attribute in drawing units. Text alignments
are defined as enums of type :class:`ezdxf.enums.TextEntityAlignment`.

.. seealso::

    See the documentation for the :class:`Textstyle` class to understand the
    limitations of text representation in the DXF format.

    :ref:`tut_text`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'TEXT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_text`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided
    factory functions!


.. class:: Text

    .. attribute:: dxf.text

        Text content as string.

    .. attribute:: dxf.insert

        First alignment point of text (2D/3D Point in :ref:`OCS`), relevant for
        the adjustments LEFT, ALIGNED  and FIT.

    .. attribute:: dxf.align_point

        The main alignment point of text (2D/3D Point in :ref:`OCS`), if the
        alignment is anything else than LEFT, or the second alignment point
        for the ALIGNED and FIT alignments.

    .. attribute:: dxf.height

        Text height in drawing units as float value, the default value is 1.

    .. attribute:: dxf.rotation

        Text rotation in degrees as float value, the default value is 0.

    .. attribute:: dxf.oblique

        Text oblique angle (slanting)  in degrees as float value, the default
        value is 0 (straight vertical text).

    .. attribute:: dxf.style

        :class:`Textstyle` name as case insensitive string, the default value
        is "Standard"

    .. attribute:: dxf.width

        Width scale factor as float value, the default value is 1.

    .. attribute:: dxf.halign

        Horizontal alignment flag as int value, use the :meth:`~Text.set_placement`
        and :meth:`~Text.get_align_enum` methods to handle text alignment, the
        default value is 0.

        === =========
        0   Left
        2   Right
        3   Aligned (if vertical alignment = 0)
        4   Middle (if vertical alignment = 0)
        5   Fit (if vertical alignment = 0)
        === =========

    .. attribute:: dxf.valign

        Vertical alignment flag as int value, use the :meth:`~Text.set_placement`
        and :meth:`~Text.get_align_enum` methods to handle text alignment, the
        default value is 0.

        === =========
        0   Baseline
        1   Bottom
        2   Middle
        3   Top
        === =========

    .. attribute:: dxf.text_generation_flag

        Text generation flags as int value, use the :attr:`is_backward` and
        :attr:`is_upside_down` attributes to handle this flags.

        === =========
        2   text is backward (mirrored in X)
        4   text is upside down (mirrored in Y)
        === =========

    .. autoproperty:: is_backward

    .. autoproperty:: is_upside_down

    .. automethod:: set_placement

    .. automethod:: set_pos

    .. automethod:: get_placement

    .. automethod:: get_pos

    .. automethod:: get_align_enum

    .. automethod:: get_align

    .. automethod:: set_align_enum

    .. automethod:: set_align

    .. automethod:: transform

    .. automethod:: translate

    .. automethod:: plain_text

    .. automethod:: font_name

    .. automethod:: fit_length

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-62E5383D-8A14-47B4-BFC4-35824CAE8363