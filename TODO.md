TODO
====
 
Add-ons
-------

- drawing
    - MLEADER support (v0.16)
    - add support for ATTRIB with embedded MTEXT (v0.16)
    - render proxy graphic, class `ProxyGraphic()` is already 
      implemented but not tested with real world data.
    - ACAD_TABLE

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

- Optimize DXF loading (>1.0): SubclassProcessor.load_tags_into_namespace()
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

Cython Code (>1.0)
------------------

- optional for install, testing and development
- profiling required!!!
- optimized Vec2(), Vector() and Matrix44() classes
- optimized math & construction tools
- optimized tag loader
