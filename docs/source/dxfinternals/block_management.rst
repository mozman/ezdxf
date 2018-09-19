.. _Block Management Structures:

Block Management Structures
===========================

A BLOCK is a kind of layout like the model space or a paper space, with the similarity that all these layouts
are containers for other graphical DXF entities. This block definition can be referenced in other layouts by the
INSERT entity. By using block references the same set of graphical entities can be located multiple times at
different layouts, this block references can be stretched and rotated without modifying the original entities. A
block is referenced only by its name defined by the DXF tag :code:`(2, name)`, there is a second DXF tag
:code:`(3, name2)` for the block name, which is not further documented by Autodesk, and I haven't tested what happens I
the second name is different to the first block name.

The :code:`(10, base_point)` tag (in BLOCK defines a insertion point of the block, by 'inserting' a block by
the INSERT entity, this point of the block is placed at the location defined by the :code:`(10, insert)` tag in
the INSERT entity, and it is also the base point for stretching and rotation.

A block definition can contain INSERT entities, and it is possible to create cyclic block definitions (a
BLOCK contains a INSERT of itself), but this should be avoided, CAD applications will not load the DXF file at all or
maybe just crash. This is also the case for all other kinds of cyclic definitions like: BLOCK 'A' -> INSERT BLOCK 'B'
and BLOCK 'B' -> INSERT BLOCK 'A'.


.. seealso::

    - ezdxf DXF Internals: :ref:`Blocks Section`
    - DXF Reference: `BLOCKS Section`_
    - DXF Reference: `BLOCK Entity`_
    - DXF Reference: `ENDBLK Entity`_
    - DXF Reference: `INSERT Entity`_

Block Names
-----------

Block names has to be unique and they are case insensitive ('Test' == 'TEST'). If there are two or more block
definitions with the same name, AutoCAD (LT 2018) merges these blocks into a single block with unpredictable properties
of all these blocks. In my test with two blocks, the final block has the name of the first block and the base-point of
the second block, and contains all entities of both blocks.

Block Definitions in DXF R12
----------------------------

In DXF R12 the definition of a block is located in the BLOCKS section, no additional structures are needed.
The definition starts with a BLOCK entity and ends with a ENDBLK entity. All entities between this
two entities are the content of the block, the block is the owner of this entities like any layout.

As shown in the DXF file below (created by AutoCAD LT 2018), the BLOCK entity has no handle, but ezdxf writes
also handles for the BLOCK entity and AutoCAD doesn't complain.

DXF R12 BLOCKS structure:

.. code-block:: none

    0           <<< start of a SECTION
    SECTION
    2           <<< start of BLOCKS section
    BLOCKS
    ...         <<< model space and paper space block definitions not shown,
    ...         <<< see layout management
    ...
    0           <<< start of a BLOCK definition
    BLOCK
    8           <<< layer, what this layer definition does is another fact, I don't know (now)
    0
    2           <<< block name
    ArchTick
    70          <<< flags
    1
    10          <<< base point, x
    0.0
    20          <<< base point, y
    0.0
    30          <<< base point, z
    0.0
    3           <<< second BLOCK name, same as (2, name)
    ArchTick
    1           <<< xref name, if block is an external reference
                <<< empty string!
    0           <<< start of the first entity of the BLOCK
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
    0           <<< start of the second entity of the BLOCK
    LINE
    ...
    0.0
    0           <<< ENDBLK entity, marks the end of the BLOCK definition
    ENDBLK
    5           <<< ENDBLK gets a handle by AutoCAD, but BLOCK didn't
    2F2
    8           <<< as every entity, also ENDBLK requires a layer (same as BLOCK entity!)
    0
    0           <<< start of next BLOCK entity
    BLOCK
    ...
    0           <<< end BLOCK entity
    ENDBLK
    0           <<< end of BLOCKS section
    ENDSEC

Block Definitions in DXF R2000 and later
----------------------------------------

The overall organization in the BLOCKS sections remains the same, but additional tags in the BLOCK entity, have to be
maintained.

Especially the concept of ownership is important. Since DXF R13 every graphic entity is associated to a specific layout,
and a BLOCK definition is a kind of layout. So all entities in the BLOCK definition, including the BLOCK and the ENDBLK
entities, have an owner tag :code:`(330, ...)`, which points to a BLOCK_RECORD entry in the BLOCK_RECORD table.
As you can see in the chapter about :ref:`Layout Management Structures`, this concept is also valid for model space
and paper space layouts, because these layouts are also BLOCKS, with the special difference, that entities of the model
space and the `active` paper space are stored in the ENTITIES section.

.. image:: gfx/block_definition.png
    :align: center

.. seealso::

    - :ref:`Tag Structure DXF R13 and later`
    - ezdxf DXF Internals: :ref:`Tables Section`
    - DXF Reference: `TABLES Section`_
    - DXF Reference: `BLOCK_RECORD Entity`_


DXF R13 BLOCKS structure:

.. code-block:: none

    0           <<< start of a SECTION
    SECTION
    2           <<< start of BLOCKS section
    BLOCKS
    ...         <<< model space and paper space block definitions not shown,
    ...         <<< see layout management
    0           <<< start of BLOCK definition
    BLOCK
    5           <<< even BLOCK gets a handle now ;)
    23A
    330         <<< owner tag, the owner of a BLOCK is a BLOCK_RECORD in the BLOCK_RECORD table
    238
    100         <<< subclass marker
    AcDbEntity
    8           <<< layer of the BLOCK definition
    0
    100         <<< subclass marker
    AcDbBlockBegin
    2           <<< BLOCK name
    ArchTick
    70          <<< flags
    0
    10          <<< base point, x
    0.0
    20          <<< base point, y
    0.0
    30          <<< base point, z
    0.0
    3           <<< second BLOCK name, same as (2, name)
    ArchTick
    1           <<< xref name, if block is an external reference
                <<< empty string!
    0           <<< start of the first entity of the BLOCK
    LWPOLYLINE
    5
    239
    330         <<< owner tag of LWPOLYLINE
    238         <<< handle of the BLOCK_RECORD!
    100
    AcDbEntity
    8
    0
    6
    ByBlock
    62
    0
    100
    AcDbPolyline
    90
    2
    70
    0
    43
    0.15
    10
    -0.5
    20
    -0.5
    10
    0.5
    20
    0.5
    0           <<< ENDBLK entity, marks the end of the BLOCK definition
    ENDBLK
    5           <<< handle
    23B
    330         <<< owner tag, same BLOCK_RECORD as for the BLOCK entity
    238
    100         <<< subclass marker
    AcDbEntity
    8           <<< as every entity, also ENDBLK requires a layer (same as BLOCK entity!)
    0
    100         <<< subclass marker
    AcDbBlockEnd
    0           <<< start of the next BLOCK
    BLOCK
    ...
    0
    ENDBLK
    ...
    0           <<< end of the BLOCKS section
    ENDSEC


DXF R13 BLOCK_RECORD structure:

.. code-block:: none

    0           <<< start of a SECTION
    SECTION
    2           <<< start of TABLES section
    TABLES
    0           <<< start of a TABLE
    TABLE
    2           <<< start of the BLOCK_RECORD table
    BLOCK_RECORD
    5           <<< handle of the table (INFO: ezdxf doesn't store tables in the entities database)
    1
    330         <<< owner tag of the table
    0           <<< is always #0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of table entries, not reliable
    4
    0           <<< start of first BLOCK_RECORD entry
    BLOCK_RECORD
    5           <<< handle of BLOCK_RECORD, in ezdxf often referred to as 'layout key'
    1F
    330         <<< owner of the BLOCK_RECORD is the BLOCK_RECORD table
    1
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbBlockTableRecord
    2           <<< name of the BLOCK or LAYOUT
    *Model_Space
    340         <<< pointer to the associated LAYOUT object
    4AF
    70          <<< AC1021 (R2007) block insertion units
    0
    280         <<< AC1021 (R2007) block explodability
    1
    281         <<< AC1021 (R2007) block scalability
    0

    ...         <<< paper space not shown
    ...
    0           <<< next BLOCK_RECORD
    BLOCK_RECORD
    5           <<< handle of BLOCK_RECORD, in ezdxf often referred to as 'layout key'
    238
    330         <<< owner of the BLOCK_RECORD is the BLOCK_RECORD table
    1
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbBlockTableRecord
    2           <<< name of the BLOCK
    ArchTick
    340         <<< pointer to the associated LAYOUT object
    0           <<< #0, because BLOCK doesn't have an associated LAYOUT object
    70          <<< AC1021 (R2007) block insertion units
    0
    280         <<< AC1021 (R2007) block explodability
    1
    281         <<< AC1021 (R2007) block scalability
    0
    0           <<< end of BLOCK_RECORD table
    ENDTAB
    0           <<< next TABLE
    TABLE
    ...
    0
    ENDTAB
    0           <<< end of TABLES section
    ENDESC

.. _BLOCKS Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-1D14A213-5E4D-4EA6-A6B5-8709EB925D01

.. _BLOCK Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-66D32572-005A-4E23-8B8B-8726E8C14302

.. _ENDBLK Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-27F7CC8A-E340-4C7F-A77F-5AF139AD502D

.. _INSERT Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-28FA4CFB-9D5E-4880-9F11-36C97578252F

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F

.. _BLOCK_RECORD Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A1FD1934-7EF5-4D35-A4B0-F8AE54A9A20A