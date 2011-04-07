Reference
=========

The `DXF Reference`_ is online available at `Autodesk`_.

Quoted from the original DXF 12 Reference which is **not** available on the web:

   Since the AutoCAD drawing database (.dwg file) is written in a
   compact format that changes significantly as new features are added
   to AutoCAD, we do not document its format and do not recommend that
   you attempt to write programs to read it directly. To assist in
   interchanging drawings between AutoCAD and other programs, a Drawing
   Interchange file format (DXF) has been defined. All implementations
   of AutoCAD accept this format and are able to convert it to and from
   their internal drawing file representation.

DXF File Format
---------------

A Drawing Interchange File is simply an ASCII text file with a file
type of .dxf and specially formatted text. The overall organization
of a DXF file is as follows:

1. HEADER section - General information about the drawing is found
   in this section of the DXF file. Each parameter has a variable
   name and an associated value.

2. TABLES section - This section contains definitions of named
   items.

   * Linetype table (LTYPE)
   * Layer table (LAYER)
   * Text Style table (STYLE)
   * View table (VIEW)
   * User Coordinate System table (UCS)
   * Viewport configuration table (VPORT)
   * Dimension Style table (DIMSTYLE)
   * Application Identification table (APPID)

3. BLOCKS section - This section contains Block Definition entities
   describing the entities that make up each Block in the drawing.

4. ENTITIES section - This section contains the drawing entities,
   including any Block References.

5. END OF FILE

Drawing
-------

The :class:`Drawing` class manages all entities and tables related to a
DXF drawing. You can read DXF drawings from file-system or from a text-stream
and you can also write the drawing to file-system or to a text-stream.

.. toctree::
   :maxdepth: 2

   dwgmanagement
   drawing
   sections

Tables
------

.. toctree::
   :maxdepth: 2

   tables

Layouts
-------

.. toctree::
   :maxdepth: 2

   layouts

Entities
--------

.. toctree::
   :maxdepth: 2

   entities

Blocks
------

.. toctree::
   :maxdepth: 2

   blocks

.. _DXF Reference: http://usa.autodesk.com/adsk/servlet/item?siteID=123112&id=12272454&linkID=10809853
.. _Autodesk: http://usa.autodesk.com/