TODO
====
 
Add-ons
-------

- drawing
    - HATCH island support (v0.15)
    - matplotlib back-end support for: (v0.15)
        - hatch pattern
        - hatch gradient
        - fonts
    - pyqt5 back-end: implement features of matplotlib back-end
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

- LWPOLYLINE and 2D POLYLINE the `virtual_entities(dxftype='ARC')` method
  could return bulges as ARC, ELLIPSE or SPLINE entities
- `ACADTable.virtual_entities()` ??? -> requires basic ACAD_TABLE support
- `MLeader.virtual_entities()` ??? -> requires complete MLEADER implementation
- `MLine.virtual_entities()` ??? -> requires complete MLINE implementation

Geo Interface
-------------

- https://gist.github.com/sgillies/2217756
- First: study existing implementations! 
- Shapely is a good start: https://pypi.org/project/Shapely/
- load by a function `geo_interface()`, like 
  `entity = ezdxf.geo_interface(shape)`, which returns:
  - POINT for Point
  - LWPOLYLINE for LineString
  - multiple LWPOLYLINE entities and/or one HATCH entity for Polygon
- these entities can be added to a layout by the `msp.add_entity()` method
- export by the `__geo_interface__` for:
  - POINT as Point
  - LINE as LineString
  - LWPOLYLINE as LineString
  - SOLID, TRACE and 3DFACE as LineString
  - POLYLINE as LineString (no support for mesh or poly-face-mesh)
  - ARC, CIRCLE, ELLIPSE and SPLINE as flattened LineString
  - HATCH as Polygon
  - all 3D entities drop the z-axis, also OCS entities with extrusion 
    vector != (0, 0, 1), projection into the xy-plane.
  - layout filter: `for e in geo_entities_filter(msp): ...`, 
    to filter just entities with `__geo_interface__` support
  
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
