.. _Block Management Structures:

Block Management Structures
===========================

A :class:`Block` is a kind of layout like the model space or a paper space, with the similarity that all these layouts
are containers for other graphical DXF entities. This block definition can be referenced in other layouts by the
:class:`Insert` entity. By using block references the same set of graphical entities can be located multiple times at
different layouts, this block references can be stretched and rotated without modifying the original entities. A
block is referenced only by its name defined by the DXF tag :code:`(2, name)`, there is a second DXF tag
:code:`(3, name2)` for the block name, which is not further documented by Autodesk, and I haven't tested what happens I
the second name is different to the first block name.

The :code:`(10, base_point)` tag (in :class:`Block`) defines a insertion point of the block, by 'inserting' a block by
the :class:`Insert` entity, this point of the block is placed at the location defined by the :code:`(10, insert)` tag in
the :class:`Insert` entity, and it is also the base point for stretching and rotation.

A block defintion can contain :class:`Insert` entities, and it is possible to create recursive block definitions (a
BLOCK contains a INSERT of itself), but this should be avoided, CAD applications will not load the DXF file at all or
maybe just crash. This is also the case for all other kinds of recursive definitions like: BLOCK 'A' -> INSERT BLOCK 'B'
and BLOCK 'B' -> INSERT BLOCK 'A'.


Further information:

    - ezdxf DXF Internals: :ref:`Blocks Section`
    - Autodesk: `Blocks Section`_
    - Autodesk: `BLOCK Entity`_
    - Autodesk: `ENDBLK Entity`_
    - Autodesk: `INSERT Entity`_

Block Definitions in DXF R12
----------------------------

In DXF R12 the definition of a block is located in the BLOCKS section, no additional structures are needed.
The definition starts with a :class:`Block` entity and ends with a :class:`BlkEnd` entity. All entities between this
two entities are the content of the block, the block is the owner of this entities like any layout.

As shown in the DXF file below (created by AutoCAD LT 2018), the :class:`Block` entity has no handle, but ezdxf writes
also handles for the :class:`Block` entity and AutoCAD doesn't complain.

DXF R12 tag structure::

    0           <<< start of a section
    SECTION
    2           <<< start of the blocks section
    BLOCKS
    ...         <<< model space and paper space block definitions not shown,
    ...         <<< see layout management
    ...
    0           <<< start of a block definition
    BLOCK
    8           <<< layer, what this layer definition does is another fact, I don't know (now)
    0
    2           <<< block name
    Blockname
    70          <<< flags
    1
    10          <<< base point, x
    0.0
    20          <<< base point, y
    0.0
    30          <<< base point, z
    0.0
    3           <<< second block name, same as (2, name)
    Blockname
    1           <<< xref name, if block is a external reference
                <<< empty string!
    0           <<< start of the first entity of the block
    LINE
    5
    28E
    8
    0
    62
    0
    10
    500.0
    20
    500.0
    30
    0.0
    11
    500.0
    21
    511.0
    31
    0.0
    0           <<< start of the second entity of the block
    LINE
    ...
    0.0
    0           <<< end block entity
    ENDBLK
    5           <<< ENDBLK gets a handle by AutoCAD, but BLOCK didn't
    2F2
    8           <<< as every entity, also end block requires a layer (same as BLOCK entity!)
    0
    0           <<< next block starts with a block entity
    BLOCK
    ...

    0           <<< end of block section
    ENDSEC

Block Definitions in DXF R2000 and later
----------------------------------------


Tag (330, ...): (Autodesk says: Soft-pointer ID/handle to owner BLOCK_RECORD object)

I call this tag 'owner' tag. Every graphic entity is associated to a specific layout,
a layout can be the model space, a paper space or a block definition.

The owner tag is the link from the DXF entity to the associated layout.

The owner tag is the handle of the block record entry of the layout.

A layout consists of a BLOCK definition (e. g. \*Model_Space) in the BLOCKS section
and a LAYOUT entry in the OBJECTS section.

Every BLOCK definition requires also a BLOCK_RECORD entry in the BLOCK_RECORDS
table in the TABLES section.

The handle (5, ...) of the BLOCK_RECORD is the owner tag for all entities in that layout.
I call this value also layout key in the context of layouts and owner tag in the context of DXF entities.

.. _Blocks Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-1D14A213-5E4D-4EA6-A6B5-8709EB925D01

.. _BLOCK Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-66D32572-005A-4E23-8B8B-8726E8C14302

.. _ENDBLK Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-27F7CC8A-E340-4C7F-A77F-5AF139AD502D

.. _INSERT Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-28FA4CFB-9D5E-4880-9F11-36C97578252F