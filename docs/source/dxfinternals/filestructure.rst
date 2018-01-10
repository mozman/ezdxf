.. _file structure:

DXF File Structure
------------------

A Drawing Interchange File is simply an ASCII text file with a file
type of .dxf and special formatted text. The basic file structure
are DXF tags, a DXF tag consist of a DXF group code as an integer
value on its own line and a the DXF value on the following line.
In the documentation DXF tags will be written as (group code, value).

Group codes are indicating the value type:

============ ==================
Group Code   Value Type
============ ==================
0 - 9        String
10 - 59      Float
60 - 79      Integer
140 - 147    Float
170 - 175    Integer
210 - 239    Float
999          Comment (string)
1000 - 1009  String
1010 - 1059  Float
1060 - 1079  Integer
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

A usual DXF file is organized in sections, starting with the DXF tag
(0, 'SECTION') and ending with the DXF tag (0, 'ENDSEC'). The (0, 'EOF')
tag signals the end of file.


1. **HEADER** - General information about the drawing is found in this section of the DXF file.
   Each parameter has a variable name and an associated value.

2. **CLASSES** - holds the information for application defined classes. (DXF13 and later)

3. **TABLES** - contains definitions of named items.

   * Linetype table (LTYPE)
   * Layer table (LAYER)
   * Text Style table (STYLE)
   * View table (VIEW): (IMHO) layout of the CAD working space, only interesting for interactive CAD applications
   * Viewport configuration table (VPORT): The VPORT table is unique in that it may contain several entries
     with the same name (indicating a multiple-viewport configuration). The entries corresponding to the
     active viewport configuration all have the name ``*ACTIVE``. The first such entry describes the current
     viewport.

   * Dimension Style table (DIMSTYLE)
   * User Coordinate System table (UCS) (IMHO) only interesting for interactive CAD applications
   * Application Identification table (APPID): Table of names for all applications registered with a drawing.
   * Block Record table (BLOCK_RECORD) (DXF R13 and Later)

4. **BLOCKS** - contains all block definitions. A block definition defines the content of a block.
   The block name ``*Model_Space`` or ``*MODEL_SPACE`` is reserved for the drawing model space and the block name
   ``*Paper_Space`` or ``*PAPER_SPACE`` is reserved for the active paper space layout. Both block definitions are empty,
   the content of the model space and the active paper space is stored in the ENTITIES section. The entities of other
   layouts are stored in special block definitions called ``*Paper_Spacennn``, nnn is an arbitrary but unique number.

5. **ENTITIES** - contains the drawing entities of the model space and the active paper space layout. Entities of other
   layouts are stored in the BLOCKS sections.

6. **OBJECTS** - non-graphical objects (DXF R13 and later)

7. **THUMBNAILIMAGE** - contains a preview image of the DXF file, it is optional and can usually be ignored.
   (DXF R13 and later)

8. **END OF FILE**

For further information read the original `DXF Reference`_.

Structure a usual DXF R12 file::

  0            (Begin HEADER section)
  SECTION
  2
  HEADER
               <<<<Header variable items go here>>>>
  0
  ENDSEC       (End HEADER section)
  0            (Begin TABLES section)
  SECTION
  2
  TABLES
  0
  TABLE
  2
  VPORT
  70           (viewport table maximum item count)
               <<<<viewport table items go here>>>>
  0
  ENDTAB
  0
  TABLE
  2
  APPID, DIMSTYLE, LTYPE, LAYER, STYLE, UCS, VIEW, or VPORT
  70           (Table maximum item count)
               <<<<Table items go here>>>>
  0
  ENDTAB
  0
  ENDSEC       (End TABLES section)
  0            (Begin BLOCKS section)
  SECTION
  2
  BLOCKS
               <<<<Block definition entities go here>>>>
  0
  ENDSEC       (End BLOCKS section)
  0            (Begin ENTITIES section)
  SECTION
  2
  ENTITIES
               <<<<Drawing entities go here>>>>
  0
  ENDSEC       (End ENTITIES section)
  0
  EOF          (End of file)

Minimal DXF Content
-------------------

DXF R12
=======

Contrary to the previous chapter, the DXF R12 format (AC1009) and prior requires just the ENTITIES section::

    0
    SECTION
    2
    ENTITIES
    0
    ENDSEC
    0
    EOF

DXF R13/14 and later
====================

DXF version R13/14 and later needs much more DXF content than DXF version R12.

Required sections: HEADER, CLASSES, TABLES, ENTITIES, OBJECTS

The HEADER section requires two entries:

- ``$ACADVER``
- ``$HANDSEED``

The CLASSES section can be empty, but some DXF entities requires class definitions to work in AutoCAD.

The TABLES section requires following tables:

- VPORT with at least an entry called ``'*ACTIVE'``
- LTYPE with at least the following line types defined:

  - ``ByBlock``
  - ``ByLayer``
  - ``Continuous``

- LAYER with at least an entry for layer ``0``
- STYLE with at least an entry for style ``STANDARD``
- VIEW can be empty
- UCS can be empty
- APPID with at least an entry for ``ACAD``
- DIMSTYLE with at least an entry for style ``STANDARD``
- BLOCK_RECORDS with two entries:

  - ``*MODEL_SPACE``
  - ``*PAPER_SPACE``

The BLOCKS section requires two BLOCKS:

- ``*MODEL_SPACE``
- ``*PAPER_SPACE``

The ENTITIES section can be empty.

The OBJECTS section requires following entities:

- DICTIONARY - the root dict
  - one entry ``ACAD_GROUP``

- DICTONARY ``ACAD_GROUP`` can be empty

Minimal DXF to download: https://bitbucket.org/mozman/ezdxf/downloads/Minimal_DXF_AC1021.dxf

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3

.. _DXF Group Codes in Numerical Order Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-3F0380A5-1C15-464D-BC66-2C5F094BCFB9