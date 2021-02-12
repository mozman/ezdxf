Version 0.16 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-16.html
- NEW: `text2path` add-on to create `Path` objects from text strings and text 
  entities, see [docs](https://ezdxf.mozman.at/docs/addons/text2path.html)
- NEW: `bbox` module to detect extents of DXF entities, see [docs](https://ezdxf.mozman.at/docs/bbox.html)
- NEW: `zoom` module to reset the active viewport of layouts, see [docs](https://ezdxf.mozman.at/docs/zoom.html)
- NEW: `path` sub-package, an extended version of the previous `ezdxf.render.path`
  module, see [docs](https://ezdxf.mozman.at/docs/path.html)
- NEW: support module `disassemble`, see [docs](https://ezdxf.mozman.at/docs/disassemble.html)
- NEW: quadratic Bézier curve support for the `Path()` class
- NEW: `ezdxf.math.Bezier3P`, optimized quadratic Bézier curve construction tool 
- NEW: `ezdxf.math.quadratic_to_cubic_bezier()`, Bezier3P to Bezier4P converter   
- NEW: `ezdxf.math.bezier_to_bspline()`, Bezier to BSpline converter
- NEW: `ezdxf.math.clip_polygon_2d()`, clip polygon by a convex clipping polygon 
- NEW: `ezdxf.math.basic_transformation()`, returns a combined transformation 
  matrix for translation, scaling and rotation about the z-axis 
- CHANGED: `ezdxf.render.nesting` content moved into the `ezdxf.path` package
- CHANGED: renamed `MeshBuilder.render()` to `MeshBuilder.render_mesh()`
- DEPRECATED: `ezdxf.render.path` module, replaced by `ezdxf.path` package
- DEPRECATED: `Path.from_lwpolyline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_polyline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_spline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_ellipse()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_arc()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_circle()`, replaced by factory `make_path()`
- DEPRECATED: `Path.add_curve()`, replaced by function `add_bezier4p()`
- DEPRECATED: `Path.add_ellipse()`, replaced by function `add_ellipse()`
- DEPRECATED: `Path.add_spline()`, replaced by function `add_spline()`
- DEPRECATED: `Path.add_2d_poyline()`, replaced by function `add_2d_polyline()`
- DEPRECATED: `Path.from_vertices()`, replaced by factory `from_vertices()`
- REMOVED: `Path.from_from_hatch_boundary_path()`, replaced by factory `from_hatch()`
- REMOVED: `Path.from_from_hatch_polyline_path()`
- REMOVED: `Path.from_from_hatch_edge_path()`
- REMOVED: `Block.purge()`, unsafe operation

