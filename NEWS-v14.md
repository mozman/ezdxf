Version 0.14 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-14.html
- CHANGE: `linspace()` uses Decimal() for precise calculations, but still returns float
- NEW: `TraceBuilder()` a render tool to generate quadrilaterals (TRACE, SOLID or 3DFACE) 
  from LWPOLYLINE or 2D POLYLINE with width information.