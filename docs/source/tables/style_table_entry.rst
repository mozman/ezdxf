Style
=====

.. module:: ezdxf.entities
    :noindex:

Defines a text style (`DXF Reference`_), can be used by entities: :class:`Text`, :class:`Attrib` and
:class:`Attdef`.


======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'STYLE'``
Factory function         :meth:`Drawing.styles.new`
======================== ==========================================

.. seealso::

    :ref:`tut_text` and DXF internals for :ref:`dimstyle_table_internals`.

.. class:: Textstyle

    .. attribute:: dxf.handle

        DXF handle (feature for experts).

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.StyleTable`).

    .. attribute:: dxf.name

        Style name (str)

    .. attribute:: dxf.flags

        Style flags (feature for experts).

        === =======================================================
        1   If set, this entry describes a shape
        4   Vertical text
        16  If set, table entry is externally dependent on an xref
        32  If both this bit and bit 16 are set, the externally dependent xref has been successfully resolved
        64  If set, the table entry was referenced by at least one entity in the drawing the last time the drawing was
            edited. (This flag is only for the benefit of AutoCAD)commands. It can be ignored by most programs that read DXF
            files and need not be set by programs that write DXF files)
        === =======================================================

    .. attribute:: dxf.height

        Fixed height in drawing units, ``0`` for not fixed (float).

    .. attribute:: dxf.width

        Width factor (float), default is ``1``.

    .. attribute:: dxf.oblique

        Oblique angle in degrees, ``0`` is vertical (float).

    .. attribute:: dxf.generation_flags

        Text generations flags (int)

        === ===================================
        2   text is backward (mirrored in X)
        4   text is upside down (mirrored in Y)
        === ===================================

    .. attribute:: dxf.last_height

        Last height used in drawing units (float).

    .. attribute:: dxf.font

        Primary font file name (str).

    .. attribute:: dxf.bigfont

        Big font name, blank if none (str)

    .. autoproperty:: has_extended_font_data

    .. automethod:: get_extended_font_data

    .. automethod:: set_extended_font_data

    .. automethod:: discard_extended_font_data


.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-EF68AF7C-13EF-45A1-8175-ED6CE66C8FC9