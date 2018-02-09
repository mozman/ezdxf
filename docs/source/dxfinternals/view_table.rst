.. _VIEW Table:

VIEW Table
==========

The `VIEW`_ entry stores a named view of the model or a paper space layout. This stored views makes parts of the
drawing or some view points of the model in a CAD applications more accessible. This views have no influence to the
drawing content or to the generated output by exporting PDFs or plotting on paper sheets, they are just for the
convenience of CAD application users.

Using *ezdxf* you have access to the views table by the attribute :attr:`Drawing.views`. The views table itself is
not stored in the entity database, but the table entries are stored in entity database, and can be accessed by its
handle.

DXF R12
-------

.. code-block:: none

    0
    VIEW
    2       <<< name of view
    VIEWNAME
    70      <<< flags bit-coded: 1st bit -> (0/1 = model space/paper space)
    0       <<< model space
    40      <<< view width in Display Coordinate System (DCS)
    20.01
    10      <<< view center point in DCS
    40.36   <<<     x value
    20      <<<     group code for y value
    15.86   <<<     y value
    41      <<< view height in DCS
    17.91
    11      <<< view direction from target point, 3D vector
    0.0     <<<     x value
    21      <<<     group code for y value
    0.0     <<<     y value
    31      <<<     group code for z value
    1.0     <<<     z value
    12      <<< target point in WCS
    0.0     <<<     x value
    22      <<<     group code for y value
    0.0     <<<     y value
    32      <<<     group code for z value
    0.0     <<<     z value
    42      <<< lens (focal) length
    50.0    <<< 50mm
    43      <<< front clipping plane, offset from target
    0.0
    44      <<< back clipping plane, offset from target
    0.0
    50      <<< twist angle
    0.0
    71      <<< view mode
    0

.. seealso::

    :ref:`Coordinate Systems`

DXF R2000+
----------

Mostly the same structure as DXF R12, but with handle, owner tag and subclass markers.

.. code-block:: none

    0       <<< adding the VIEW table head, just for information
    TABLE
    2       <<< table name
    VIEW
    5       <<< handle of table, see owner tag of VIEW table entry
    37C
    330     <<< owner tag of table, always #0
    0
    100     <<< subclass marker
    AcDbSymbolTable
    70      <<< VIEW table (max.) count, not reliable (ignore)
    9
    0       <<< first VIEW table entry
    VIEW
    5       <<< handle
    3EA
    330     <<< owner, the VIEW table is the owner of the VIEW entry
    37C     <<< handle of the VIEW table
    100     <<< subclass marker
    AcDbSymbolTableRecord
    100     <<< subclass marker
    AcDbViewTableRecord
    2       <<< view name, from here all the same as DXF R12
    VIEWNAME
    70
    0
    40
    20.01
    10
    40.36
    20
    15.86
    41
    17.91
    11
    0.0
    21
    0.0
    31
    1.0
    12
    0.0
    22
    0.0
    32
    0.0
    42
    50.0
    43
    0.0
    44
    0.0
    50
    0.0
    71
    0
    281     <<< render mode 0-6 (... too much options)
    0       <<< 0= 2D optimized (classic 2D)
    72      <<< UCS associated (0/1 = no/yes)
    0       <<< 0 = no

DXF R2000+ supports additional features in the VIEW entry, see the `VIEW`_ table reference provided by Autodesk.

.. _VIEW: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-CF3094AB-ECA9-43C1-8075-7791AC84F97C
