.. _ltype_table_internals:

LTYPE Table
===========

The `LTYPE`_ table stores all line type definitions of a DXF drawing. Every line type
used in the drawing has to have a table entry, or the DXF drawing is invalid for AutoCAD.

DXF R12 supports just simple line types, DXF R2000+ supports also complex line types with
text or shapes included.

You have access to the line types table by the attribute :attr:`Drawing.linetypes`.
The line type table itself is not stored in the entity database, but the table entries
are stored in entity database, and can be accessed by its handle.


.. seealso::

    - DXF Reference: `TABLES Section`_
    - DXF Reference: `LTYPE`_ Table

Table Structure DXF R12
-----------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< set table type
    LTYPE
    70          <<< count of line types defined in this table, AutoCAD ignores this value
    9
    0           <<< 1. LTYPE table entry
    LTYPE
                <<< LTYPE data tags
    0           <<< 2. LTYPE table entry
    LTYPE
                <<< LTYPE data tags and so on
    0           <<< end of LTYPE table
    ENDTAB


Table Structure DXF R2000+
--------------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< set table type
    LTYPE
    5           <<< LTYPE table handle
    5F
    330         <<< owner tag, tables has no owner
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of line types defined in this table, AutoCAD ignores this value
    9
    0           <<< 1. LTYPE table entry
    LTYPE
                <<< LTYPE data tags
    0           <<< 2. LTYPE table entry
    LTYPE
                <<< LTYPE data tags and so on
    0           <<< end of LTYPE table
    ENDTAB


Simple Line Type
----------------

`ezdxf` setup for line type "CENTER":

.. code-block:: python

    dwg.linetypes.add("CENTER",
        description="Center ____ _ ____ _ ____ _ ____ _ ____ _ ____",
        pattern=[2.0, 1.25, -0.25, 0.25, -0.25],
    )


Simple Line Type Tag Structure DXF R2000+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    0           <<< line type table entry
    LTYPE
    5           <<< handle of line type
    1B1
    330         <<< owner handle, handle of LTYPE table
    5F
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbLinetypeTableRecord
    2           <<< line type name
    CENTER
    70          <<< flags
    0
    3
    Center ____ _ ____ _ ____ _ ____ _ ____ _ ____
    72          <<<< signature tag
    65          <<<< ascii code for "A"
    73          <<<< count of pattern groups starting with a code 49 tag
    4           <<<< 4 pattern groups
    40          <<<< overall pattern length in drawing units
    2.0
    49          <<<< 1. pattern group
    1.25        <<<< >0 line, <0 gap, =0 point
    74          <<<< type marker
    0           <<<< 0 for line group
    49          <<<< 2. pattern group
    -0.25
    74
    0
    49          <<<< 3. pattern group
    0.25
    74
    0
    49          <<<< 4. pattern group
    -0.25
    74
    0

Complex Line Type TEXT
----------------------

`ezdxf` setup for line type "GASLEITUNG":

.. code-block:: python

    dwg.linetypes.add("GASLEITUNG",
        description="Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--",
        length=1,
        pattern='A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
    )

TEXT Tag Structure
~~~~~~~~~~~~~~~~~~

.. code-block:: none

    0
    LTYPE
    5
    614
    330
    5F
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbLinetypeTableRecord
    2
    GASLEITUNG
    70
    0
    3
    Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--
    72          <<<< signature tag
    65          <<<< ascii code for "A"
    73          <<<< count of pattern groups starting with a code 49 tag
    3           <<<< 3 pattern groups
    40          <<<< overall pattern length in drawing units
    1
    49          <<<< 1. pattern group
    0.5         <<<< >0 line, <0 gap, =0 point
    74          <<<< type marker
    0           <<<< 0 for line group
    49          <<<< 2. pattern group
    -0.2
    74          <<<< type marker
    2           <<<< 2 for text group
    75          <<<< shape number in shape-file
    0           <<<< always 0 for text group
    340         <<<< handle to text style "STANDARD"
    11
    46          <<<< scaling factor: "s" in pattern definition
    0.1
    50          <<<< rotation angle: "r" and "u" in pattern definition
    0.0
    44          <<<< shift x units: "x" in pattern definition = parallel to line direction
    -0.1
    45          <<<< shift y units: "y" in pattern definition = normal to line direction
    -0.05
    9           <<<< text
    GAS
    49          <<<< 3. pattern group
    -0.25
    74
    0

Complex Line Type SHAPE
-----------------------

ezdxf setup for line type 'GRENZE2'::

    dwg.linetypes.new('GRENZE2', dxfattribs={
        'description': 'Grenze eckig ----[]-----[]----[]-----[]----[]--',
        'length': 1.45,
        'pattern': 'A,.25,-.1,[132,ltypeshp.shx,x=-.1,s=.1],-.1,1',
    })

SHAPE Tag Structure
~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    0
    LTYPE
    5
    615
    330
    5F
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbLinetypeTableRecord
    2
    GRENZE2
    70
    0
    3
    Grenze eckig ----[]-----[]----[]-----[]----[]--
    72          <<<< signature tag
    65          <<<< ascii code for "A"
    73          <<<< count of pattern groups starting with a code 49 tag
    4           <<<< 4 pattern groups
    40          <<<< overall pattern length in drawing units
    1.45
    49          <<<< 1. pattern group
    0.25        <<<< >0 line, <0 gap, =0 point
    74          <<<< type marker
    0           <<<< 0 for line group
    49          <<<< 2. pattern group
    -0.1
    74          <<<< type marker
    4           <<<< 4 for shape group
    75          <<<< shape number in shape-file
    132
    340         <<<< handle to shape-file entry "ltypeshp.shx"
    616
    46          <<<< scaling factor: "s" in pattern definition
    0.1
    50          <<<< rotation angle: "r" and "u" in pattern definition
    0.0
    44          <<<< shift x units: "x" in pattern definition = parallel to line direction
    -0.1
    45          <<<< shift y units: "y" in pattern definition = normal to line direction
    0.0
    49          <<<< 3. pattern group
    -0.1
    74
    0
    49          <<<< 4. pattern group
    1.0
    74
    0


.. _LTYPE: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-F57A316C-94A2-416C-8280-191E34B182AC

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F