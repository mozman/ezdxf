.. _MTEXT Internals:

MTEXT Internals
===============

The MTEXT entity stores multiline text in a single entity and was introduced
in DXF version R13/R14. For more information about the top level stuff go to
the :class:`~ezdxf.entities.MText` class.

.. seealso::

    - DXF Reference: `MTEXT`_
    - :class:`ezdxf.entities.MText` class

The MTEXT entity does not establish an OCS. The has a text direction attribute,
which defines the local x-axis, the extrusion attribute defines the normal
vector and the y-axis = extrusion cross x-axis.

The MTEXT entity can have also a rotation attribute (in degrees), the x-axis
attribute has higher priority than the rotation attribute, but it is not clear
how convert the rotation attribute into x-axis, but for most common cases
where only the rotation is present, the extrusion is most likely the WCS z-axis
and the rotation is the direction in the xy-plane.

The content text is divided across multiple tags of group code 3 and 1, the last
line has the group code 1, each line can have a maximum line length of 255 bytes,
but BricsCAD (and AutoCAD?) store only 249 bytes (1 byte is not always 1 char)
in single line.

Text formatting is done by inline codes, see :class:`~ezdxf.entities.MText` class.

CAD application build multiple columns by chaining 2 or ore MTEXT entities
together. In this case each column is a self-sufficient entity in DXF version
R13 until R2013, the additional columns specifications are stored in the XDATA
if the MTEXT which represents the first column.

DXF R2018 changed the implementation into a single MTEXT entity which contains
all the content text at once and stores the column specification in an
embedded object.


Example column specification:

    - Column Type: Static
    - Number of Columns: 3
    - Height: 150.0
    - Width: 50.0
    - Gutter Width: 12.5

DXF R2000 example with column specification stored in XDATA:

.. code-block::

    0
    MTEXT
    5
    9D
    102
    {ACAD_XDICTIONARY
    360
    9F
    102
    }
    330
    1F
    100
    AcDbEntity
    8
    0
    100         <<< begin of MTEXT specific data
    AcDbMText
    10          <<< (10, 20, 30) insert location in WCS
    285.917876152751
    20
    276.101821192053
    30
    0.0
    40          <<< character height in drawing units
    2.5
    41          <<< reference column width, if not in column mode
    62.694...   <<< in column mode: the real column is defined in XDATA (48)
    71          <<< attachment point
    1
    72          <<< text flow direction
    1
    3           <<< begin of text
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam ...
    3
    kimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit ...
    3
    ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ...
    3
    At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd ...
    3
    ore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio ...
    1           <<< last text line and end of text
    euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.
    73          <<< line spacing style
    1
    44          <<< line spacing factor
    1.0
    1001
    AcadAnnotative
    1000
    AnnotativeData
    1002
    {
    1070
    1
    1070
    0
    1002
    }
    1001        <<< AppID "ACAD" contains the column specification
    ACAD
    1000
    ACAD_MTEXT_COLUMN_INFO_BEGIN
    1070
    75          <<< group code column type
    1070
    1           <<< column type: 0=no column; 1=static columns; 2=dynamic columns
    1070
    79          <<< group code column auto height
    1070
    0           <<< column auto height
    1070
    76          <<< group code column count
    1070
    3           <<< column count
    1070
    78          <<< group code column flow reversed
    1070
    0           <<< flag column flow reversed
    1070
    48          <<< group code column width
    1040
    50.0        <<< column width, all columns have the same width - real column width
    1070
    49          <<< group code column gutter
    1040
    12.5        <<< column gutter, all columns have the same gutter?
    1000
    ACAD_MTEXT_COLUMN_INFO_END
    1000        <<< linked MTEXT entities specification
    ACAD_MTEXT_COLUMNS_BEGIN
    1070
    47          <<< group code for column count, incl. the 1st column - this entity
    1070
    3           <<< column count
    1005
    1B4         <<< handle to 2nd column as MTEXT entity
    1005
    1B5         <<< handle to 3rd column as MTEXT entity
    1000
    ACAD_MTEXT_COLUMNS_END
    1000
    ACAD_MTEXT_DEFINED_HEIGHT_BEGIN
    1070
    46          <<< group code for defined column height
    1040
    150.0       <<< defined column height
    1000
    ACAD_MTEXT_DEFINED_HEIGHT_END

Same example in DXF R2018 with column specification stored in an embedded object:

.. code-block::

    0
    MTEXT
    5
    9D
    102
    {ACAD_XDICTIONARY
    360
    9F
    102
    }
    330
    1F
    100
    AcDbEntity
    8
    0
    100
    AcDbMText
    10
    285.917876152751
    20
    276.101821192053
    30
    0.0
    40
    2.5
    41
    62.694536423841
    46
    150.0
    71
    1
    72
    1
    3
    Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy ...
    3
    imata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, ...
    3
    a rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ...
    3
    vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd ...
    3
    eu feugiat nulla facilisis at vero eros et accumsan et iusto odio ...
    3
    od tincidunt ut laoreet dolore magna aliquam erat volutpat.   \P\PUt ...
    3
    e velit esse molestie consequat, vel illum dolore eu feugiat nulla ...
    3
    obis eleifend option congue nihil imperdiet doming id quod mazim placerat ...
    3
    m ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis ...
    3
    lisis.   \P\PAt vero eos et accusam et justo duo dolores et ea rebum. Stet ...
    3
    t labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et ...
    3
    litr, At accusam aliquyam diam diam dolore dolores duo eirmod eos erat, et ...
    1
    ipsum dolor sit amet, consetetur
    73
    1
    44
    1.0
    101         <<< column specification as embedded object
    Embedded Object
    70          <<< ???
    1
    10          <<< (10, 20, 30) text direction vector (local x-axis)
    1.0
    20
    0.0
    30
    0.0
    11          <<< (11, 21, 31) repeated insert location (10, 20, 30) in AcDbMText
    285.917876152751
    21
    276.101821192053
    31
    0.0
    40          <<< reference column width, group code 41 in AcDbMText
    62.694536423841
    41          <<< defined column height, XDATA (46)
    150.0
    42          <<< extents (total) width
    175.0
    43          <<< extents (total) height
    150.0
    71          <<< column type: 0=no column; 1=static columns; 2=dynamic columns
    1
    72          <<< column height count, if not auto height and column type is dynamic columns
    3
    44          <<< column width, XDATA (48)
    50.0
    45          <<< column gutter, XDATA (49)
    12.5
    73          <<< column auto height
    0
    74          <<< reversed column flow
    0
    1001
    AcadAnnotative
    1000
    AnnotativeData
    1002
    {
    1070
    1
    1070
    0
    1002
    }

.. _MTEXT: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-5E5DB93B-F8D3-4433-ADF7-E92E250D2BAB