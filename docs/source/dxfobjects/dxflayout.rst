DXFLayout
=========

.. module:: ezdxf.entities
    :noindex:

`LAYOUT`_ entity is part of a modelspace or paperspace layout definitions.

======================== ===========================================================
Subclass of              :class:`ezdxf.entities.PlotSettings`
DXF type                 ``'LAYOUT'``
Factory function         internal data structure, use :class:`~ezdxf.layouts.Layouts` to
                         manage layout objects.
======================== ===========================================================

.. _LAYOUT: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-433D25BF-655D-4697-834E-C666EDFD956D


.. class:: DXFLayout

    .. attribute:: dxf.name

        Layout name as shown in tabs by :term:`CAD` applications

    .. attribute:: dxf.layout_flags

        === =========================================================================
        1   Indicates the PSLTSCALE value for this layout when this layout is current
        2   Indicates the LIMCHECK value for this layout when this layout is current
        === =========================================================================

    .. attribute:: dxf.tab_order

        default is 1

    .. attribute:: dxf.limmin

        default is Vec2(0, 0)

    .. attribute:: dxf.limmax

        default is Vec2(420, 297)

    .. attribute:: dxf.insert_base

        default is Vec3(0, 0, 0)

    .. attribute:: dxf.extmin

        default is Vec3(1e20, 1e20, 1e20)

    .. attribute:: dxf.extmax

        default is Vec3(-1e20, -1e20, -1e20)

    .. attribute:: dxf.elevation

        default is 0

    .. attribute:: dxf.ucs_origin

        default is Vec3(0, 0, 0)

    .. attribute:: dxf.ucs_xaxis

        default is Vec3(1, 0, 0)

    .. attribute:: dxf.ucs_yaxis

        default is Vec3(0, 1, 0)

    .. attribute:: dxf.ucs_type

        === =========================
        0   UCS is not orthographic
        1   Top
        2   Bottom
        3   Front
        4   Back
        5   Left
        6   Right
        === =========================

        default is 1

    .. attribute:: dxf.block_record_handle

    .. attribute:: dxf.viewport_handle

    .. attribute:: dxf.ucs_handle

    .. attribute:: dxf.base_ucs_handle
