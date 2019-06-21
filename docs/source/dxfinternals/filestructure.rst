.. _File Structure:

DXF File Structure
------------------

A DXF File is simply an ASCII text file with a file type of .dxf and special formatted text. The basic file structure
are DXF tags, a DXF tag consist of a DXF group code as an integer value on its own line and a the DXF value on the
following line. In the ezdxf documentation DXF tags will be written as :code:`(group code, value)`. I know there exists
a binary DXF format, but it seems that it is not often used and for reducing file size, zipping is much more efficient.
ezdxf does not support binary encoded DXF files (yet?).

.. seealso::

    For more information about DXF tags see: :ref:`DXF Tags`


A usual DXF file is organized in sections, starting with the DXF tag
(0, 'SECTION') and ending with the DXF tag (0, 'ENDSEC'). The (0, 'EOF')
tag signals the end of file.


1. **HEADER:** General information about the drawing is found in this section of the DXF file.
   Each parameter has a variable name starting with '$' and an associated value. Has to be the first section.

2. **CLASSES:** Holds the information for application defined classes. (DXF R13 and later)

3. **TABLES:**: Contains several tables for style and property definitions.

   * Linetype table (LTYPE)
   * Layer table (LAYER)
   * Text Style table (STYLE)
   * View table (VIEW): (IMHO) layout of the CAD working space, only interesting for interactive CAD applications
   * Viewport configuration table (VPORT): The VPORT table is unique in that it may contain several entries
     with the same name (indicating a multiple-viewport configuration). The entries corresponding to the
     active viewport configuration all have the name \*ACTIVE. The first such entry describes the current
     viewport.

   * Dimension Style table (DIMSTYLE)
   * User Coordinate System table (UCS) (IMHO) only interesting for interactive CAD applications
   * Application Identification table (APPID): Table of names for all applications registered with a drawing.
   * Block Record table (BLOCK_RECORD) (DXF R13 and Later)

4. **BLOCKS:** Contains all block definitions. The block name \*Model_Space or \*MODEL_SPACE is reserved for the
   drawing modelspace and the block name \*Paper_Space or \*PAPER_SPACE is reserved for the *active* paperspace layout.
   Both block definitions are empty, the content of the modelspace and the *active* paperspace is stored in the
   ENTITIES section. The entities of other layouts are stored in special block definitions called \*Paper_Spacennn,
   nnn is an arbitrary but unique number.

5. **ENTITIES:** Contains all graphical entities of the modelspace and the *active* paperspace layout. Entities of
   other layouts are stored in the BLOCKS sections.

6. **OBJECTS:** Contains all non-graphical objects of the drawing (DXF R13 and later)

7. **THUMBNAILIMAGE:** Contains a preview image of the DXF file, it is optional and can usually be ignored.
   (DXF R13 and later)

8. **ACDSDATA:** (DXF R2013 and later) No information in the DXF reference about this section

9. **END OF FILE**

For further information read the original `DXF Reference`_.

Structure of a usual DXF R12 file:

.. code-block:: none

    0           <<< Begin HEADER section, has to be the first section
    SECTION
    2
    HEADER
                <<< Header variable items go here
    0           <<< End HEADER section
    ENDSEC
    0           <<< Begin TABLES section
    SECTION
    2
    TABLES
    0
    TABLE
    2
    VPORT
    70          <<< viewport table maximum item count
                <<< viewport table items go here
    0
    ENDTAB
    0
    TABLE
    2
    APPID, DIMSTYLE, LTYPE, LAYER, STYLE, UCS, VIEW, or VPORT
    70          <<< Table maximum item count, a not reliable value and ignored by AutoCAD
                <<< Table items go here
    0
    ENDTAB
    0           <<< End TABLES section
    ENDSEC
    0           <<< Begin BLOCKS section
    SECTION
    2
    BLOCKS
                <<< Block definition entities go here
    0           <<< End BLOCKS section
    ENDSEC
    0           <<< Begin ENTITIES section
    SECTION
    2
    ENTITIES
                <<< Drawing entities go here
    0           <<< End ENTITIES section
    ENDSEC
    0           <<< End of file marker (required)
    EOF

Minimal DXF Content
-------------------

DXF R12
=======

Contrary to the previous chapter, the DXF R12 format (AC1009) and prior requires just the ENTITIES section:

.. code-block:: none

    0
    SECTION
    2
    ENTITIES
    0
    ENDSEC
    0
    EOF

DXF R13/R14 and later
=====================

DXF version R13/14 and later needs much more DXF content than DXF R12.

Required sections: HEADER, CLASSES, TABLES, ENTITIES, OBJECTS

The HEADER section requires two entries:

- $ACADVER
- $HANDSEED

The CLASSES section can be empty, but some DXF entities requires class definitions to work in AutoCAD.

The TABLES section requires following tables:

- VPORT entry \*ACTIVE is not required! Empty table is ok for AutoCAD.
- LTYPE with at least the following line types defined:

  - BYBLOCK
  - BYLAYER
  - CONTINUOUS

- LAYER with at least an entry for layer '0'
- STYLE with at least an entry for style STANDARD
- VIEW can be empty
- UCS can be empty
- APPID with at least an entry for ACAD
- DIMSTYLE with at least an entry for style STANDARD
- BLOCK_RECORDS with two entries:

  - \*MODEL_SPACE
  - \*PAPER_SPACE

The BLOCKS section requires two BLOCKS:

- \*MODEL_SPACE
- \*PAPER_SPACE

The ENTITIES section can be empty.

The OBJECTS section requires following entities:

- DICTIONARY - the root dict
  - one entry named ACAD_GROUP

- DICTONARY ACAD_GROUP can be empty

Minimal DXF to download: https://bitbucket.org/mozman/ezdxf/downloads/Minimal_DXF_AC1021.dxf

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3
