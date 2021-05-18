Viewport
========

.. module:: ezdxf.entities
    :noindex:

The VIEWPORT (`DXF Reference`_) entity is a window from a paperspace layout to the modelspace.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'VIEWPORT'``
Factory function         :meth:`ezdxf.layouts.Paperspace.add_viewport`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Viewport

    .. attribute:: dxf.center

        Center point of the viewport located in the paper space layout in paper
        space units stored as 3D point. (Error in the DXF reference)

    .. attribute:: dxf.width

        Viewport width in paperspace units (float)

    .. attribute:: dxf.height

        Viewport height in paperspace units (float)

    .. attribute:: dxf.status

        Viewport status field (int)

        === =====================================
        -1  On, but is fully off screen, or is one of the viewports that is not active because the $MAXACTVP count is
            currently being exceeded.
        0   Off
        >0  On and active. The value indicates the order of stacking for the viewports, where 1 is the
            active viewport, 2 is the next, and so forth
        === =====================================

    .. attribute:: dxf.id

        Viewport id (int)

    .. attribute:: dxf.view_center_point

        View center point in modelspace stored as 2D point, but represents a
        :ref:`WCS` point. (Error in the DXF reference)

    .. attribute:: dxf.snap_base_point

    .. attribute:: dxf.snap_spacing

    .. attribute:: dxf.snap_angle

    .. attribute:: dxf.grid_spacing

    .. attribute:: dxf.view_direction_vector

        View direction (3D vector in :ref:`WCS`).

    .. attribute:: dxf.view_target_point

        View target point (3D point in :ref:`WCS`).

    .. attribute:: dxf.perspective_lens_length

        Lens focal length in mm as 35mm film equivalent.

    .. attribute:: dxf.front_clip_plane_z_value

    .. attribute:: dxf.back_clip_plane_z_value

    .. attribute:: dxf.view_height

        View height in :ref:`WCS`.

    .. attribute:: dxf.view_twist_angle

    .. attribute:: dxf.circle_zoom

    .. attribute:: dxf.flags

        Viewport status bit-coded flags:

        =================== =============================== ==========================================
        Bit value           Constant in :mod:`ezdxf.const`  Description
        =================== =============================== ==========================================
        1 (0x1)             VSF_PERSPECTIVE_MODE            Enables perspective mode
        2 (0x2)             VSF_FRONT_CLIPPING              Enables front clipping
        4 (0x4)             VSF_BACK_CLIPPING               Enables back clipping
        8 (0x8)             VSF_USC_FOLLOW                  Enables UCS follow
        16 (0x10)           VSF_FRONT_CLIPPING_NOT_AT_EYE   Enables front clip not at eye
        32 (0x20)           VSF_UCS_ICON_VISIBILITY         Enables UCS icon visibility
        64 (0x40)           VSF_UCS_ICON_AT_ORIGIN          Enables UCS icon at origin
        128 (0x80)          VSF_FAST_ZOOM                   Enables fast zoom
        256 (0x100)         VSF_SNAP_MODE                   Enables snap mode
        512 (0x200)         VSF_GRID_MODE                   Enables grid mode
        1024 (0x400)        VSF_ISOMETRIC_SNAP_STYLE        Enables isometric snap style
        2048 (0x800)        VSF_HIDE_PLOT_MODE              Enables hide plot mode
        4096 (0x1000)       VSF_KISOPAIR_TOP                kIsoPairTop. If set and kIsoPairRight is not set, then isopair top is enabled. If both kIsoPairTop
                                                            and kIsoPairRight are set, then isopair left is enabled
        8192 (0x2000)       VSF_KISOPAIR_RIGHT              kIsoPairRight. If set and kIsoPairTop is not set, then isopair right is enabled
        16384 (0x4000)      VSF_LOCK_ZOOM                   Enables viewport zoom locking
        32768 (0x8000)      VSF_CURRENTLY_ALWAYS_ENABLED    Currently always enabled
        65536 (0x10000)     VSF_NON_RECTANGULAR_CLIPPING    Enables non-rectangular clipping
        131072 (0x20000)    VSF_TURN_VIEWPORT_OFF           Turns the viewport off
        262144 (0x40000)    VSF_NO_GRID_LIMITS              Enables the display of the grid beyond the drawing limits
        524288 (0x80000)    VSF_ADAPTIVE_GRID_DISPLAY       Enable adaptive grid display
        1048576 (0x100000)  VSF_SUBDIVIDE_GRID              Enables subdivision of the grid below the set grid spacing when the grid display is adaptive
        2097152 (0x200000)  VSF_GRID_FOLLOW_WORKPLANE       Enables grid follows workplane switching
        =================== =============================== ==========================================

        Use helper method :meth:`~DXFEntity.set_flag_state` to set and clear
        viewport flags, e.g. lock viewport::

            vp.set_flag_state(ezdxf.const.VSF_LOCK_ZOOM, True)

    .. attribute:: dxf.clipping_boundary_handle

    .. attribute:: dxf.plot_style_name

    .. attribute:: dxf.render_mode

        === ============================
        0   2D Optimized (classic 2D)
        1   Wireframe
        2   Hidden line
        3   Flat shaded
        4   Gouraud shaded
        5   Flat shaded with wireframe
        6   Gouraud shaded with wireframe
        === ============================

    .. attribute:: dxf.ucs_per_viewport

    .. attribute:: dxf.ucs_icon

    .. attribute:: dxf.ucs_origin

        UCS origin as 3D point.

    .. attribute:: dxf.ucs_x_axis

        UCS x-axis as 3D vector.

    .. attribute:: dxf.ucs_y_axis

        UCS y-axis as 3D vector.

    .. attribute:: dxf.ucs_handle

        Handle of :class:`UCSTable` if UCS is a named UCS. If not present, then UCS is unnamed.

    .. attribute:: dxf.ucs_ortho_type

        === ====================
        0   not orthographic
        1   Top
        2   Bottom
        3   Front
        4   Back
        5   Left
        6   Right
        === ====================

    .. attribute:: dxf.ucs_base_handle

        Handle of :class:`UCSTable` of base UCS if UCS is orthographic (:attr:`Viewport.dxf.ucs_ortho_type` is non-zero).
        If not present and :attr:`Viewport.dxf.ucs_ortho_type` is non-zero, then base UCS is taken to be WORLD.

    .. attribute:: dxf.elevation

    .. attribute:: dxf.shade_plot_mode

        (DXF R2004)

        === ============
        0   As Displayed
        1   Wireframe
        2   Hidden
        3   Rendered
        === ============

    .. attribute:: dxf.grid_frequency

        Frequency of major grid lines compared to minor grid lines. (DXF R2007)

    .. attribute:: dxf.background_handle

    .. attribute:: dxf.shade_plot_handle

    .. attribute:: dxf.visual_style_handle

    .. attribute:: dxf.default_lighting_flag

    .. attribute:: dxf.default_lighting_style

        === ==================
        0   One distant light
        1   Two distant lights
        === ==================

    .. attribute:: dxf.view_brightness

    .. attribute:: dxf.view_contrast

    .. attribute:: dxf.ambient_light_color_1

        as :ref:`ACI`

    .. attribute:: dxf.ambient_light_color_2

        as true color value

    .. attribute:: dxf.ambient_light_color_3

        as true color value

    .. attribute:: dxf.sun_handle

    .. attribute:: dxf.ref_vp_object_1

    .. attribute:: dxf.ref_vp_object_2

    .. attribute:: dxf.ref_vp_object_3

    .. attribute:: dxf.ref_vp_object_4

    .. autoattribute:: frozen_layers

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-2602B0FB-02E4-4B9A-B03C-B1D904753D34