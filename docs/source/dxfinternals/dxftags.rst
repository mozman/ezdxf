.. _DXF Tags:

DXF Tags
========

A Drawing Interchange File is simply an ASCII text file with a file
type of .dxf and special formatted text. The basic file structure
are DXF tags, a DXF tag consist of a DXF group code as an integer
value on its own line and a the DXF value on the following line.
In the ezdxf documentation DXF tags will be written as (group code, value).

Group codes are indicating the value type:

============ ==================
Group Code   Value Type
============ ==================
0-9          String (with the introduction of extended symbol names in DXF R2000, the 255-character limit has been
             increased to 2049 single-byte characters not including the newline at the end of the line)
10-39        Double precision 3D point value
40-59        Double-precision floating-point value
40-59        Double-precision floating-point value
60-79        16-bit integer value
90-99        32-bit integer value
100          String (255-character maximum, less for Unicode strings)
102          String (255-character maximum, less for Unicode strings)
105          String representing hexadecimal (hex) handle value
110-119      Double precision floating-point value
120-129      Double precision floating-point value
130-139      Double precision floating-point value
140-149      Double precision scalar floating-point value
160-169      64-bit integer value
170-179      16-bit integer value
210-239      Double-precision floating-point value
270-279      16-bit integer value
280-289      16-bit integer value
290-299      Boolean flag value
300-309      Arbitrary text string
310-319      String representing hex value of binary chunk
320-329      String representing hex handle value
330-369      String representing hex object IDs
370-379      16-bit integer value
380-389      16-bit integer value
390-399      String representing hex handle value
400-409      16-bit integer value
410-419      String
420-429      32-bit integer value
430-439      String
440-449      32-bit integer value
450-459      Long
460-469      Double-precision floating-point value
470-479      String
480-481      String representing hex handle value
999          Comment (string)
1000-1009    String (same limits as indicated with 0-9 code range)
1010-1059    Double-precision floating-point value
1060-1070    16-bit integer value
1071         32-bit integer value
============ ==================

Explanation for some important group codes:

================= =======
Group Code        Meaning
================= =======
0                 DXF structure tag, entity start/end or table entries
1                 The primary text value for an entity
2                 A name: Attribute tag, Block name, and so on. Also used to identify a DXF section or table name.
3-4               Other textual or name values
5                 Entity handle expressed as a hex string (fixed)
6                 Line type name (fixed)
7                 Text style name (fixed)
8                 Layer name (fixed)
9                 Variable name identifier (used only in HEADER section of the DXF file)
10                Primary X coordinate (start point of a Line or Text entity, center of a Circle, etc.)
11-18             Other X coordinates
20                Primary Y coordinate. 2n values always correspond to 1n values and immediately follow them in the file
                  (expected by ezdxf!)
21-28             Other Y coordinates
30                Primary Z coordinate. 3n values always correspond to 1n and 2n values and immediately follow them in the
                  file (expected by ezdxf!)
31-38             Other Z coordinates
39                This entity's thickness if nonzero (fixed)
40-48             Float values (text height, scale factors, etc.)
49                Repeated value - multiple 49 groups may appear in one entity for variable length tables (such as the dash
                  lengths in the LTYPE table). A 7x group always appears before the first 49 group to specify the table
                  length
50-58             Angles
62                Color number (fixed)
66                "Entities follow" flag (fixed), only in INSERT and POLYLINE entities
67                Identifies whether entity is in model space or paper space
68                Identifies whether viewport is on but fully off screen, is not active, or is off
69                Viewport identification number
70-78             Integer values such as repeat counts, flag bits, or modes
210, 220, 230     X, Y, and Z components of extrusion direction (fixed)
999               Comments
================= =======

Extended entity data:

================= =======
Group Code        Meaning
================= =======
1000              An ASCII string (up to 255 bytes long) in extended entity data
1001              Registered application name (ASCII string up to 31 bytes long) for XDATA (fixed)
1002              Extended entity data control string ("{" or "}") (fixed)
1003              Extended entity data Layer name
1004              Chunk of bytes (up to 127 bytes long) in extended entity data
1005              Extended entity data database handle
1010, 1020, 1030  Extended entity data X, Y, and Z coordinates
1011, 1021, 1031  Extended entity data X, Y, and Z coordinates of 3D world space position
1012, 1012, 1022  Extended entity data X, Y, and Z components of 3D world space displacement
1013, 1023, 1033  Extended entity data X, Y, and Z components of 3D world space direction
1040              Extended entity data Floating-point value
1041              Extended entity data distance value
1042              Extended entity data scale factor
1070              Extended entity data 16-bit signed integer
1071              Extended entity data 32-bit signed long
================= =======

For explanation of all group codes see: `DXF Group Codes in Numerical Order Reference`_ provided by Autodesk

Storage of String Values
------------------------

String values stored in a DXF file can be expressed in plain ASCII, UTF-8, CIF (Common Interchange Format), and MIF
(Maker Interchange Format) formats. The UTF-8 format is only supported in the DXF R2007 and later file formats.
When the AutoCAD program writes a DXF file, the format in which string values are written is determined by the DXF file
format chosen.

ezdxf internal converts all strings into unicode but does not encode or decode CIF/MIF.

String values are written out in these formats by AutoCAD/ezdxf:

- DXF R2007 and later: UTF-8
- DXF R2004 and earlie: Plain ASCII and CIF encoded for codepage set in header var $DWGCODEPAGE

ezdxf registers an encoding codec `dxfbackslashreplace`, defined in ezdxf.lldxf.encoding

String values containing Unicode characters are represented with control character sequences.

For example, ``"TEST\U+7F3A\U+4E4F\U+89E3\U+91CA\U+6B63THIS\U+56FE"``

String values can be stored with these dxf group codes:

- 0 - 9
- 100 - 101
- 300 - 309
- 410 - 419
- 430 - 439
- 470 - 479
- 999 - 1003

TODO: Multiline text tags (1, ..) (3, ...) (3, ...) as in MTEXT

Subclass Markers
----------------

When filing a stream of group data, a single object may be composed of several filer members, one for each level of
inheritance where filing is done. Since derived classes and levels of inheritance can evolve separately, the data of
each class filer member must be segregated from other members. This is achieved using subclass markers.

All class filer members are expected to precede their class-specific portion of instance data with a “subclass” marker —
a 100 group code followed by a string with the actual name of the class. This does not affect the state needed to define
the object's state, but it provides a means for the DXF file parsers to direct the group codes to the corresponding
application software. See `Subclass Marker Example`_ in the DXF Reference.


.. _DXF Group Codes in Numerical Order Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3F0380A5-1C15-464D-BC66-2C5F094BCFB9

.. _Subclass Marker Example: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-CC5ACB1B-BBA3-463B-84A5-6CCD320C66E7
