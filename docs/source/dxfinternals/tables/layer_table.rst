.. _layer_table_internals:

LAYER Table
===========

TODO

.. seealso::

    - DXF Reference: `TABLES Section`_
    - DXF Reference: `LAYER`_ Table
    - :class:`~ezdxf.entities.Layer` class

Table Structure DXF R2000+
--------------------------

.. code-block:: none

    0           <<< start of table
    TABLE
    2           <<< name of table "LAYER"
    LAYER
    5           <<< handle of the TABLE
    2
    330         <<< owner tag is always "0"
    0
    100         <<< subclass marker
    AcDbSymbolTable
    70          <<< count of layers defined in this table, AutoCAD ignores this value
    5
    0           <<< 1. LAYER table entry
    LAYER
    ...         <<< LAYER entity tags
    0           <<< 2. LAYER table entry
    LAYER
    ...         <<< LAYER entity tags
    0           <<< end of TABLE
    ENDTAB

Layer Entity Tags DXF R2000+
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are some quirks:

    - the frozen/thawed state is stored in flags (group code 70)
    - the locked/unlocked state is stored in flags (group code 70)
    - the off state is stored as negative color value (group code 6)
    - the layer description is stored in the XDATA section
    - the transparency value is stored in the XDATA section

.. code-block:: none

    0           <<< LAYER table entry
    LAYER
    5           <<< handle of LAYER
    10
    330         <<< owner handle, handle of LAYER table
    2
    100         <<< subclass marker
    AcDbSymbolTableRecord
    100         <<< subclass marker
    AcDbLayerTableRecord
    2           <<< layer name
    0           <<< layer "0"
    70          <<< flags
    0
    62          <<< color
    7           <<< a negative value switches the layer off
    420         <<< optional true color value
    0
    6           <<< linetype
    Continuous
    290         <<< optional plot flag
    1
    370         <<< lineweight
    -3
    390         <<< handle to plot style
    F
    347         <<< material handle
    47
    348         <<< unknown1
    0
    1001        <<< XDATA section, APPID
    AcAecLayerStandard
    1000        <<< unknown first value, here an empty string

    1000        <<< layer description
    This layer has a description
    1001        <<< APPID
    AcCmTransparency
    1071        <<< layer transparency value
    0

Layer Viewport Overrides
~~~~~~~~~~~~~~~~~~~~~~~~

Some layer attributes can be overridden individually for any VIEWPORT
entity. This overrides are stored as extension dictionary entries of
the LAYER entity pointing to XRECORD entities in the objects section:

.. code-block:: none

    0
    LAYER
    5
    9F
    102         <<< APP data, extension dictionary
    {ACAD_XDICTIONARY
    360         <<< handle to the xdict in the objects section
    B3
    102
    }
    330
    2
    100
    AcDbSymbolTableRecord
    100
    AcDbLayerTableRecord
    2
    LayerA
    ...

The extension DICTIONARY entity:

.. code-block:: none

    0           <<< entity type
    DICTIONARY
    5           <<< handle
    B3
    330         <<< owner handle
    9F          <<< the layer owns this dictionary
    100         <<< subclass marker
    AcDbDictionary
    280         <<< hard owned flag
    1
    281         <<< cloning type
    1           <<< keep existing
    3           <<< transparency override
    ADSK_XREC_LAYER_ALPHA_OVR
    360         <<< handle to XRECORD
    E5
    3           <<< color override
    ADSK_XREC_LAYER_COLOR_OVR
    360         <<< handle to XRECORD
    B4
    3           <<< linetype override
    ADSK_XREC_LAYER_LINETYPE_OVR
    360         <<< handle to XRECORD
    DD
    3           <<< lineweight override
    ADSK_XREC_LAYER_LINEWT_OVR
    360         <<< handle to XRECORD
    E2

Transparency override XRECORD:

.. code-block:: none

    0           <<< entity type
    XRECORD
    5           <<< handle
    E5
    102         <<< reactors app data
    {ACAD_REACTORS
    330
    B3          <<< extension dictionary
    102
    }
    330         <<< owner tag
    B3          <<< extension dictionary
    100         <<< subclass marker
    AcDbXrecord
    280         <<< cloning flag
    1           <<< keep existing
    102         <<< for each overridden VIEWPORT one entry
    {ADSK_LYR_ALPHA_OVERRIDE
    335         <<< handle to VIEWPORT
    AC
    440         <<< transparency override
    33554661
    102
    }

Color override XRECORD:

.. code-block:: none

    0
    XRECORD
    ...         <<< like transparency XRECORD
    102         <<< for each overridden VIEWPORT one entry
    {ADSK_LYR_COLOR_OVERRIDE
    335         <<< handle to VIEWPORT
    AF
    420         <<< color override
    -1023409925 <<< raw color value
    102
    }

Linetype override XRECORD:

.. code-block:: none

    0
    XRECORD
    ...         <<< like transparency XRECORD
    102         <<< for each overridden VIEWPORT one entry
    {ADSK_LYR_LINETYPE_OVERRIDE
    335         <<< handle to VIEWPORT
    AC
    343         <<< linetype override
    DC          <<< handle to LINETYPE table entry
    102
    }

Lineweight override XRECORD:

.. code-block:: none

    0
    XRECORD
    ...         <<< like transparency XRECORD
    102         <<< for each overridden VIEWPORT one entry
    {ADSK_LYR_LINEWT_OVERRIDE
    335         <<< handle to VIEWPORT
    AC
    91          <<< lineweight override
    13          <<< lineweight value
    102
    }

Name References
---------------

LAYER table entries are referenced by name:

    - all graphical DXF entities
    - VIEWPORT entity

.. _LAYER: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-D94802B0-8BE8-4AC9-8054-17197688AFDB

.. _TABLES Section: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-A9FD9590-C97B-4E41-9F26-BD82C34A4F9F