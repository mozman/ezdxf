TODO
====

Add-ons
-------

- DWG loader (work in progress)
- Simple SVG exporter
- drawing
    - support for SORTENTSTABLE - change redraw order of entities in model- 
      and paperspace, see example wipeout_door.dxf, lines below the WIPEOUT of 
      the exploded block are not wiped out without applying SORTENTSTABLE
    - ACAD_TABLE
    - MLEADER ???
    - MLINE ???
    - render POINT symbols
    - render proxy graphic, class `ProxyGraphic()` is already 
      implemented but not tested with real world data.
      
- recover

    Mimic the CAD "RECOVER" command, try to read messy DXF files,
    needs only as much work until the regular ezdxf loader can handle 
    and audit the DXF file:
    
    - recover missing ENDSEC and EOF tags
    - merge multiple sections with same name
    - reorder sections
    - merge multiple tables with same name
    - reorder vertex tags for all possible vertices, 
      use repair.fix_coordinate_order()
    - recover tags "outside" of sections
    - move header variable tags (9, "$...") into HEADER section 
     

Render Tools
------------

- `ACADTable.virtual_entities()`
- `MLeader.virtual_entities()` ???
- `MLine.virtual_entities()` ???
- LWPOLYLINE and 2D POLYLINE the `virtual_entities(dxftype='ARC')` method
  could return bulges as ARC, ELLIPSE or SPLINE entities
  

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
- check TEXT, MTEXT
    - text style exist; repair: set to 'Standard'


Cython Code
-----------

- optional for install, testing and development
- profiling required!!!
- optimized Vec2(), Vector() and Matrix44() classes
- optimized math & construction tools
- optimized tag loader
