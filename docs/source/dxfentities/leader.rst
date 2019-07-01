Leader
======

.. module:: ezdxf.entities

The LEADER entity (`DXF Reference`_) represents an arrow, made up of one or more vertices
(or spline fit points) and an arrowhead. The label or other content to which the :class:`Leader` is attached
is stored as a separate entity, and is not part of the :class:`Leader` itself.

:class:`Leader` shares its styling infrastructure with :class:`Dimension`.

By default a :class:`Leader` without any annotation is created. For creating more fancy leaders and annotations
see documentation provided by Autodesk or `Demystifying DXF: LEADER and MULTILEADER implementation notes <https://atlight.github.io/formats/dxf-leader.html>`_  .

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'LEADER'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_leader`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-396B2369-F89F-47D7-8223-8B7FB794F9F3

.. class:: Leader

    .. attribute:: dxf.dimstyle

        Name of :class:`Dimstyle` as string.

    .. attribute:: dxf.has_arrowhead

        == ============
        0  Disabled
        1  Enabled
        == ============

    .. attribute:: dxf.path_type

        Leader path type:

        == ==========================
        0  Straight line segments
        1  Spline
        == ==========================


    .. attribute:: dxf.annotation_type

        == ===========================================
        0  Created with text annotation
        1  Created with tolerance annotation
        2  Created with block reference annotation
        3  Created without any annotation (default)
        == ===========================================

    .. attribute:: dxf.hookline_direction

        Hook line direction flag:

        == =================================================================
        0  Hookline (or end of tangent for a splined leader) is the opposite direction from the horizontal vector
        1  Hookline (or end of tangent for a splined leader) is the same direction as horizontal vector (see ``has_hook_line``)
        == =================================================================

    .. attribute:: dxf.has_hookline

        == ==================
        0  No hookline
        1  Has a hookline
        == ==================

    .. attribute:: dxf.text_height

        Text annotation height in drawing units.

    .. attribute:: dxf.text_width

        Text annotation width.

    .. attribute:: dxf.block_color

        Color to use if leader's DIMCLRD = BYBLOCK

    .. attribute:: dxf.annotation_handle

        Hard reference (handle) to associated annotation (:class:`MText`, :class:`Tolerance`,
        or :class:`Insert` entity)

    .. attribute:: dxf.normal_vector

        Extrusion vector? default = ``(0, 0, 1)``.

    .. attribute:: .dxf.horizontal_direction

        `Horizontal` direction for leader, default = ``(1, 0, 0)``.

    .. attribute:: dxf.leader_offset_block_ref

        Offset of last leader vertex from block reference insertion point, default = ``(0, 0, 0)``.

    .. attribute:: dxf.leader_offset_annotation_placement

        Offset of last leader vertex from annotation placement point, default = ``(0, 0, 0)``.


    .. attribute:: vertices

        List of :class:`~ezdxf.math.Vector` objects, representing the vertices of the leader (3D Point in :ref:`WCS`).

    .. automethod:: Leader.set_vertices

