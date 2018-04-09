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

Drawing
-------

The :class:`Drawing` class manages all entities and tables related to a
DXF drawing. You can read DXF drawings from file-system or from a text-stream
and you can also write the drawing to file-system or to a text-stream.

.. toctree::
   :maxdepth: 2

   dwgmanagement
   drawing
   header_section

Tables
------


.. toctree::
   :maxdepth: 1

   tables/tables
   tables/layer_table_entry
   tables/style_table_entry
   tables/linetype_table_entry
   tables/dimstyle_table_entry
   tables/vport_table_entry
   tables/view_table_entry
   tables/appid_table_entry
   tables/ucs_table_entry
   tables/blockrecord_table_entry

Layouts
-------

.. toctree::
   :maxdepth: 2

   layouts

Entities
--------

.. toctree::
   :maxdepth: 1

   dxfentities/graphic_base_class
   dxfentities/point
   dxfentities/line
   dxfentities/circle
   dxfentities/arc
   dxfentities/text
   dxfentities/shape
   dxfentities/polyline
   dxfentities/solid
   dxfentities/trace
   dxfentities/3dface
   dxfentities/ellipse
   dxfentities/lwpolyline
   dxfentities/mtext
   dxfentities/hatch
   dxfentities/mesh
   dxfentities/spline
   dxfentities/image
   dxfentities/ray
   dxfentities/xline
   dxfentities/body
   dxfentities/region
   dxfentities/3dsolid
   dxfentities/surface
   dxfentities/underlay

Blocks
------

.. toctree::
   :maxdepth: 1

   blocks/blocks
   blocks/block
   blocks/insert
   blocks/attdef
   blocks/attrib

Groups
------

.. toctree::
   :maxdepth: 1

   groups

Objects
-------

.. toctree::
   :maxdepth: 1

   dxfobjects/object_base_class
   dxfobjects/imagedef
   dxfobjects/underlaydef
   dxfobjects/geodata


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

Fast DXF R12 File/Stream Writer
-------------------------------

.. toctree::
   :maxdepth: 1

   r12writer

Algebra Utilities
-----------------

.. toctree::
   :maxdepth: 1

   algebra/functions
   algebra/ocs_ucs
   algebra/vector
   algebra/matrix44
   algebra/bspline

Tag Data Structures
-------------------

.. toctree::
   :maxdepth: 2

   tags

.. _DXF Reference: http://docs.autodesk.com/ACD/2014/ENU/index.html?url=files/GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3.htm,topicNumber=d30e652301
.. _Autodesk: http://usa.autodesk.com/