DXF Graphic Entity Base Class
=============================

.. module:: ezdxf.entities
    :noindex:

Common base class for all graphical DXF entities.

This entities resides in entity spaces like :class:`~ezdxf.layouts.Modelspace`, any :class:`~ezdxf.layouts.Paperspace`
or :class:`~ezdxf.layouts.BlockLayout`.

============ =================================
Subclass of  :class:`ezdxf.entities.DXFEntity`
============ =================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: DXFGraphic

    .. attribute:: rgb

        Get/set DXF attribute :attr:`dxf.true_color` as ``(r, g, b)`` tuple, returns ``None`` if attribute
        :attr:`dxf.true_color` is not set.

        .. code-block:: python

            entity.rgb = (30, 40, 50)
            r, g, b = entity.rgb

        This is the recommend method to get/set RGB values, when ever possible do not use the DXF low level attribute
        :attr:`dxf.true_color`.


    .. attribute:: transparency

        Get/set transparency value as float. Value range ``0`` to ``1``, where ``0`` means entity is opaque and
        ``1`` means entity is 100% transparent (invisible). This is the recommend method to get/set transparency
        values, when ever possible do not use the DXF low level attribute :attr:`DXFGraphic.dxf.transparency`

        This attribute requires DXF R2004 or later, returns ``0`` for prior DXF versions
        and raises :class:`DXFAttributeError` for setting `transparency` in older DXF versions.

    .. attribute:: zorder

        Inverted :attr:`~ezdxf.entities.DXFEntity.priority` order (lowest value first), :attr:`zorder` support
        not implemented yet, setting :attr:`zorder` has no effect.

    .. automethod:: ocs() -> OCS

    .. automethod:: get_layout() -> BaseLayout

    .. automethod:: copy_to_layout(layout: BaseLayout) -> DXFEntity

    .. automethod:: move_to_layout(layout: BaseLayout, source: BaseLayout=None)

    .. automethod:: graphic_properties

.. _Common graphical DXF attributes:

Common graphical DXF attributes
-------------------------------

    .. attribute:: DXFGraphic.dxf.layer

        Layer name as string; default = ``'0'``

    .. attribute:: DXFGraphic.dxf.linetype

        Linetype as string, special names ``'BYLAYER'``, ``'BYBLOCK'``; default value is ``'BYLAYER'``

    .. attribute:: DXFGraphic.dxf.color

        :ref:`aci`,  default = ``256``

        Constants defined in :mod:`ezdxf.lldxf.const`

        === =========
        0   BYBLOCK
        256 BYLAYER
        257 BYOBJECT
        === =========

    .. attribute:: DXFGraphic.dxf.lineweight

        Line weight in mm times 100 (e.g. 0.13mm = 13). Smallest line weight is 13 and biggest line weight is 200, values
        outside this range prevents AutoCAD from loading the file. (requires DXF R2000)

        Constants defined in :mod:`ezdxf.lldxf.const`

        === ==================
        -1  LINEWEIGHT_BYLAYER
        -2  LINEWEIGHT_BYBLOCK
        -3  LINEWEIGHT_DEFAULT
        === ==================

    .. attribute:: DXFGraphic.dxf.ltscale

        Line type scale as float; default = ``1.0`` (requires DXF R2000)

    .. attribute:: DXFGraphic.dxf.invisible

        ``1`` for invisible, ``0`` for visible; default = ``0`` (requires DXF R2000)

    .. attribute:: DXFGraphic.dxf.paperspace

        ``0`` for entity resides in modelspace or a block, ``1`` for paperspace, this attribute is set automatically by
        adding an entity to a layout (feature for experts); default = ``0``

    .. attribute:: DXFGraphic.dxf.extrusion

        Extrusion direction as 3D vector; default = ``(0, 0, 1)``

    .. attribute:: DXFGraphic.dxf.thickness

        Entity thickness as float; default = ``0.0`` (requires DXF R2000)

    .. attribute:: DXFGraphic.dxf.true_color

        True color value as int ``0x00RRGGBB``, use :attr:`DXFGraphic.rgb` to get/set true color values as ``(r, g, b)``
        tuples. (requires DXF R2004)

    .. attribute:: DXFGraphic.dxf.color_name

        Color name as string. (requires DXF R2004)

    .. attribute:: DXFGraphic.dxf.transparency

        Transparency value as int, ``0x020000TT`` ``0x00`` = 100% transparent / ``0xFF`` = opaque, use
        :attr:`DXFGraphic.transparency` to get/set transparency as float value.

        (requires DXF R2004)

    .. attribute:: DXFGraphic.dxf.shadow_mode

        === ==========================
        0   casts and receives shadows
        1   casts shadows
        2   receives shadows
        3   ignores shadows
        === ==========================

        (requires DXF R2007)