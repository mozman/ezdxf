Graphic Base Class
==================

.. class:: GraphicEntity

    Common base class for all graphic entities.

.. attribute:: GraphicEntity.dxf

    (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
    :code:`entity.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
    writeable.

.. attribute:: GraphicEntity.drawing

    (read only) Get the associated drawing.

.. attribute:: GraphicEntity.dxffactory

    (read only) Get the associated DXF factory. (feature for experts)

.. attribute:: GraphicEntity.rgb

    (read/write) Get/Set true color as RGB-Tuple. This attribute does not exist in DXF AC1009 (R12) entities, the
    attribute exists in DXF AC1015 entities but does not work (raises ``DXFValueError``), requires at least DXF Version
    AC1018 (AutoCAD R2004). usage: :code:`entity.rgb = (30, 40, 50)`;

.. attribute:: GraphicEntity.transparency

    (read/write) Get/Set transparency value as float. This attribute does not exist in DXF AC1009 (R12) entities, the
    attribute exists in DXF AC1015 entities but does not work (raises ``DXFValueError``), requires at least DXF Version
    AC1018 (AutoCAD R2004). Value range 0.0 to 1.0 where 0.0 means entity is opaque and 1.0 means entity is 100%
    transparent (invisible). This is the recommend method to get/set transparency values, when ever possible do not use
    the DXF low level attribute :attr:`entity.dxf.transparency`

.. method:: GraphicEntity.dxftype()

    Get the DXF type string, like ``LINE`` for the line entity.

.. method:: GraphicEntity.copy()

    Deep copy of DXFEntity with new handle and duplicated linked entities (VERTEX, ATTRIB, SEQEND).
    The new entity is not included in any layout space, so the owner tag is set to '0' for undefined owner/layout.

    Use :meth:`Layout.add_entity()` to add the duplicated entity to a layout, layout can be the model space, a paper
    space layout or a block layout.

    This is not a deep copy in the meaning of Python, because handle, link and owner is changed.

.. method:: GraphicEntity.copy_to_layout(layout)

    Duplicate entity and add new entity to *layout*.

.. method:: GraphicEntity.move_to_layout(layout, source=None)

    Move entity from actual layout to *layout*. For DXF R12 providing *source* is faster, if the entity resides in a
    block layout, because ezdxf has to search in all block layouts, else *source* is not required.

.. method:: GraphicEntity.get_dxf_attrib(key, default=DXFValueError)

    Get DXF attribute *key*, returns *default* if key doesn't exist, or raise
    ``DXFValueError`` if *default* is ``DXFValueError`` and no DXF default
    value is defined::

        layer = entity.get_dxf_attrib("layer")
        # same as
        layer = entity.dxf.layer

.. method:: GraphicEntity.set_dxf_attrib(key, value)

    Set DXF attribute *key* to *value*::

       entity.set_dxf_attrib("layer", "MyLayer")
       # same as
       entity.dxf.layer = "MyLayer"

.. method:: GraphicEntity.del_dxf_attrib(key)

    Delete/remove DXF attribute *key*. Raises :class:`AttributeError` if *key* isn't supported.

.. method:: GraphicEntity.dxf_attrib_exists(key)

    Returns *True* if DXF attrib *key* really exists else *False*. Raises :class:`AttributeError` if *key* isn't supported

.. method:: GraphicEntity.supported_dxf_attrib(key)

    Returns *True* if DXF attrib *key* is supported by this entity else *False*. Does not grant that attrib
    *key* really exists.

.. method:: GraphicEntity.valid_dxf_attrib_names(key)

    Returns a list of supported DXF attribute names.

.. method:: GraphicEntity.dxfattribs()

    Create a dict() with all accessible DXF attributes and their value, not all data is accessible by dxf attributes like
    definition points of :class:`LWPolyline` or :class:`Spline`

.. method:: GraphicEntity.update_attribs(dxfattribs)

    Set DXF attributes by a dict() like :code:`{'layer': 'test', 'color': 4}`.

.. method:: GraphicEntity.set_flag_state(flag, state=True, name='flags')

    Set binary coded `flag` of DXF attribute `name` to 1 (on) if `state` is True, set `flag` to 0 (off) if `state`
    is False.

.. method:: GraphicEntity.get_flag_state(flag, name='flags')

    Returns True if any `flag` of DXF attribute is 1 (on), else False. Always check just one flag state at the time.

.. method:: GraphicEntity.get_layout()

    Returns the :class:`Layout` which contains this entity, `None` if entity is not assigned to any layout.

.. method:: GraphicEntity.get_ocs()

    Returns an :class:`OCS` object, see also: :ref:`ocs`

.. _Common DXF attributes for DXF R12:

Common DXF Attributes for DXF R12
---------------------------------

.. attribute:: GraphicEntity.dxf.handle

    DXF handle (feature for experts)

.. attribute:: GraphicEntity.dxf.layer

    layer name as string; default=0

.. attribute:: GraphicEntity.dxf.linetype

    linetype as string, special names BYLAYER, BYBLOCK; default=BYLAYER

.. attribute:: GraphicEntity.dxf.color

    dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER; default=256

.. attribute:: GraphicEntity.dxf.paperspace

    0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an entity to
    a layout (feature for experts); default=0

.. attribute:: GraphicEntity.dxf.extrusion

    extrusion direction as 3D point; default=(0, 0, 1)


.. _Common DXF attributes for DXF R13 or later:

Common DXF Attributes for DXF R13 or later
------------------------------------------

.. attribute:: GraphicEntity.dxf.handle

    DXF handle (feature for experts)

.. attribute:: GraphicEntity.dxf.owner

    handle to owner, it's a BLOCK_RECORD entry (feature for experts)

.. attribute:: GraphicEntity.dxf.layer

    layer name as string; default = 0

.. attribute:: GraphicEntity.dxf.linetype

    linetype as string, special names BYLAYER, BYBLOCK; default=BYLAYER

.. attribute:: GraphicEntity.dxf.color

    dxf color index,  default = 256

    - 0 = BYBLOCK
    - 256 = BYLAYER
    - 257 = BYOBJECT

.. attribute:: GraphicEntity.dxf.lineweight

    Line weight in mm times 100 (e.g. 0.13mm = 13). Smallest line weight is 13 and biggest line weight is 200, values
    outside this range prevents AutoCAD from loading the file.

    Constants defined in ezdxf.lldxf.const

    - LINEWEIGHT_BYLAYER = -1
    - LINEWEIGHT_BYBLOCK = -2
    - LINEWEIGHT_DEFAULT = -3


.. attribute:: GraphicEntity.dxf.ltscale

    line type scale as float; default=1.0

.. attribute:: GraphicEntity.dxf.invisible

    1 for invisible, 0 for visible; default=0

.. attribute:: GraphicEntity.dxf.paperspace

    0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an entity to
    a layout (feature for experts); default=0

.. attribute:: GraphicEntity.dxf.extrusion

    extrusion direction as 3D point; default=(0, 0, 1)

.. attribute:: GraphicEntity.dxf.thickness

    entity thickness as float; default=0

.. attribute:: GraphicEntity.dxf.true_color

    true color value as int 0x00RRGGBB, requires DXF Version AC1018 (AutoCAD R2004)

.. attribute:: GraphicEntity.dxf.color_name

    color name as string (R2004)

.. attribute:: GraphicEntity.dxf.transparency

    transparency value as int, 0x020000TT 0x00 = 100% transparent / 0xFF = opaque (R2004)

.. attribute:: GraphicEntity.dxf.shadow_mode (R2007)

    - 0 = casts and receives shadows
    - 1 = casts shadows
    - 2 = receives shadows
    - 3 = ignores shadows
