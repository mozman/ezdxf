.. _Header Section:

HEADER Section
==============

Documentation to ezdxf :class:`HeaderSection` class.

In DXF R12 an prior the HEADER section was optional, but since DXF R13 the HEADER section is mandatory. The overall
structure is:

.. code-block:: none

    0           <<< Begin HEADER section
    SECTION
    2
    HEADER
    9
    $ACADVER    <<< Header variable items go here
    1
    AC1009
    ...
    0
    ENDSEC      <<< End HEADER section

A header variable has a name defined by a :code:`(9, Name)` tag and following value tags.


.. seealso::

    DXF Reference: `Header Variables`_


.. _Header Variables: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A85E8E67-27CD-4C59-BE61-4DC9FADBE74A