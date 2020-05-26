Version 0.13 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-13.html
- NEW: general transformation interface: `DXFGraphic.transform(m)`, 
  transform entity by a transformation matrix `m` inplace
- NEW: specialized entity transformation interfaces:
    - `DXFGraphic.translate(dx, dy, dz)`
    - `DXFGraphic.scale(sx, sy, sz)`
    - `DXFGraphic.scale_uniform(s)`
    - `DXFGraphic.rotate_axis(axis, angle)`
    - `DXFGraphic.rotate_x(angle)`
    - `DXFGraphic.rotate_y(angle)`
    - `DXFGraphic.rotate_z(angle)`
    
   supported entities: POINT, LINE, CIRCLE, ARC, ELLIPSE, MESH, SPLINE, POLYLINE, LWPOLYLINE, TEXT, MTEXT, 
   INSERT, SOLID, TRACE, 3DFACE, HELIX, IMAGE, LEADER, LIGHT, TOLERANCE, SHAPE, XLINE, RAY
   
- NEW: `ezdxf.math.linspace()` like `numpy.linspace()`
- NEW: `Arc.angles(num)`, yields `num` angles from start- to end angle in counter clockwise order
- NEW: `Ellipse.params(num)`, yields `num` params from start- to end param in counter clockwise order
- NEW: `UCS` and `OCS` uses `Matrix44`for transformations
- CHANGE: `Hatch` full support for rotated patterns.
- CHANGE: `Hatch.set_pattern_definition()` added argument `angle` for pattern rotation. 
- NEW: `Hatch.set_pattern_scale()` to set scaling of pattern definition
- NEW: `Hatch.set_pattern_angle()` to set rotation angle of pattern definition
- DEPRECATED: getter and edit methods in `Hatch` for attributes `paths`, `gradient`, `pattern` and `seeds` 
- REMOVED: `ezdxf.math.Matrix33` class  
- REMOVED: `ezdxf.math.BRCS` class and `Insert.brcs()`
- CHANGE: renamed old `Insert.scale()` to `Insert.set_scale()`, name conflict with transformation interface
- REMOVED: `ezdxf.math.normalize_angle(angle)`, replace call by expression: `angle % math.tau`
- DEPRECATED: `DXFGraphic.transform_to_wcs(ucs)`, replace call by `DXFGraphic.transform(ucs.matrix)`
- DEPRECATED: `non_uniform_scaling` argument for `Insert.explode()`  
- DEPRECATED: `non_uniform_scaling` argument for `Insert.virtual_entities()`  
