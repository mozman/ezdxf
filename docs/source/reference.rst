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

1. HEADER - General information about the drawing is found
   in this section of the DXF file. Each parameter has a variable
   name and an associated value.

2. CLASSES - This section holds the information for application-defined
   classes. This section was introduced with AC1015 and can usually be
   ignored.

3. TABLES - This section contains definitions of named items.

   * Linetype table (LTYPE)
   * Layer table (LAYER)
   * Text Style table (STYLE)
   * View table (VIEW)
   * User Coordinate System table (UCS)
   * Viewport configuration table (VPORT)
   * Dimension Style table (DIMSTYLE)
   * Application Identification table (APPID)

4. BLOCKS - This section contains Block Definition entities
   describing the entities that make up each Block in the drawing.

5. ENTITIES - This section contains the drawing entities,
   including any Block References.

6. OBJECTS - non-graphical objects

7. THUMBNAILIMAGE - This section contains a preview image of the DXF
   file, it is optional and can usually be ignored.

8. END OF FILE

By using *ezdxf* you don't have to know anything about this details, but
interested users can look at the original `DXF Reference`_.

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

Importer
--------

.. toctree::
   :maxdepth: 2

   importer

Data Query
----------

.. toctree::
   :maxdepth: 1

   query



.. _DXF Reference: http://docs.autodesk.com/ACD/2014/ENU/index.html?url=files/GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3.htm,topicNumber=d30e652301
.. _Autodesk: http://usa.autodesk.com/