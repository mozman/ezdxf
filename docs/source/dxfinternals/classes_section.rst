.. _Classes Section:

CLASSES Section
===============

The CLASSES section contains CLASS definitions which are only important for Autodesk products, some DXF entities require
a class definition or AutoCAD will not open the DXF file.

The CLASSES sections was introduced with DXF AC1015 (AutoCAD Release R13).

DXF Reference: `About the DXF CLASSES Section`_

The CLASSES section in DXF files holds the information for application-defined classes whose instances appear in
the BLOCKS, ENTITIES, and OBJECTS sections of the database. It is assumed that a class definition is permanently
fixed in the class hierarchy. All fields are required.

CLASS Entities
--------------

DXF Reference: `Group Codes for the CLASS entity`_

CLASS entities have no handle and therefor ezdxf does not store the CLASS entity in the drawing entities database!

.. code-block:: none

    0
    SECTION
    2           <<< begin CLASSES section
    CLASSES
    0           <<< first CLASS entity
    CLASS
    1           <<< class DXF entity name; always unique
    ACDBDICTIONARYWDFLT
    2           <<< C++ class name; always unique
    AcDbDictionaryWithDefault
    3           <<< application name
    ObjectDBX Classes
    90          <<< proxy capabilities flags
    0
    91          <<< instance counter for custom class, since DXF version AC1018 (R2004)
    0           <<< no problem if the counter is wrong, AutoCAD doesn't care about
    280         <<< was-a-proxy flag. Set to 1 if class was not loaded when this DXF file was created, and 0 otherwise
    0
    281         <<< is-an-entity flag. Set to 1 if class reside in the BLOCKS or ENTITIES section. If 0, instances may appear only in the OBJECTS section
    0
    0           <<< second CLASS entity
    CLASS
    ...
    ...
    0           <<< end of CLASSES section
    ENDSEC


.. _About the DXF CLASSES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-6160F1F1-2805-4C69-8077-CA1AEB6B1005

.. _Group Codes for the CLASS entity: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-DBD5351C-E408-4CED-9336-3BD489179EF5