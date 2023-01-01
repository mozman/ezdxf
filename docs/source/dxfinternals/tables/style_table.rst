.. _style_table_internals:

STYLE Table
===========

The `STYLE`_ table stores all text styles and shape-file definitions. The "STANDARD"
entry must always exist.

Shape-files are also defined by a STYLE table entry, the bit 0 of the flags-tag is
set to 1 and the name-tag is an empty string, the only important data is the font-tag
with group code 3 which stores the associated SHX font file.

.. seealso::

    - DXF Reference: `TABLES Section`_
    - DXF Reference: `STYLE`_ Table
    - :class:`~ezdxf.entities.Textstyle` class


Table Structure DXF R12
-----------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< table type
    STYLE
    70           <<< count of table entries, AutoCAD ignores this value
    1
    0           <<< first table entry
    STYLE
    2           <<< text style name
    Standard
    70          <<< flags, see `STYLE`_ reference
    0
    40          <<< fixed text height; 0 if not fixed
    0.0
    41          <<< width factor
    1.0
    50          <<< oblique angle
    0.0
    71          <<< text generation flags; 2=backwards (mirror-x), 4=upside down (mirror-y)
    0
    42          <<< last height used
    2.5
    3           <<< font file name; SHX or TTF file name
    txt
    4           <<< big font name; SHX file with unicode symbols; empty if none

    0           <<< next text style
    STYLE
    ...
    0           <<< end of STYLE table
    ENDTAB


Table Structure DXF R2000+
--------------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< table type
    STYLE
    5           <<< table handle
    5
    330         <<< owner tag, tables have no owner
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70           <<< count of table entries, AutoCAD ignores this value
    1
    0           <<< first table entry
    STYLE
    5           <<< handle of text style
    29
    330         <<< owner handle, handle of STYLE table
    5
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbTextStyleTableRecord
    2           <<< text style name
    Standard
    70          <<< flags, see `STYLE`_ reference
    0
    40          <<< fixed text height; 0 if not fixed
    0.0
    41          <<< width factor
    1.0
    50          <<< oblique angle
    0.0
    71          <<< text generation flags; 2=backwards (mirror-x), 4=upside down (mirror-y)
    0
    42          <<< last height used
    2.5
    3           <<< font file name; SHX or TTF file name
    txt
    4           <<< big font name; SHX file with unicode symbols; empty if none

    0           <<< next text style
    STYLE
    ...
    0           <<< end of STYLE table
    ENDTAB

Extended Font Data
------------------

Additional information of the font-family, italic and bold style flags are stored in the
XDATA section of the STYLE entity by the APPID "ACAD":

.. code-block:: none

    0
    STYLE
    ...
    3
    Arial.ttf
    4

    1001        <<< start of the XDATA section
    ACAD        <<< APPID
    1000        <<< font family name
    Arial
    1071        <<< style flags, see table below
    50331682

======= =========== =========
Flag    dec         hex
======= =========== =========
ITALIC  16777216    0x1000000
BOLD    33554432    0x2000000
======= =========== =========

Name References
---------------

STYLE table entries are referenced by name:

    - TEXT entity
    - MTEXT entity
    - DIMSTYLE table entry
    - DIMSTYLE override



.. _STYLE: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-EF68AF7C-13EF-45A1-8175-ED6CE66C8FC9

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F