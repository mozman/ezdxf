Text
====

.. module:: ezdxf.entities
    :noindex:

One line TEXT entity (`DXF Reference`_). :attr:`Text.dxf.height` in drawing units and defaults to ``1``, but it also depends on the
font rendering of the CAD application. :attr:`Text.dxf.width` is a scaling factor, but the DXF reference does not define
the base value to scale, in practice the :attr:`Text.dxf.height` is the base value, the effective text width
depends on the font defined by :attr:`Text.dxf.style` and the font rendering of the CAD application, especially for
proportional fonts, text width calculation is nearly impossible without knowlegde of the used CAD application and their
font rendering behavior. This is one reason why the DXF and also DWG file format are not reliable for exchanging exact
text layout, they are just reliable for exchanging exact geometry.

.. seealso::

    :ref:`tut_text`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'TEXT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_text`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Text

    .. attribute:: dxf.text

        Text content. (str)

    .. attribute:: dxf.insert

        First alignment point of text (2D/3D Point in :ref:`OCS`), relevant for the adjustments ``'LEFT'``, ``'ALIGN'``
        and ``'FIT'``.

    .. attribute:: dxf.align_point

    second alignment point of text (2D/3D Point in :ref:`OCS`), if the justification is anything other than ``'LEFT'``,
    the second alignment point specify also the first alignment point: (or just the second alignment point for
    ``'ALIGN'`` and ``'FIT'``)

    .. attribute:: dxf.height

        Text height in drawing units (float); default value is ``1``

    .. attribute:: dxf.rotation

        Text rotation in degrees (float); default value is ``0``

    .. attribute:: dxf.oblique

        Text oblique angle in degrees (float); default value is ``0`` (straight vertical text)

    .. attribute:: dxf.style

        :class:`Textstyle` name (str); default value is ``'Standard'``

    .. attribute:: dxf.width

        Width scale factor (float); default value is ``1``

    .. attribute:: dxf.halign

        Horizontal alignment flag (int), use :meth:`~Text.set_pos` and :meth:`~Text.get_align`; default value is ``0``

        === ===================================
        0   Left
        2   Right
        3   Aligned (if vertical alignment = 0)
        4   Middle (if vertical alignment = 0)
        5   Fit (if vertical alignment = 0)
        === ===================================

    .. attribute:: dxf.valign

        Vertical alignment flag (int), use :meth:`~Text.set_pos` and :meth:`~Text.get_align`; default value is ``0``

        === ===========
        0   Baseline
        1   Bottom
        2   Middle
        3   Top
        === ===========

    .. attribute:: dxf.text_generation_flag

        Text generation flags (int)

        === ===================================
        2   text is backward (mirrored in X)
        4   text is upside down (mirrored in Y)
        === ===================================

    .. automethod:: set_pos

    .. automethod:: get_pos

    .. automethod:: get_align

    .. automethod:: set_align(align: str = 'LEFT') -> Text

    .. automethod:: transform_to_wcs(ucs: UCS) -> Text

    .. automethod:: transform(m: Matrix44) -> Text

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-62E5383D-8A14-47B4-BFC4-35824CAE8363