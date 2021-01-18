TODO
====
 
Add-ons
-------

- drawing
    - MLEADER full rendering support (v0.16), requires `MLeader.virtual_entities()`
    - add support for ATTRIB with embedded MTEXT (v0.16)
    - non-graphical backend for "estimating" bounding boxes (v0.16)
    - ACAD_TABLE

- Tool for estimating bounding boxes, based on the non-graphical 
  backend of the drawing add-on
- Simple SVG exporter, planned after the matplotlib backend supports all the 
  planned features. 
- DWG loader, boring and tedious but really planned for the future         

Render Tools
------------

- `MLeader.virtual_entities()` (v0.16)
- `ACADTable.virtual_entities()` ??? -> requires basic ACAD_TABLE support

DXF Entities
------------

- MLEADER: factory methods to create new MLEADER entities (v0.16)  
- ATTRIB/ATTDEF support for embedded MTEXT entity (v0.16),
  example: `dxftest/attrib_attdef_with_embedded_mtext.dxf`
- Remove generic "Embedded Object" support in DXFEntity because this is always 
  a special case which should be handled by DXF load/export procedure and it is 
  used only by ATTRIB/ATTDEF yet (v0.16).
- Blocks.purge(): remove purge() - it is just too dangerous! The method name 
  suggests a functionality and quality similar to that of a CAD application, 
  which can not be delivered! (v0.16)

- DIMENSION rendering, boring and tedious due to lack of documentation!
    - angular dim
    - angular 3 point dim
    - ordinate dim
    - arc dim
- FIELD, boring and tedious due to lack of documentation!
- ACAD_TABLE, boring and tedious due to lack of documentation!
- disassemble module (v0.16) - recursively disassemble DXF entities:
  - DXF entity collection (model space, entity query) -> flat DXF entity stream 
  - DXF entity stream -> path/mesh stream
  - path/mesh stream -> vertices stream
  
- Optimize DXF export (>1.0): write tags direct in export_entity() 
  without any indirections, but this requires some additional tag writing 
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

Cython Code
-----------

- optimized math & construction tools
- tag loader: creates mostly Python structures, no speed gain by using Cython  
