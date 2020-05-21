Insert
======

.. module:: ezdxf.entities
    :noindex:

Block reference (`DXF Reference`_) with maybe attached attributes (:class:`Attrib`).

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

TODO: influence of layer, linetype, color DXF attributes to block entities

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

        Count of repeated insertions in row direction (int)

    .. attribute:: dxf.row_spacing

        Distance between two insert points in row direction (float)

    .. attribute:: dxf.column_count

        Count of repeated insertions in column direction (int)

    .. attribute:: dxf.column_spacing

        Distance between two insert points in column direction (float)

    .. attribute:: attribs

        A ``list`` of all attached :class:`Attrib` entities.

    .. autoattribute:: has_scaling

    .. autoattribute:: has_uniform_scaling

    .. automethod:: set_scale

    .. automethod:: block

    .. automethod:: place

    .. automethod:: grid(size: Tuple[int, int] = (1, 1), spacing: Tuple[float, float] = (1, 1)) -> Insert

    .. automethod:: has_attrib

    .. automethod:: get_attrib

    .. automethod:: get_attrib_text

    .. automethod:: add_attrib

    .. automethod:: add_auto_attribs

    .. automethod:: delete_attrib

    .. automethod:: delete_all_attribs

    .. automethod:: reset_transformation

    .. automethod:: transform(m: Matrix44) -> Insert

    .. automethod:: translate(dx: float, dy: float, dz: float) -> Insert

    .. automethod:: virtual_entities(non_uniform_scaling = False, skipped_entity_callback: Callable[[DXFGraphic, str], None] = None) -> Iterable[DXFGraphic]

    .. automethod:: explode(target_layout: BaseLayout = None, non_uniform_scaling = False) -> EntityQuery



.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-28FA4CFB-9D5E-4880-9F11-36C97578252F