Version 0.14 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-14.html
- NEW: `addons.drawing.Frontend()` supports width attributes of LWPOLYLINE and 2D POLYLINE entities
- NEW: `TraceBuilder()` a render tool to generate quadrilaterals (TRACE, SOLID or 3DFACE), 
  from LWPOLYLINE or 2D POLYLINE with width information,
  see [docs](https://ezdxf.mozman.at/docs/render/trace.html)
- NEW: `Path()` a render tool for paths build of lines and cubic Bezier curves, used for
  faster rendering of LWPOLYLINE, POLYLINE and SPLINE entities for render back-ends, 
  see [docs](https://ezdxf.mozman.at/docs/render/path.html)  
- NEW: `Arc.construction_tool()` returns the 2D `ConstructionArc()`
- NEW: `Arc.apply_construction_tool()` apply parameters from `ConstructionArc()`
- NEW: `Leader.virtual_entities()` yields 'virtual' DXF primitives
- NEW: `Leader.explode()` explode LEADER as DXF primitives into target layout
- NEW: `Bezier4P.reverse()` returns object with reversed control point order
- NEW: `LWPolyline.has_width` property is `True` if any width attribute is set
- NEW: `Polyline.has_width` property is `True` if any width attribute is set
- NEW: `DXFVertex.format()` support for user defined point format 
- NEW: `BSpline.is_clamped` property is `True` for clamped (open) B-spline
- NEW: `UCS.transform` general transformation interface
- CHANGE: `linspace()` uses Decimal() for precise calculations, but still returns float