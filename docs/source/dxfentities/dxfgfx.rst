DXF Graphic Entity Base Class
=============================

.. module:: ezdxf.entities.dxfgfx

.. class:: DXFGraphic

    Common base class for all graphic entities, a subclass of :class:`~ezdxf.entities.dxfentity.DXFEntity`.

    .. attribute:: rgb

        (read/write) Get/Set true color as RGB-Tuple. This attribute does not exist in DXF AC1009 (R12) entities, the
        attribute exists in DXF AC1015 entities but does not work (raises ``DXFValueError``), requires at least DXF Version
        AC1018 (AutoCAD R2004). usage: :code:`entity.rgb = (30, 40, 50)`;

    .. attribute:: transparency

        (read/write) Get/Set transparency value as float. This attribute does not exist in DXF AC1009 (R12) entities, the
        attribute exists in DXF AC1015 entities but does not work (raises ``DXFValueError``), requires at least DXF Version
        AC1018 (AutoCAD R2004). Value range 0.0 to 1.0 where 0.0 means entity is opaque and 1.0 means entity is 100%
        transparent (invisible). This is the recommend method to get/set transparency values, when ever possible do not use
        the DXF low level attribute :attr:`entity.dxf.transparency`

    .. method:: copy_to_layout(layout)

        Duplicate entity and add new entity to *layout*.

    .. method:: move_to_layout(layout, source=None)

        Move entity from actual layout to *layout*. For DXF R12 providing *source* is faster, if the entity resides in a
        block layout, because ezdxf has to search in all block layouts, else *source* is not required.


    .. method:: get_layout()

        Returns the :class:`Layout` which contains this entity, `None` if entity is not assigned to any layout.

    .. method:: get_ocs()

        Returns an :class:`OCS` object, see also: :ref:`ocs`

.. _Common graphical DXF attributes for DXF R12:

Common graphical DXF Attributes for DXF R12
-------------------------------------------

    :ref:`Common DXF attributes for DXF R12`

    .. attribute:: DXFGraphic.dxf.layer

        layer name as string; default=0

    .. attribute:: DXFGraphic.dxf.linetype

        linetype as string, special names BYLAYER, BYBLOCK; default=BYLAYER

    .. attribute:: DXFGraphic.dxf.color

        dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER; default=256

        The color value represents an *ACI* (AutoCAD Color Index). AutoCAD and every other CAD application provides a
        default color table, but pen table would be the more correct term. Each ACI entry defines the color value, the line
        weight and some other attributes to use for the pen. This pen table can be edited by the user or loaded from an
        *.ctb* file.

        DXF R12 and prior are not good in preserving the layout of a drawing, because of the lack of a standard color table
        defined by the DXF reference and missing DXF structures to define these color tables in the DXF file. So if a CAD
        user redefined an ACI and do not provide a .ctb file, you have no ability to determine which color or lineweight
        was used. This is better in later DXF versions by providing additional DXF attributes like *lineweight*,
        *true_color* and *transparency*.

    .. attribute:: DXFGraphic.dxf.paperspace

        0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an entity to
        a layout (feature for experts), default value is ``0``

    .. attribute:: DXFGraphic.dxf.extrusion

        extrusion direction as 3D point, default value is ``(0, 0, 1)``


.. _Common graphical DXF attributes for DXF R13 or later:

Common graphical DXF Attributes for DXF R13 or later
----------------------------------------------------

    :ref:`Common DXF attributes for DXF R13 or later`

    .. attribute:: DXFGraphic.dxf.layer

        layer name as string; default = 0

    .. attribute:: DXFGraphic.dxf.linetype

        linetype as string, special names BYLAYER, BYBLOCK; default=BYLAYER

    .. attribute:: DXFGraphic.dxf.color

        dxf color index,  default = 256

        - 0 = BYBLOCK
        - 256 = BYLAYER
        - 257 = BYOBJECT

    .. attribute:: DXFGraphic.dxf.lineweight

        Line weight in mm times 100 (e.g. 0.13mm = 13). Smallest line weight is 13 and biggest line weight is 200, values
        outside this range prevents AutoCAD from loading the file.

        Constants defined in ezdxf.lldxf.const

        - LINEWEIGHT_BYLAYER = -1
        - LINEWEIGHT_BYBLOCK = -2
        - LINEWEIGHT_DEFAULT = -3


    .. attribute:: DXFGraphic.dxf.ltscale

        line type scale as float; default=1.0

    .. attribute:: DXFGraphic.dxf.invisible

        1 for invisible, 0 for visible; default=0

    .. attribute:: DXFGraphic.dxf.paperspace

        0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an entity to
        a layout (feature for experts); default=0

    .. attribute:: DXFGraphic.dxf.extrusion

        extrusion direction as 3D point; default=(0, 0, 1)

    .. attribute:: DXFGraphic.dxf.thickness

        entity thickness as float; default=0

    .. attribute:: DXFGraphic.dxf.true_color

        true color value as int 0x00RRGGBB, requires DXF Version AC1018 (AutoCAD R2004)

    .. attribute:: DXFGraphic.dxf.color_name

        color name as string (R2004)

    .. attribute:: DXFGraphic.dxf.transparency

        transparency value as int, 0x020000TT 0x00 = 100% transparent / 0xFF = opaque (R2004)

    .. attribute:: DXFGraphic.dxf.shadow_mode (R2007)

        - 0 = casts and receives shadows
        - 1 = casts shadows
        - 2 = receives shadows
        - 3 = ignores shadows
