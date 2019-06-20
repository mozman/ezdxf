Leader
======

.. class:: Leader(GraphicEntity)

Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is LEADER.

The :class:`Leader` entity represents an arrow, made up of one or more vertices (or spline fit points) and an
arrowhead. The label or other content to which the :class:`Leader` is attached is stored as a separate entity,
and is not part of the :class:`Leader` itself.

:class:`Leader` shares its styling infrastructure with :class:`Dimension`.

By default a :class:`Leader` without any annotation is created. For creating more fancy leaders and annotations
see documentation provided by Autodesk or `Demystifying DXF: LEADER and MULTILEADER implementation notes <https://atlight.github.io/formats/dxf-leader.html>`_  .

Create leader in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_leader`.

:attr:`Ellipse.dxf.extrusion` is supported, but does not establish an :ref:`OCS`, it is used to create an 3D entity by
extruding the base ellipse.


DXF Attributes for Ellipse
--------------------------

:ref:`Common graphical DXF attributes`

.. attribute:: Leader.dxf.dimstyle

    Name of :class:`Dimstyle` as string.

.. attribute:: Leader.dxf.has_arrowhead

    == ============
    0  Disabled
    1  Enabled
    == ============

.. attribute:: Leader.dxf.path_type

    Leader path type:

    == ==========================
    0  Straight line segments
    1  Spline
    == ==========================


.. attribute:: Leader.dxf.annotation_type

    == ===========================================
    0  Created with text annotation
    1  Created with tolerance annotation
    2  Created with block reference annotation
    3  Created without any annotation (default)
    == ===========================================

.. attribute:: Leader.dxf.hookline_direction

    Hook line direction flag:

    == =================================================================
    0  Hookline (or end of tangent for a splined leader) is the opposite direction from the horizontal vector
    1  Hookline (or end of tangent for a splined leader) is the same direction as horizontal vector (see ``has_hook_line``)
    == =================================================================

.. attribute:: Leader.dxf.has_hookline

    == ==================
    0  No hookline
    1  Has a hookline
    == ==================

.. attribute:: Leader.dxf.text_height

    Text annotation height.

.. attribute:: Leader.dxf.text_width

    Text annotation width.

.. attribute:: Leader.dxf.block_color

    Color to use if leader's DIMCLRD = BYBLOCK

.. attribute:: Leader.dxf.annotation_handle

    Hard reference (handle) to associated annotation (:class:`MText`, :class:`Tolerance`,
    or :class:`Insert` entity)

.. attribute:: Leader.dxf.normal_vector

    Default: (0, 0, 1)

.. attribute:: Leader.dxf.horizontal_direction

    "Horizontal" direction for leader, Default: (1, 0, 0)

.. attribute:: Leader.dxf.leader_offset_block_ref

    Offset of last leader vertex from block reference insertion point, Default: (0, 0, 0)

.. attribute:: Leader.dxf.leader_offset_annotation_placement

    Offset of last leader vertex from annotation placement point, Default: (0, 0, 0)


Leader Attributes
-----------------

.. attribute:: Leader.vertices

    List of :class:`~ezdxf.math.Vector` objects, representing the vertices of the leader (3D Point in :ref:`WCS`).

Leader Methods
--------------

.. method:: Leader.set_vertices(vertices)

    Set vertices of the leader, vertices is an iterable of (x, y [,z]) tuples or :class:`~ezdxf.math.Vector`.
