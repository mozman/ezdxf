.. _file structure:

DXF File Structure
------------------

A Drawing Interchange File is simply an ASCII text file with a file
type of .dxf and specially formatted text. The overall organization
of a DXF file is as follows:

1. HEADER - General information about the drawing is found
   in this section of the DXF file. Each parameter has a variable
   name and an associated value.

2. CLASSES - holds the information for application defined classes. This section was introduced with AC1015 and can
   usually be ignored.

3. TABLES - contains definitions of named items.

   * Linetype table (LTYPE)
   * Layer table (LAYER)
   * Text Style table (STYLE)
   * View table (VIEW)
   * User Coordinate System table (UCS)
   * Viewport configuration table (VPORT)
   * Dimension Style table (DIMSTYLE)
   * Application Identification table (APPID)

4. BLOCKS - contains all block definitions. A block definition defines the content of a block.

5. ENTITIES - contains the drawing entities of the model space and the active paper space layout. Entities of other
   layouts are stored in the BLOCKS sections in special block definitions called `*Paper_Space_nnn`, nnn is an arbitrary
   but unique number.

6. OBJECTS - non-graphical objects

7. THUMBNAILIMAGE - contains a preview image of the DXF file, it is optional and can usually be ignored.

8. END OF FILE

By using *ezdxf* you don't have to know much about this details, but
interested users can look at the original `DXF Reference`_.

Minimal DXF Content
-------------------

DXF R12
=======

The DXF format R12 (AC1009) and prior requires just the ENTITIES section::

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

.. _DXF Reference: http://docs.autodesk.com/ACD/2014/ENU/index.html?url=files/GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3.htm,topicNumber=d30e652301