TODO
====

Add-ons
-------

- DWG loader (work in progress)
- Simple SVG exporter
- drawing
    - LEADER
    - ACAD_TABLE
    - MLEADER ???
    - MLINE ???
    - start- and end width support for 2D polylines
    - render POINT symbols
    - resolve fonts and pass them to `draw_text()`, 
      `get_font_measurements()` and `get_text_line_width()`
    - render proxy graphic, class `ProxyGraphic()` is already 
      implemented but not tested with real world data.

Render Tools
------------

- `Leader.virtual_entities()`
- `ACADTable.virtual_entities()`
- `MLeader.virtual_entities()` ???
- `MLine.virtual_entities()` ???
- `TraceBuilder()` class to create banded lines like polylines with start- and end width.
  - `add_station(vertex, start_width, end_width)` 
  - `add_spline(bspline, start_width, end_width, segments)`
  - add arcs or ellipses by converting them to B-splines, required
    tools are already implemented
  - `virtual_entities(dxftype='TRACE', dxfattribs=None)` yields TRACE, SOLID or 3DFACE entities
  - `faces()` yields 4 vertices for each face as a tuple of `Vector()` objects
  - `partial_faces()` yields only the last 2 vertices for each face, 2 vertices of 
    the previous face are the first 2 vertices of the actual face, this works only 
    for traces without width changes at the segment border, end-width of previous 
    segment is equal to the start-width of the actual segment. 
- Decompose polylines into lines and bulges into splines with start- 
  and end-width as input for `Tracer()`
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

DXF Audit & Repair
------------------

- check ownership
    - DXF objects in OBJECTS section
    - DXF Entities in a layout (model space, paper space, block)
- check DIMENSION
    - dimstyle exist
    - arrows exist
    - text style exist
- check TEXT, MTEXT
    - text style exist
- check required DXF attributes:
    - R12: layer; repair: set to '0' (in ezdxf defaults to '0')
    - R2000+: layer, owner?, handle?
- VERTEX on same layer as POLYLINE; repair: set VERTEX layer to POLYLINE layer
- find unreferenced objects:
    - DICTIONARY e.g. orphaned extension dicts; repair: delete
- find unused BLOCK definitions: has no corresponding INSERT; repair: delete
    - EXCEPTION: layout blocks
    - EXCEPTION: anonymous blocks without explicit INSERT like DIMENSION geometry

Cython Code
-----------

- optional for install, testing and development
- profiling required!!!
- optimized Vec2(), Vector() and Matrix44() classes
- optimized math & construction tools
- optimized tag loader
