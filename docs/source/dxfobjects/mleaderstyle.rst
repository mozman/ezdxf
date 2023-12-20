MLeaderStyle
============

.. module:: ezdxf.entities
    :noindex:

The MLEADERSTYLE entity (`DXF Reference`_) stores all attributes required to
create new :class:`MultiLeader` entities. The meaning of these attributes are
not really documented in the `DXF Reference`_.
The default style "Standard" always exist.

.. seealso::

    - :class:`ezdxf.entities.MultiLeader`
    - :class:`ezdxf.render.MultiLeaderBuilder`
    - :ref:`tut_mleader`

Create a new :class:`MLeaderStyle`::

    import ezdxf

    doc = ezdxf.new()
    new_style = doc.mleader_styles.new("NewStyle")

Duplicate an existing style::

    duplicated_style = doc.mleader_styles.duplicate_entry("Standard", "DuplicatedStyle")


======================== =======================================================
Subclass of              :class:`ezdxf.entities.DXFObject`
DXF type                 ``'MLEADERSTYLE'``
Factory function         :meth:`ezdxf.document.Drawing.mleader_styles.new`
======================== =======================================================

.. class:: MLeaderStyle

    .. attribute:: dxf.align_space

        unknown meaning

    .. attribute:: dxf.arrow_head_handle

        handle of default arrow head, see also :mod:`ezdxf.render.arrows` module,
        by default no handle is set, which mean default arrow "closed filled"

    .. attribute:: dxf.arrow_head_size

        default arrow head size in drawing units, default is 4.0

    .. attribute:: dxf.block_color

        default block color as ;term:`raw color` value, default is BY_BLOCK_RAW_VALUE

    .. attribute:: dxf.block_connection_type

        === ================
        0   center extents
        1   insertion point
        === ================

    .. attribute:: dxf.block_record_handle

        handle to block record of the BLOCK content, not set by default

    .. attribute:: dxf.block_rotation

        default BLOCK rotation in radians, default is 0.0

    .. attribute:: dxf.block_scale_x

        default block x-axis scale factor, default is 1.0

    .. attribute:: dxf.block_scale_y

        default block y-axis scale factor, default is 1.0

    .. attribute:: dxf.block_scale_z

        default block z-axis scale factor, default is 1.0

    .. attribute:: dxf.break_gap_size

        default break gap size, default is 3.75

    .. attribute:: dxf.char_height

        default MTEXT char height, default is 4.0

    .. attribute:: dxf.content_type

        === =========
        0   none
        1   BLOCK
        2   MTEXT
        3   TOLERANCE
        === =========

        default is MTEXT (2)

    .. attribute:: dxf.default_text_content

        default MTEXT content as string, default is ""

    .. attribute:: dxf.dogleg_length

        default dogleg length, default is 8.0

    .. attribute:: dxf.draw_leader_order_type

        unknown meaning

    .. attribute:: dxf.draw_mleader_order_type

        unknown meaning

    .. attribute:: dxf.first_segment_angle_constraint

        angle of fist leader segment in radians, default is 0.0

    .. attribute:: dxf.has_block_rotation

    .. attribute:: dxf.has_block_scaling

    .. attribute:: dxf.has_dogleg

        default is 1

    .. attribute:: dxf.has_landing

        default is 1

    .. attribute:: dxf.is_annotative

        default is 0

    .. attribute:: dxf.landing_gap_size

        default landing gap size, default is 2.0

    .. attribute:: dxf.leader_line_color

        default leader line color as :term:`raw-color` value, default is
        BY_BLOCK_RAW_VALUE

    .. attribute:: dxf.leader_linetype_handle

        handle of default leader linetype

    .. attribute:: dxf.leader_lineweight

        default leader lineweight, default is LINEWEIGHT_BYBLOCK

    .. attribute:: dxf.leader_type

        === ====================
        0   invisible
        1   straight line leader
        2   spline leader
        === ====================

        default is 1

    .. attribute:: dxf.max_leader_segments_points

        max count of leader segments, default is 2

    .. attribute:: dxf.name

        MLEADERSTYLE name

    .. attribute:: dxf.overwrite_property_value

        unknown meaning

    .. attribute:: dxf.scale

        overall scaling factor, default is 1.0

    .. attribute:: dxf.second_segment_angle_constraint

        angle of fist leader segment in radians, default is 0.0

    .. attribute:: dxf.text_align_always_left

        use always left side to attach leaders, default is 0

    .. attribute:: dxf.text_alignment_type

        unknown meaning - its not the MTEXT attachment point!

    .. attribute:: dxf.text_angle_type

        === =======================================================
        0   text angle is equal to last leader line segment angle
        1   text is horizontal
        2   text angle is equal to last leader line segment angle, but potentially
            rotated by 180 degrees so the right side is up for readability.
        === =======================================================

        default is 1

    .. attribute:: dxf.text_attachment_direction

        defines whether the leaders attach to the left & right of the content
        BLOCK/MTEXT or attach to the top & bottom:

        === =====================================
        0   horizontal - left & right of content
        1   vertical - top & bottom of content
        === =====================================

        default is 0

    .. attribute:: dxf.text_bottom_attachment_type

        === ===============================
        9   center
        10  overline and center
        === ===============================

        default is 9

    .. attribute:: dxf.text_color

        default MTEXT color as :term:`raw-color` value, default is
        BY_BLOCK_RAW_VALUE

    .. attribute:: dxf.text_left_attachment_type

        === ========================================================
        0   top of top MTEXT line
        1   middle of top MTEXT line
        2   middle of whole MTEXT
        3   middle of bottom MTEXT line
        4   bottom of bottom MTEXT line
        5   bottom of bottom MTEXT line & underline bottom MTEXT line
        6   bottom of top MTEXT line & underline top MTEXT line
        7   bottom of top MTEXT line
        8   bottom of top MTEXT line & underline all MTEXT lines
        === ========================================================

    .. attribute:: dxf.text_right_attachment_type

        === ========================================================
        0   top of top MTEXT line
        1   middle of top MTEXT line
        2   middle of whole MTEXT
        3   middle of bottom MTEXT line
        4   bottom of bottom MTEXT line
        5   bottom of bottom MTEXT line & underline bottom MTEXT line
        6   bottom of top MTEXT line & underline top MTEXT line
        7   bottom of top MTEXT line
        8   bottom of top MTEXT line & underline all MTEXT lines
        === ========================================================

    .. attribute:: dxf.text_style_handle

        handle of the default MTEXT text style, not set by default, which means
        "Standard"

    .. attribute:: dxf.text_top_attachment_type

        === ===============================
        9   center
        10  overline and center
        === ===============================



.. _DXF Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0E489B69-17A4-4439-8505-9DCE032100B4
