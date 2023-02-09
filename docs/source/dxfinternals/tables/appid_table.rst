.. _appid_table_internals:

APPID Table
===========

The `APPID`_ table stores unique application identifiers. These identifiers are used to
mark sub-sections in the XDATA section of DXF entities. AutoCAD will not load DXF files
which uses AppIDs without an entry in the AppIDs table and the "ACAD" entry must always
exist.

Some known AppIDs:

=========================== =========== ===
APPID                       Used by     Description
=========================== =========== ===
ACAD                        Autodesk    various use cases
AcAecLayerStandard          Autodesk    layer description
AcCmTransparency            Autodesk    layer transparency
HATCHBACKGROUNDCOLOR        Autodesk    background color for pattern fillings
EZDXF                       ezdxf       meta data
=========================== =========== ===

.. seealso::

    - DXF Reference: `TABLES Section`_
    - DXF Reference: `APPID`_ Table
    - :class:`~ezdxf.entities.AppID` class

Table Structure DXF R12
-----------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< table type
    APPID
    70          <<< count of table entries, AutoCAD ignores this value
    3
    0           <<< 1. table entry
    APPID
    2           <<< unique application identifier
    ACAD
    70          <<< flags, see `APPID`_ reference
    0           <<< in common cases always 0
    0           <<< next table entry
    APPID
    ...
    0           <<< end of APPID table
    ENDTAB

Table Structure DXF R2000+
--------------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< table type
    APPID
    5           <<< table handle
    3
    330         <<< owner tag, tables have no owner
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of table entries, AutoCAD ignores this value
    3
    0           <<< first table entry
    APPID
    5           <<< handle of appid
    2A
    330         <<< owner handle, handle of APPID table
    3
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbRegAppTableRecord
    2           <<< unique application identifier
    ACAD
    70          <<< flags, see `APPID`_ reference
    0           <<< in common cases always 0
    0           <<< next table entry
    APPID
    ...
    0           <<< end of APPID table
    ENDTAB

Name References
---------------

APPID table entries are referenced by name:

    - XDATA section of DXF entities



.. _APPID: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-6E3140E9-E560-4C77-904E-480382F0553E

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F