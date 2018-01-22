.. _Linetype Table:

Linetype Table
==============

All tag structures for DXF R2000 and later.

Linetype Table
--------------

You have access to the line types table by the attribute :attr:`Drawing.linetypes`. The line type table itself is not
stored in the entity database, but the table entries are stored in entity database, and can be accessed by its handle.


.. seealso::

    - DXF Reference: `TABLES Section`_
    - DXF Reference: `LTYPE Entity`_

LTYPE Table Tag Structure
~~~~~~~~~~~~~~~~~~~~~~~~~

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

ezdxf setup for line type 'CENTER'::

    dwg.linetypes.new("CENTER", dxfattribs={
        description = "Center ____ _ ____ _ ____ _ ____ _ ____ _ ____",
        pattern=[2.0, 1.25, -0.25, 0.25, -0.25],
     })


Simple Tag Structure
~~~~~~~~~~~~~~~~~~~~

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
    72
    65
    73
    4
    40
    2.0
    49
    1.25
    74
    0
    49
    -0.25
    74
    0
    49
    0.25
    74
    0
    49
    -0.25
    74
    0

Complex Line Type TEXT
----------------------

ezdxf setup for line type 'GASLEITUNG'::

    dwg.linetypes.new('GASLEITUNG', dxfattribs={
        'description': 'Gasleitung2 ----GAS----GAS----GAS----GAS----GAS----GAS--',
        'length': 1,
        'pattern': 'A,.5,-.2,["GAS",STANDARD,S=.1,U=0.0,X=-0.1,Y=-.05],-.25',
    })

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
    72
    65
    73
    3
    40
    1
    49
    0.5
    74
    0
    49
    -0.2
    74
    2
    75
    0
    340
    11
    46
    0.1
    50
    0.0
    44
    -0.1
    45
    -0.05
    9
    GAS
    49
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
    72
    65
    73
    4
    40
    1.45
    49
    0.25
    74
    0
    49
    -0.1
    74
    4
    75
    132
    340
    616
    46
    0.1
    50
    0.0
    44
    -0.1
    45
    0.0
    49
    -0.1
    74
    0
    49
    1.0
    74
    0


.. _LTYPE Entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-F57A316C-94A2-416C-8280-191E34B182AC

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F