TODO
====
 
Add-ons
-------

- drawing
  - (>v1.0) support for switching plot styles (DXF_DEFAULT_PAPERSPACE_COLORS)
  - (>v1.0) VIEWPORT rendering support?
  
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
  
  In consideration, if the SVG exporter works well.
    
- (>v1.0) DWG loader, planned for the future. Cython will be required for the 
  low level stuff, no pure Python implementation.

Render Tools
------------

- (>v1.0) ACAD_TABLE tool to render content as DXF primitives to create the 
  content of the anonymous block `*T...`
- (>v1.0) factory methods to create ACAD_TABLE entities
- (>v1.0) fix LWPOLYLINE parsing error in ProxyGraphic, see test script 239
- (>v1.0) tool to create proxy graphic 


DXF Entities
------------

- (>v1.0) ACAD_TABLE entity load and export support beyond `AcadTableBlockContent`
- (>v1.0) ACAD_TABLE tool to manage content at table and cell basis
- (>v1.0) GEODATA version 1 support, see mpolygon examples and DXF reference R2009
- (>v1.0) FIELD, used by ACAD_TABLE and MTEXT

DXF Document
------------

- (>v1.0) `doc.to_dxf_r12()`: convert the whole DXF document into DXF R12. 
  This is a destructive process, which converts or explodes DXF entities:
  
  - explode MTEXT, MULTILEADER, MLINE, ACAD_TABLE, ARC_DIMENSION
  - convert MESH to PolyFaceMesh
  - convert LWPOLYLINE into 2D polyline
  - flatten SPLINE into a 3D polyline
  - flatten ELLIPSE into a 3D polyline

  Removes all data not supported by DXF R12:
  - all ACIS based entities 
  - HATCH and MPOLYGON entities
  - IMAGE and UNDERLAY entities
  - XLINE and RAY entities
  - OBJECTS and the CLASSES sections
  - all but the first paper space layout

- (>v1.0) core module `ezdxf.xref` as replacement for the `Importer` add-on
  - AutoCAD does not support DXF as XREF objects!
  - ezdxf will only support DXF as XREF objects, use the `odafc` add-on to convert 
    DWG to DXF
  - has to be much more versatile than the current `Importer` add-on otherwise 
    just improve and extend the `Importer` add-on 
  - resource management like CAD applications, e.g. layer names of xrefs: 
    <dwg-name>$0$layername
  - `xref.bind(xref_block)`: convert a XREF into a common BLOCK, this replaces 
    the model space import of the `Importer` add-on
  - `xref.attach(doc, "xref_filename.dxf")`, replaces `Drawing.add_xref_def()`
  - `xmgr = xref.XRefManager(source_doc, target_doc)`
  - `xmgr.import_modelspace()` import all modelspace entities
  - `xmgr.import_entities(entities)` import selected entities
  - modify entities on import (transform, change DXF properties)
  - `xmgr.import_block("block_name")`
  - `xmgr.import_resources(resource_desc)`
  - `xmgr.import_paperspace("layout_name")` ???
  - `xmgr.finalize()`
  
Documentation
-------------

- Basic concept & tutorial: Text styling (TEXT, ATTRIB, ATTDEF, MTEXT)
- Tutorial for POLYFACE