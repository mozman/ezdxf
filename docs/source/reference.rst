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
   :maxdepth: 1

   graphic_base_class
   point_entity
   line_entity
   circle_entity
   arc_entity
   text_entity
   shape_entity
   polyline_entity
   solid_entity
   trace_entity
   3dface_entity
   ellipse_entity
   lwpolyline_entity
   mtext_entity
   hatch_entity
   mesh_entity
   spline_entity
   image_entity
   ray_entity
   xline_entity
   body_entity
   region_entity
   3dsolid_entity
   underlay_entity

Blocks
------

.. toctree::
   :maxdepth: 2

   blocks

Groups
------

.. toctree::
   :maxdepth: 1

   groups

Objects
-------

.. toctree::
   :maxdepth: 1

   object_base_class
   imagedef_entity
   underlaydef_entity


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

   algebra


.. _DXF Reference: http://docs.autodesk.com/ACD/2014/ENU/index.html?url=files/GUID-235B22E0-A567-4CF6-92D3-38A2306D73F3.htm,topicNumber=d30e652301
.. _Autodesk: http://usa.autodesk.com/