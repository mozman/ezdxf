MultiLeader
===========

.. module:: ezdxf.entities
    :noindex:

.. versionadded:: 0.18

The MULTILEADER entity (`DXF Reference`_) represents one ore more leaders,
made up of one or more vertices (or spline fit points) and an arrowhead.
In contrast to the :class:`Leader` entity the text- or block content is part of
the MULTILEADER entity.

AutoCAD, BricsCAD and maybe other CAD applications do accept ``'MLEADER'`` as
type string but they always create entities with ``'MULTILEADER'`` as type
string.

Because of the complexity of the MLEADER entity it is recommend to use the
:class:`~ezdxf.render.MultiLeaderBuilder` to construct the entity.

The visual design is based on an associated :class:`~ezdxf.entities.MLeaderStyle`,
but almost all attributes are also stored in the MULTILEADER entity itself.

The attribute :attr:`MultiLeader.dxf.property_override_flags` should indicate
which MLEADERSTYLE attributes are overridden by MULTILEADER attributes,
but these flags do not always reflect the state of overridden attributes.
The `ezdxf` MULTILEADER renderer uses always the attributes from
the MULTILEADER entity and ignores the override flags.

All vertices are WCS coordinates, even those for BLOCK entities which are OCS
coordinates in the usual case.

.. seealso::

    - :class:`ezdxf.entities.MLeaderStyle`
    - :class:`ezdxf.render.MultiLeaderBuilder`
    - :ref:`tut_mleader`
    - :ref:`MLEADER Internals`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'MULTILEADER'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_multileader`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-72D20B8C-0F5E-4993-BEB7-0FCF94F32BE0


.. class:: MultiLeader

    .. attribute:: dxf.arrow_head_handle

        handle of the arrow head, see also :mod:`ezdxf.render.arrows` module,
        "closed filled" arrow if not set

    .. attribute:: dxf.arrow_head_size

        arrow head size in drawing units

    .. attribute:: dxf.block_color

        block color as :term:`raw color` value, default is BY_BLOCK_RAW_VALUE

    .. attribute:: dxf.block_connection_type

        === ================
        0   center extents
        1   insertion point
        === ================

    .. attribute:: dxf.block_record_handle

        handle to block record of the BLOCK content

    .. attribute:: dxf.block_rotation

        BLOCK rotation in radians

    .. attribute:: dxf.block_scale_vector

        :class:`Vec3` object which stores the scaling factors for the x-, y-
        and z-axis

    .. attribute:: dxf.content_type

        === =========
        0   none
        1   BLOCK
        2   MTEXT
        3   TOLERANCE
        === =========

    .. attribute:: dxf.dogleg_length

        dogleg length in drawing units

    .. attribute:: dxf.has_dogleg

    .. attribute:: dxf.has_landing

    .. attribute:: dxf.has_text_frame

    .. attribute:: dxf.is_annotative

    .. attribute:: dxf.is_text_direction_negative

    .. attribute:: dxf.leader_extend_to_text

    .. attribute:: dxf.leader_line_color

         leader line color as :term:`raw color` value

    .. attribute:: dxf.leader_linetype_handle

        handle of the leader linetype, "CONTINUOUS" if not set

    .. attribute:: dxf.leader_lineweight

    .. attribute:: dxf.leader_type

        === ====================
        0   invisible
        1   straight line leader
        2   spline leader
        === ====================

    .. attribute:: dxf.property_override_flags

        Each bit shows if the MLEADERSTYLE is overridden by the value in the
        MULTILEADER entity, but this is not always the case for all values,
        it seems to be save to always use the value from the MULTILEADER entity.

    .. attribute:: dxf.scale

        overall scaling factor

    .. attribute:: dxf.style_handle

        handle to the associated MLEADERSTYLE object

    .. attribute:: dxf.text_IPE_align

        unknown meaning

    .. attribute:: dxf.text_alignment_type

        unknown meaning - its not the MTEXT attachment point!

    .. attribute:: dxf.text_angle_type

        === =======================================================
        0   text angle is equal to last leader line segment angle
        1   text is horizontal
        2   text angle is equal to last leader line segment angle, but potentially
            rotated by 180 degrees so the right side is up for readability.
        === =======================================================

    .. attribute:: dxf.text_attachment_direction

        defines whether the leaders attach to the left & right of the content
        BLOCK/MTEXT or attach to the top & bottom:

        === =====================================
        0   horizontal - left & right of content
        1   vertical - top & bottom of content
        === =====================================

    .. attribute:: dxf.text_attachment_point

        MTEXT attachment point

        === =============
        1   top left
        2   top center
        3   top right
        === =============

    .. attribute:: dxf.text_bottom_attachment_type

        === ===============================
        9   center
        10  overline and center
        === ===============================

    .. attribute:: dxf.text_color

        MTEXT color as :term:`raw color` value

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

        handle of the MTEXT text style, "Standard" if not set

    .. attribute:: dxf.text_top_attachment_type

        === ===============================
        9   center
        10  overline and center
        === ===============================

    .. attribute:: dxf.version

        always 2?

    .. attribute:: context

        :class:`MLeaderContext` instance

    .. attribute:: arrow_heads

        list of :class:`ArrowHeadData`

    .. attribute:: block_attribs

        list of :class:`AttribData`

    .. automethod:: virtual_entities() -> Iterable[DXFGraphic]

    .. automethod:: explode(target_layout: BaseLayout = None) -> EntityQuery

    .. automethod:: transform(m: Matrix44) -> MultiLeader

.. class:: MLeaderContext

    .. attribute:: leaders

        list of :class:`LeaderData` objects

    .. attribute:: scale

        redundant data: :attr:`MultiLeader.dxf.scale`

    .. attribute:: base_point

        insert location as :class:`Vec3` of the MTEXT or the BLOCK entity?

    .. attribute:: char_height

        MTEXT char height, already scaled

    .. attribute:: arrow_head_size

        redundant data: :attr:`MultiLeader.dxf.arrow_head_size`

    .. attribute:: landing_gap_size

    .. attribute:: left_attachment

        redundant data: :attr:`MultiLeader.dxf.text_left_attachment_type`

    .. attribute:: right_attachment

        redundant data: :attr:`MultiLeader.dxf.text_right_attachment_type`

    .. attribute:: text_align_type

        redundant data: :attr:`MultiLeader.dxf.text_attachment_point`

    .. attribute:: attachment_type

        BLOCK alignment?

        === ===============
        0   content extents
        1   insertion point
        === ===============

    .. attribute:: mtext

        instance of :class:`MTextData` if content is MTEXT otherwise ``None``

    .. attribute:: block

        instance of :class:`BlockData` if content is BLOCK otherwise ``None``

    .. attribute:: plane_origin

        :class:`Vec3`

    .. attribute:: plane_x_axis

        :class:`Vec3`

    .. attribute:: plane_y_axis

        :class:`Vec3`

    .. attribute:: plane_normal_reversed

        the plan normal is x-axis "cross" y-axis (right-hand-rule), this flag
        indicates to invert this plan normal

    .. attribute:: top_attachment

        redundant data: :attr:`MultiLeader.dxf.text_top_attachment_type`

    .. attribute:: bottom_attachment

        redundant data: :attr:`MultiLeader.dxf.text_bottom_attachment_type`

.. class:: LeaderData

    .. attribute:: lines

        list of :class:`LeaderLine`

    .. attribute:: has_last_leader_line

        unknown meaning

    .. attribute:: has_dogleg_vector

    .. attribute:: last_leader_point

        WCS point as :class:`Vec3`

    .. attribute:: dogleg_vector

        WCS direction as :class:`Vec3`

    .. attribute:: dogleg_length

        redundant data: :attr:`MultiLeader.dxf.dogleg_length`

    .. attribute:: index

        leader index?

    .. attribute:: attachment_direction

        redundant data: :attr:`MultiLeader.dxf.text_attachment_direction`

    .. attribute:: breaks

        list of break vertices as :class:`Vec3` objects

.. class:: LeaderLine

    .. attribute:: vertices

        list of WCS coordinates as :class:`Vec3`

    .. attribute:: breaks

        mixed list of mixed integer indices and break coordinates
        or ``None`` leader lines without breaks in it

    .. attribute:: index

        leader line index?

    .. attribute:: color

        leader line color override, ignore override value if BY_BLOCK_RAW_VALUE

.. class:: ArrowHeadData

    .. attribute:: index

        arrow head index?

    .. attribute:: handle

        handle to arrow head block

.. class:: AttribData

    .. attribute:: handle

        handle to :class:`Attdef` entity in the BLOCK definition

    .. attribute:: index

        unknown meaning

    .. attribute:: width

        text width factor?

    .. attribute:: text

        :class:`Attrib` content

.. class:: MTextData

    stores the content and attributes of the MTEXT entity

    .. attribute:: default_content

        content as string

    .. attribute:: extrusion

        extrusion vector of the MTEXT entity but MTEXT is not an OCS entity!

    .. attribute:: style_handle

        redundant data: :attr:`MultiLeader.dxf.text_style_handle`

    .. attribute:: insert

        insert location in WCS coordinates, same as
        :attr:`MLeaderContext.base_point`?

    .. attribute:: text_direction

        "horizontal" text direction vector in WCS

    .. attribute:: rotation

        rotation angle in radians (!) around the extrusion vector, calculated
        as it were an OCS entity

    .. attribute:: width

        unscaled column width

    .. attribute:: defined_height

        unscaled defined column height

    .. attribute:: line_spacing_factor

        see :attr:`MText.dxf.line_spacing_factor`

    .. attribute:: line_spacing_style

        see :attr:`MText.dxf.line_spacing_style`

    .. attribute:: color

        redundant data: :attr:`MultiLeader.dxf.text_color`

    .. attribute:: alignment

        redundant data: :attr:`MultiLeader.dxf.text_attachment_point`

    .. attribute:: flow_direction

        === ==================
        1   horizontal
        3   vertical
        6   by text style
        === ==================

    .. attribute:: bg_color

        background color as :term:`raw color` value

    .. attribute:: bg_scale_factor

        see :attr:`MText.dxf.box_fill_scale`

    .. attribute:: bg_transparency

        background transparency value

    .. attribute:: use_window_bg_color

    .. attribute:: has_bg_fill

    .. attribute:: column_type

        unknown meaning - most likely:

        === ========
        0   none
        1   static
        2   dynamic
        === ========

    .. attribute:: use_auto_height

    .. attribute:: column_width

        unscaled column width, redundant data :attr:`width`

    .. attribute:: column_gutter_width

        unscaled column gutter width

    .. attribute:: column_flow_reversed

    .. attribute:: column_sizes

        list of unscaled columns heights for dynamic column with manual heights

    .. attribute:: use_word_break

.. class:: BlockData

    stores the attributes for the :class:`Insert` entity

    .. attribute:: block_record_handle

        redundant data: :attr:`MultiLeader.dxf.block_record_handle`

    .. attribute:: extrusion

        extrusion vector in WCS

    .. attribute:: insert

        insertion location in WCS as :class:`Vec3`, same as
        :attr:`MLeaderContext.base_point`?

    .. attribute:: scale

        redundant data: :attr:`MultiLeader.dxf.block_scale_vector`

    .. attribute:: rotation

        redundant data: :attr:`MultiLeader.dxf.block_rotation`

    .. attribute:: color

        redundant data: :attr:`MultiLeader.dxf.block_color`

