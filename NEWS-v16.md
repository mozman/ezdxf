Version 0.16 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-16.html
- NEW: `ezdxf.render.make_path()` factory function to create `Path()` objects 
  from many DXF entities.
- NEW: `ezdxf.render.has_make_path_support()` to check if an entity is supported 
  by `make_path()`
- NEW: add-on `text2path`, see [docs](https://ezdxf.mozman.at/docs/addons/text2path.html)
- NEW: support module `bbox`, see [docs](https://ezdxf.mozman.at/docs/bbox.html)
- NEW: support module `disassemble`, see [docs](https://ezdxf.mozman.at/docs/disassemble.html)
- NEW: get clipping path from VIEWPORT entities by `make_path()`
- NEW: `ezdxf.math.Bezier3P`, optimized quadratic Bézier curve construction tool 
- NEW: quadratic Bézier curve support for the `Path()` class 
- NEW: `path.transform_paths()` to transform multiple `Path()` objects at once 
- NEW: `path.make_path()`, convert a DXF entity into a single `Path` object
- NEW: `path.from_hatch()`, convert a HATCH entity into multiple `Path` objects 
- NEW: `path.from_matplotlib_path()`, convert a Matplotlib `Path` into multiple 
  ezdxf `Path` objects (requires `matplotlib`)
- NEW: `path.from_qpainter_path()`, convert a PyQt `QPainterPath` into multiple 
  ezdxf `Path` objects (requires `PyQt5`)
- NEW: `path.transform_paths_to_ocs()` to transform multiple `Path()` objects 
  at once form WCS to OCS  
- NEW: `path.bbox()`, calculate bounding box for multiple `Path()` objects  
- NEW: `path.fit_paths_into_box()`, scale paths to fit into a given box size  
- NEW: `path.from_matplotlib_path()` yields multiple `Path()` objects from a
  matplotlib Path (TextPath).
- NEW: `path.from_qpainter_path()` yields multiple `Path()` objects from a 
  PyQt5 QPainterPath.
- NEW: `path.render_lwpolylines()`, render paths as LWPOLYLINE entities
- NEW: `path.render_polylines2d()`, render paths as 2D POLYLINE entities
- NEW: `path.render_hatches()`, render paths as HATCH entities
- NEW: `path.render_polylines3d()`, render paths as 3D POLYLINE entities
- NEW: `path.render_lines()`, render paths as LINE entities
- NEW: `path.render_splines_and_polylines()`, render paths as SPLINE and 3D POLYLINE entities
- NEW: `path.to_lwpolylines()`, convert paths to LWPOLYLINE entities
- NEW: `path.to_polylines2d()`, convert paths to 2D POLYLINE entities
- NEW: `path.to_hatches()`, convert paths to HATCH entities
- NEW: `path.to_polylines3d()`, convert paths to 3D POLYLINE entities
- NEW: `path.to_lines()`, convert paths to LINE entities
- NEW: `path.to_splines_and_polylines()`, convert paths to SPLINE and 3D POLYLINE entities
- NEW: `path.to_bspline_and_vertices()`, convert paths to B-splines and lists of vertices
- NEW: `path.to_matplotlib_path()`, convert paths to a matplotlib Path
- NEW: `path.to_qpainter_path()`, convert paths to a PyQt5 QPainterPath 
- NEW: `ezdxf.math.quadratic_to_cubic_bezier()`, Bezier3P to Bezier4P converter   
- NEW: `ezdxf.math.bezier_to_bspline()`, Bezier to BSpline converter
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
- DEPRECATED: `Path.from_vertiues()`, replaced by factory `from_vertices()`
- REMOVED: `Path.from_from_hatch_boundary_path()`, replaced by factory `from_hatch()`
- REMOVED: `Path.from_from_hatch_polyline_path()`
- REMOVED: `Path.from_from_hatch_edge_path()`
- REMOVED: `Block.purge()`, unsafe operation

