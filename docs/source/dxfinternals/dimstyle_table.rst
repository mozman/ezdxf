.. _DIMSTYLE Table:

DIMSTYLE Table
==============

The `DIMSTYLE`_ table stores all dimension style definitions of a DXF drawing.

You have access to the dimension styles table by the attribute :attr:`Drawing.dimstyles`.


.. seealso::

    - DXF Reference: `TABLES Section`_
    - DXF Reference: `DIMSTYLE`_ Table

Table Structure DXF R12
-----------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< set table type
    DIMSTYLE
    70          <<< count of line types defined in this table, AutoCAD ignores this value
    9
    0           <<< 1. DIMSTYLE table entry
    DIMSTYLE
                <<< DIMSTYLE data tags
    0           <<< 2. DIMSTYLE table entry
    DIMSTYLE
                <<< DIMSTYLE data tags and so on
    0           <<< end of DIMSTYLE table
    ENDTAB


DIMSTYLE Entry DXF R12
----------------------

.. image:: gfx/dimstyleR12_variables.svg
    :align: center
    :width: 800px

Table Structure DXF R2000+
--------------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< set table type
    DIMSTYLE
    5           <<< DIMSTYLE table handle
    5F
    330         <<< owner tag, tables has no owner
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of dimension styles defined in this table, AutoCAD ignores this value
    9
    0           <<< 1. DIMSTYLE table entry
    DIMSTYLE
                <<< DIMSTYLE data tags
    0           <<< 2. DIMSTYLE table entry
    DIMSTYLE
                <<< DIMSTYLE data tags and so on
    0           <<< end of DIMSTYLE table
    ENDTAB


DIMSTYLE Entry DXF R2000+
-------------------------


.. _DIMSTYLE: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-F2FAD36F-0CE3-4943-9DAD-A9BCD2AE81DA

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F