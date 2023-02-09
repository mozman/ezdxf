.. _tables_section_internals:

TABLES Section
==============

The TABLES section contains the resource tables of a DXF document.

.. toctree::
    :maxdepth: 1

    ../tables/appid_table
    ../tables/block_record_table
    ../tables/dimstyle_table
    ../tables/layer_table
    ../tables/linetype_table
    ../tables/style_table
    ../tables/ucs_table
    ../tables/view_table
    ../tables/vport_table


The TABLES section of DXF R13 and later looks like this:

.. code-block:: none

    0
    SECTION
    2           <<< begin TABLES section
    TABLES
    0           <<< first TABLE
    TABLE
    2           <<< name of table "LTYPE"
    LTYPE
    5           <<< handle of the TABLE
    8
    330         <<< owner handle is always "0"
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of table entries
    4           <<< do not rely on this value!
    0           <<< first table entry
    LTYPE
    ...
    0           <<< second table entry
    LTYPE
    ...
    0           <<< end of TABLE
    ENDTAB
    0           <<< next TABLE
    TABLE
    2           <<< name of table "LAYER"
    LAYER
    5           <<< handle of the TABLE
    2
    330         <<< owner handle is always "0"
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of table entries
    1
    0           <<< first table entry
    LAYER
    ...
    0           <<< end of TABLE
    ENDTAB
    0           <<< end of SECTION
    ENDSEC

The TABLES section of DXF R12 and prior is a bit simpler and does not contain the
BLOCK_RECORD table. The handles in DXF R12 and prior are optional and only present if
the HEADER variable $HANDLING is 1.

.. code-block:: none

    0
    SECTION
    2           <<< begin TABLES section
    TABLES
    0           <<< first TABLE
    TABLE
    2           <<< name of table "LTYPE"
    LTYPE
    5           <<< optional handle of the TABLE
    8
    70          <<< count of table entries
    4
    0           <<< first table entry
    LTYPE
    ...
    0           <<< second table entry
    LTYPE
    ...
    0           <<< end of TABLE
    ENDTAB
    0           <<< next TABLE
    TABLE
    2           <<< name of table "LAYER"
    LAYER
    5           <<< optional handle of the TABLE
    2
    70          <<< count of table entries
    1
    0           <<< first table entry
    LAYER
    ...
    0           <<< end of TABLE
    ENDTAB
    0           <<< end of SECTION
    ENDSEC
