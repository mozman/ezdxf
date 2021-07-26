TODO
====
 
Add-ons
-------

- drawing
    - (v0.17) add support for ATTRIB with embedded MTEXT
    - (v0.17) global fonts cache usage
    - (v0.17) extended MTEXT renderer  
    - (v0.18) MLEADER full rendering support, requires `MLeader.virtual_entities()`
    - (>v1.0) ACAD_TABLE
    - (>v1.0) support for switching plot styles (DXF_DEFAULT_PAPERSPACE_COLORS)
  
- geo: (v0.17) MPOLYGON support
  
- (>v1.0) Native SVG exporter, planned after the matplotlib backend supports 
  all v1.0 features. 

- (>v1.0) Native PDF exporter? Problem: The PDF 1.7 reference has ~1300 pages, 
  but I assume I only need a fraction of that information for a simple exporter. 
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
    
- (>v1.0) DWG loader, planned for the future. Cython will be required for the 
  low level stuff, no pure Python implementation.

Render Tools
------------

- (v0.17) `EulerSpiral()` conversion to B-spline with end tangent constraints
- (v0.18) `MLeader.virtual_entities()`
- (v0.18) DIMENSION rendering
    - angular dim
    - angular 3 point dim
    - ordinate dim
    - arc dim
- (>v1.0) `ACADTable.virtual_entities()`, requires basic ACAD_TABLE support
- (>v1.0) tool to create proxy graphic 

Construction Tools
------------------

- (<v1.0) `make_primitive()`: apply thickness if not 0, which creates meshes 

DXF Entities
------------

- (v0.17) ATTRIB/ATTDEF support for embedded MTEXT entity,
  example: `dxftest/attrib_attdef_with_embedded_mtext.dxf`
- (v0.17) Remove generic "Embedded Object" support in DXFEntity because this is 
  always a special case which should be handled by DXF load/export procedure, 
  and it is used only by ATTRIB/ATTDEF/MTEXT yet.
- (v0.18) MLEADER: factory methods to create new MLEADER entities
- (<v1.0) do more entities support the DXF "thickness" attribute (group code 39)?
  possible candidates: HATCH, MPOLYGON, planar SPLINE, ELLIPSE, MLINE 
  -> `make_primitive()` 
- (>v1.0) GEODATA version 1 support, see mpolygon examples and DXF reference R2009
- (>v1.0) FIELD, used by ACAD_TABLE and MTEXT
- (>v1.0) ACAD_TABLE

DXF Document
------------

- (>v1.0) `doc.to_dxf_r12()`: convert the whole DXF document into DXF R12. 
  This is a destructive process, which converts MTEXT to TEXT, 
  MESH to PolyFaceMesh, LWPOLYLINE into POLYLINE, flatten SPLINE into 
  POLYLINE ..., and removes all entities not supported by DXF R12 
  like TABLE, ACIS entities, ...
  
- (>v1.0) Optimize DXF export: write tags direct in export_entity() 
  without any indirections, this requires some additional tag writing 
  function in the Tagwriter() class, these additional functions should only use 
  methods from AbstractTagwriter():
  - write_tag2_skip_default(code, value, default)
  - write_vertex_2d(code, value, default) write explicit 2D vertices and 
    skip default value if given
  - a check function for tags containing user strings (line breaks!)
  
DXF Audit & Repair
------------------

- (v0.17) Standalone ATTRIBS are not allowed in model space (also paper space- 
  and block layout?). Important for exploding INSERT entities with ATTRIBS, 
  the current implementation already convert ATTRIB to TEXT. 
  BricsCAD removes them and TrueView crashes, more testing is required. 
- (v0.17) Remove invalid standalone ATTRIB/ATTDEF entities
- (<v1.0) check DIMENSION
  - overridden properties in XDATA have to be checked!
  - dimstyle exist; repair: set to 'Standard'
  - arrows exist; repair: set to '' = default open filled arrow
  - text style exist; repair: set to 'Standard'
  - check consistent defpoint and POINT entity locations in the associated 
    geometry block 
