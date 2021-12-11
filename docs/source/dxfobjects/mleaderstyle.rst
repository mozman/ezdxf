MLeaderStyle
============

.. module:: ezdxf.entities
    :noindex:

The MLEADERSTYLE object (`DXF Reference`_) store all attributes required to
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

    .. attribute:: dxf.arrow_head_handle

        handle of default arrow head, see also :mod:`ezdxf.render.arrows` module

    .. attribute:: dxf.arrow_head_size

        default arrow head size in drawing units

    .. attribute:: dxf.block_color

        default block color as raw color value

    .. attribute:: dxf.block_connection_type

    .. attribute:: dxf.block_record_handle

    .. attribute:: dxf.block_rotation

    .. attribute:: dxf.block_scale_x

    .. attribute:: dxf.block_scale_y

    .. attribute:: dxf.block_scale_z

    .. attribute:: dxf.break_gap_size

    .. attribute:: dxf.char_height

    .. attribute:: dxf.content_type

    .. attribute:: dxf.default_text_content

    .. attribute:: dxf.dogleg_length

    .. attribute:: dxf.draw_leader_order_type

    .. attribute:: dxf.draw_mleader_order_type

    .. attribute:: dxf.first_segment_angle_constraint

    .. attribute:: dxf.has_block_rotation

    .. attribute:: dxf.has_block_scaling

    .. attribute:: dxf.has_dogleg

    .. attribute:: dxf.has_landing

    .. attribute:: dxf.is_annotative

    .. attribute:: dxf.landing_gap

    .. attribute:: dxf.leader_line_color

    .. attribute:: dxf.leader_linetype_handle

    .. attribute:: dxf.leader_lineweight

    .. attribute:: dxf.leader_type

    .. attribute:: dxf.max_leader_segments_points

    .. attribute:: dxf.name

    .. attribute:: dxf.overwrite_property_value

    .. attribute:: dxf.scale

    .. attribute:: dxf.second_segment_angle_constraint

    .. attribute:: dxf.text_align_always_left

    .. attribute:: dxf.text_alignment_type

    .. attribute:: dxf.text_angle_type

    .. attribute:: dxf.text_attachment_direction

    .. attribute:: dxf.text_bottom_attachment_type

    .. attribute:: dxf.text_color

    .. attribute:: dxf.text_left_attachment_type

    .. attribute:: dxf.text_right_attachment_type

    .. attribute:: dxf.text_style_handle

    .. attribute:: dxf.text_top_attachment_type

.. _DXF Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0E489B69-17A4-4439-8505-9DCE032100B4