View
====

.. module:: ezdxf.entities
    :noindex:

The View table (`DXF Reference`_) stores named views of the model or paperspace
layouts. This stored views makes parts of the drawing or some view points of the
model in a CAD applications more accessible. This views have no influence to the
drawing content or to the generated output by exporting PDFs or plotting on paper
sheets, they are just for the convenience of CAD application users.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFEntity`
DXF type                 ``'VIEW'``
Factory function         :meth:`Drawing.views.new`
======================== ==========================================

.. seealso::

    DXF Internals: :ref:`view_table_internals`

.. class:: View

    .. attribute:: dxf.owner

        Handle to owner (:class:`~ezdxf.sections.table.Table`).

    .. attribute:: dxf.name

        Name of view.

    .. attribute:: dxf.flags

        Standard flag values (bit-coded values):

        === =========================================================
        1   If set, this is a paper space view
        16  If set, table entry is externally dependent on an xref
        32  If both this bit and bit 16 are set, the externally dependent xref
            has been successfully resolved
        64  If set, the table entry was referenced by at least one entity in the
            drawing the last time the drawing was edited. (This flag is only for
            the benefit of AutoCAD)
        === =========================================================

    .. attribute:: dxf.height

        View height (in DCS)

    .. attribute:: dxf.width

        View width (in DCS)

    .. attribute:: dxf.center_point

        View center point (in DCS)

    .. attribute:: dxf.direction_point

        View direction from target (in WCS)

    .. attribute:: dxf.target_point

        Target point (in WCS)

    .. attribute:: dxf.lens_length

        Lens length

    .. attribute:: dxf.front_clipping

        Front clipping plane (offset from target point)

    .. attribute:: dxf.back_clipping

        Back clipping plane (offset from target point)

    .. attribute:: dxf.view_twist

        Twist angle in degrees.

    .. attribute:: dxf.view_mode

        View mode (see VIEWMODE system variable)

    .. attribute:: dxf.render_mode

        === =================================
        0   2D Optimized (classic 2D)
        1   Wireframe
        2   Hidden line
        3   Flat shaded
        4   Gouraud shaded
        5   Flat shaded with wireframe
        6   Gouraud shaded with wireframe
        === =================================

    .. attribute:: dxf.ucs

        1 if there is a UCS associated to this view; 0 otherwise

    .. attribute:: dxf.ucs_origin

        UCS origin as (x, y, z) tuple (appears only if :attr:`ucs` is set to 1)

    .. attribute:: dxf.ucs_xaxis

        UCS x-axis as (x, y, z) tuple (appears only if :attr:`ucs` is set to 1)

    .. attribute:: dxf.ucs_yaxis

        UCS y-axis as (x, y, z) tuple (appears only if :attr:`ucs` is set to 1)

    .. attribute:: dxf.ucs_ortho_type

        Orthographic type of UCS (appears only if :attr:`ucs` is set to 1)

        === =======================
        0   UCS is not orthographic
        1   Top
        2   Bottom
        3   Front
        4   Back
        5   Left
        6   Right
        === =======================

    .. attribute:: dxf.elevation

        UCS elevation

    .. attribute:: dxf.ucs_handle

        Handle of :class:`~ezdxf.entities.UCSTable` if UCS is a named UCS. If not
        present, then UCS is unnamed (appears only if :attr:`ucs` is set to 1)

    .. attribute:: dxf.base_ucs_handle

        Handle of :class:`~ezdxf.entities.UCSTable` of base UCS if UCS is
        orthographic. If not present and :attr:`ucs_ortho_type` is non-zero,
        then base UCS is taken to be WORLD (appears only if :attr:`ucs` is
        set to 1)

    .. attribute:: dxf.camera_plottable

        1 if the camera is plottable

    .. attribute:: dxf.background_handle

        Handle to background object (optional)

    .. attribute:: dxf.live_selection_handle

        Handle to live section object (optional)

    .. attribute:: dxf.visual_style_handle

        Handle to visual style object (optional)

    .. attribute:: dxf.sun_handle

        Sun hard ownership handle.

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-CF3094AB-ECA9-43C1-8075-7791AC84F97C
