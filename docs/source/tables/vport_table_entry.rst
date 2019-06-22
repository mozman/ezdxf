VPort
=====

.. module:: ezdxf.entities

The viewport table stores the modelspace viewport configurations. So this entries just modelspace viewports,
not paperspace viewports, for paperspace viewports see the :class:`Viewport` entity.

.. seealso::

    DXF Internals: :ref:`vport_table_internals`

.. class:: VPort

    Subclass of :class:`DXFEntity`

    Defines a viewport configurations for the modelspace.

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.ViewportTable`).

    .. attribute:: dxf.name

    .. attribute:: dxf.flags

    .. attribute:: dxf.lower_left

    .. attribute:: dxf.upper_right

    .. attribute:: dxf.center_point

    .. attribute:: dxf.snap_base

    .. attribute:: dxf.snap_spacing

    .. attribute:: dxf.grid_spacing

    .. attribute:: dxf.direction_point

    .. attribute:: dxf.target_point

    .. attribute:: dxf.height

    .. attribute:: dxf.aspect_ratio

    .. attribute:: dxf.lens_length

    .. attribute:: dxf.front_clipping

    .. attribute:: dxf.back_clipping

    .. attribute:: dxf.snap_rotation

    .. attribute:: dxf.view_twist

    .. attribute:: dxf.status

    .. attribute:: dxf.view_mode

    .. attribute:: dxf.circle_zoom

    .. attribute:: dxf.fast_zoom

    .. attribute:: dxf.ucs_icon

    .. attribute:: dxf.snap_on

    .. attribute:: dxf.grid_on

    .. attribute:: dxf.snap_style

    .. attribute:: dxf.snap_isopair

