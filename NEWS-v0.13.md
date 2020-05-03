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
    
   supported entities: POINT, LINE, CIRCLE, ARC
   
- NEW: `ezdxf.math.linspace()` like `numpy.linspace()`
- NEW: `Arc.angles(num)`, yields `num` angles from start- to end angle in counter clockwise order
- NEW: `Ellipse.params(num)`, yields `num` params from start- to end param in counter clockwise order
- REMOVED: `ezdxf.math.normalize_angle(angle)`, replace calls by expression: `angle % math.tau`
- DEPRECATED: `DXFGraphic.transform_to_wcs()`, replace call by `entity.transform(ucs.matrix)` (not implemented)