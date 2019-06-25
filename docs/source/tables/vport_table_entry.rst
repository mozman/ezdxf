VPort
=====

.. module:: ezdxf.entities

The viewport table (`DXF Reference`_) stores the modelspace viewport configurations. So this entries just modelspace
viewports, not paperspace viewports, for paperspace viewports see the :class:`Viewport` entity.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'VPORT'``
Factory function         :meth:`Drawing.viewports.new`
======================== ==========================================

.. seealso::

    DXF Internals: :ref:`vport_table_internals`

.. class:: VPort

    Subclass of :class:`DXFEntity`

    Defines a viewport configurations for the modelspace.

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.ViewportTable`).

    .. attribute:: dxf.name

        Viewport name

    .. attribute:: dxf.flags

        Standard flag values (bit-coded values):

        === ==============================================================
        16  If set, table entry is externally dependent on an xref
        32  If both this bit and bit 16 are set, the externally dependent xref has been successfully resolved
        64  If set, the table entry was referenced by at least one entity in the drawing the last time the drawing
            was edited. (This flag is only for the benefit of AutoCAD)
        === ==============================================================

    .. attribute:: dxf.lower_left

        Lower-left corner of viewport

    .. attribute:: dxf.upper_right

        Upper-right corner of viewport

    .. attribute:: dxf.center_point

        View center point (in :ref:`DCS`)

    .. attribute:: dxf.snap_base

        Snap base point (in :ref:`DCS`)

    .. attribute:: dxf.snap_spacing

        Snap spacing X and Y

    .. attribute:: dxf.grid_spacing

        Grid spacing X and Y

    .. attribute:: dxf.direction_point

        View direction from target point (in :ref:`WCS`)

    .. attribute:: dxf.target_point

        View target point (in :ref:`WCS`)

    .. attribute:: dxf.height

        View height

    .. attribute:: dxf.aspect_ratio

    .. attribute:: dxf.lens_length

        Lens focal length in mm

    .. attribute:: dxf.front_clipping

        Front clipping plane (offset from target point)

    .. attribute:: dxf.back_clipping

        Back clipping plane (offset from target point)

    .. attribute:: dxf.snap_rotation

        Snap rotation angle in degrees

    .. attribute:: dxf.view_twist

        View twist angle in degrees

    .. attribute:: dxf.status

    .. attribute:: dxf.view_mode

    .. attribute:: dxf.circle_zoom

    .. attribute:: dxf.fast_zoom

    .. attribute:: dxf.ucs_icon

    .. attribute:: dxf.snap_on

    .. attribute:: dxf.grid_on

    .. attribute:: dxf.snap_style

    .. attribute:: dxf.snap_isopair

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-8CE7CC87-27BD-4490-89DA-C21F516415A9