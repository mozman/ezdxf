Insert
======

.. module:: ezdxf.entities
    :noindex:

The INSERT entity (`DXF Reference`_) represents a block reference with optional
attached attributes as (:class:`Attrib`) entities.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'INSERT'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_blockref`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. seealso::

    :ref:`tut_blocks`

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!


.. class:: Insert

    .. attribute:: dxf.name

        BLOCK name (str)

    .. attribute:: dxf.insert

        Insertion location of the BLOCK base point as (2D/3D Point in :ref:`OCS`)

    .. attribute:: dxf.xscale

        Scale factor for x direction (float)

    .. attribute:: dxf.yscale

        Scale factor for y direction (float)

        Not all CAD applications support non-uniform scaling (e.g. LibreCAD).

    .. attribute:: dxf.zscale

        Scale factor for z direction (float)

        Not all CAD applications support non-uniform scaling (e.g. LibreCAD).

    .. attribute:: dxf.rotation

        Rotation angle in degrees (float)

    .. attribute:: dxf.row_count

        Count of repeated insertions in row direction, MINSERT entity if > 1 (int)

    .. attribute:: dxf.row_spacing

        Distance between two insert points (MINSERT) in row direction (float)

    .. attribute:: dxf.column_count

        Count of repeated insertions in column direction, MINSERT entity if > 1 (int)

    .. attribute:: dxf.column_spacing

        Distance between two insert points (MINSERT) in column direction (float)

    .. attribute:: attribs

        A list of all attached :class:`Attrib` entities.

    .. autoattribute:: has_scaling

    .. autoattribute:: has_uniform_scaling

    .. autoattribute:: mcount

    .. automethod:: set_scale

    .. automethod:: block

    .. automethod:: place

    .. automethod:: grid

    .. automethod:: has_attrib

    .. automethod:: get_attrib

    .. automethod:: get_attrib_text

    .. automethod:: add_attrib

    .. automethod:: add_auto_attribs

    .. automethod:: delete_attrib

    .. automethod:: delete_all_attribs

    .. automethod:: transform

    .. automethod:: translate

    .. automethod:: virtual_entities

    .. automethod:: multi_insert

    .. automethod:: explode

    .. automethod:: ucs

    .. automethod:: matrix44

    .. automethod:: reset_transformation



.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-28FA4CFB-9D5E-4880-9F11-36C97578252F