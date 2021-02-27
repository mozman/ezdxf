TODO
====
 
Add-ons
-------

- drawing
    - MLEADER full rendering support (v0.17), requires `MLeader.virtual_entities()`
    - add support for ATTRIB with embedded MTEXT (v0.17)
    - ACAD_TABLE
    - global fonts cache usage
  
- Native SVG exporter, planned after the matplotlib backend supports all the 
  planned features.
- Native PDF exporter? Problem: The PDF 1.7 reference has ~1300 pages, but I 
  assume I only need a fraction of that information for a simple exporter. 
  I can use Matplotlib for text rendering as Bèzier curves if required.
  
  Existing Python packages for PDF rendering: 
  - pycairo: binary wheels for Windows on PyPI - could handle SVG & PDF, but I 
    don't know how much control I get from cairo. The advantage of a native 
    exporter would be to get full control over all available features of the 
    output format, by the disadvantage of doing ALL the work by myself.
  - pypoppler: only source code distribution from 2013 on PyPI
  - python-poppler-qt5: only source code distribution on PyPI
  - Reportlab: more report or magazine page layout oriented
  - PyQt: QPrinter & QPainter - https://wiki.qt.io/Handling_PDF
  
  In consideration, if then SVG exporter works well.
    
- DWG loader, planned for the future. Cython will be required for the low level 
  stuff, no pure Python implementation.         


Render Tools
------------

- `MLeader.virtual_entities()` (v0.17)
- `ACADTable.virtual_entities()` ??? -> requires basic ACAD_TABLE support
- `EulerSpiral()` conversion to B-spline with end tangent constraints

DXF Entities
------------

- MLEADER: factory methods to create new MLEADER entities (v0.17)  
- ATTRIB/ATTDEF support for embedded MTEXT entity (v0.17),
  example: `dxftest/attrib_attdef_with_embedded_mtext.dxf`
- Remove generic "Embedded Object" support in DXFEntity because this is always 
  a special case which should be handled by DXF load/export procedure and it is 
  used only by ATTRIB/ATTDEF yet (v0.17).

- DIMENSION rendering, boring and tedious due to lack of documentation!
    - angular dim
    - angular 3 point dim
    - ordinate dim
    - arc dim
- FIELD, boring and tedious due to lack of documentation!
- ACAD_TABLE, boring and tedious due to lack of documentation!
  
- Optimize DXF export (>1.0): write tags direct in export_entity() 
  without any indirections, this requires some additional tag writing 
  function in the Tagwriter() class, these additional functions should only use 
  methods from AbstractTagwriter():
  - write_tag2_skip_default(code, value, default)
  - write_vertex_2d(code, value, default) write explicit 2D vertices and 
    skip default value if given
  - a check function for tags containing user strings (line breaks!)
  
      
DXF Audit & Repair
------------------

- check DIMENSION
    - dimstyle exist; repair: set to 'Standard'
    - arrows exist; repair: set to '' = default open filled arrow
    - text style exist; repair: set to 'Standard'
  