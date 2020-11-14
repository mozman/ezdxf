TODO
====
 
Add-ons
-------

- drawing
    - ACAD_TABLE
    - MLEADER ???
    - render proxy graphic, class `ProxyGraphic()` is already 
      implemented but not tested with real world data.
    - add support for ATTRIB with embedded MTEXT
- Simple SVG exporter
- DWG loader (work in progress)         

Render Tools
------------

- `ACADTable.virtual_entities()` ??? -> requires basic ACAD_TABLE support
- `MLeader.virtual_entities()` ??? -> requires complete MLEADER implementation

DXF Entities
------------

- DIMENSION rendering
    - angular dim
    - angular 3 point dim
    - ordinate dim
    - arc dim
- MLEADER
- FIELD
- ACAD_TABLE
- ATTRIB/ATTDEF support for embedded MTEXT entity,
  example: `dxftest/attrib_attdef_with_embedded_mtext.dxf`
- Remove generic "Embedded Object" support in DXFEntity because this is always 
  a special case which should be handled by DXF load/export procedure and it is 
  used only by ATTRIB/ATTDEF yet.

- Blocks.purge(): remove purge() - it is just too dangerous! The method name 
  suggests a functionality and quality similar to that of a CAD application, 
  which can not be delivered!

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
