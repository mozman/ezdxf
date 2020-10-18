TODO
====
 
Add-ons
-------

- drawing
    - ACAD_TABLE
    - MLEADER ???
    - MLINE ???
    - render POINT symbols (v0.15)
    - render proxy graphic, class `ProxyGraphic()` is already 
      implemented but not tested with real world data.
- Simple SVG exporter
- DWG loader (work in progress)         

Render Tools
------------

- `ACADTable.virtual_entities()` ??? -> requires basic ACAD_TABLE support
- `MLeader.virtual_entities()` ??? -> requires complete MLEADER implementation
- `MLine.virtual_entities()` ??? -> requires complete MLINE implementation

DXF Entities
------------

- DIMENSION rendering
    - angular dim
    - angular 3 point dim
    - ordinate dim
    - arc dim
- MLEADER
- MLINE
- FIELD
- ACAD_TABLE

- Blocks.purge() search for non-explicit block references in:
    - All arrows in DIMENSION are no problem, there has to be an explicit 
      INSERT for each used arrow in the associated geometry block.
    - user defined arrow blocks in LEADER, MLEADER
    - LEADER override: 'dimldrblk_handle'
    - MLEADER: block content
    - ACAD_TABLE: block content


DXF Audit & Repair
------------------

- check DIMENSION
    - dimstyle exist; repair: set to 'Standard'
    - arrows exist; repair: set to '' = default open filled arrow
    - text style exist; repair: set to 'Standard'

Cython Code
-----------

- optional for install, testing and development
- profiling required!!!
- optimized Vec2(), Vector() and Matrix44() classes
- optimized math & construction tools
- optimized tag loader
