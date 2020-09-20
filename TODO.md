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

Geo/Shapely Interface
---------------------

- https://gist.github.com/sgillies/2217756

Shapely: https://pypi.org/project/Shapely/

Many entities must be approximated and the `__geo_interface__` does not 
provide any options for approximation precision, therefore a direct 
implementation of the interface in DXF entities is not the best way.

Implementation as `geo` add-on:

Load geo/shapely objects by function `geo.load()`: 
```
from ezdxf.addons import geo

entity = geo.load(shape, polygon=1) # Polygon as LWPOLYLINE
entity = geo.load(shape, polygon=2) # Polygon as HATCH - has no outline
entity = geo.load(shape, polygon=3) # Polygon as LWPOLYLINE and HATCH
```

which returns:

- POINT for Point
- Iterable of POINT for MultiPoint
- LWPOLYLINE for LineString
- Iterable of LWPOLYLINE for MultiLineString
- List of LWPOLYLINE entities and/or one HATCH entity for Polygon
- Iterable of Polygon objects for MultiPolygon
- GeometryCollection?

The returned objects can be added to a layout by the `geo.append(msp, ret_obj)` 
function.

Export by dict:

`d = geo.mapping(entity, distance=0.1)`

Returns a dict like `{'type': 'Point', 'coordinates': (0.0, 0.0)}`, argument
`distance` defines the maximum flattening distance for entity approximation.

Export by a proxy object:

`proxy = geo.proxy(entity, distance=0.1)`

Returns an object of type `GeoProxy()`, which provides the `__geo_interface__`
attribute.

- POINT as Point
- LINE as LineString
- LWPOLYLINE as LineString
- SOLID, TRACE and 3DFACE as LineString
- POLYLINE as LineString (no support for mesh or poly-face-mesh)
- ARC, CIRCLE, ELLIPSE and SPLINE as flattened LineString
- HATCH as Polygon
- all 3D entities drop the z-axis, also OCS entities with extrusion 
  vector != (0, 0, 1), projection into the xy-plane.

Layout entity filter: `for e in geo.filter(msp): ...`, to filter just entities 
with `__geo_interface__` support.
  
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
