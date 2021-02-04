Version 0.16 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-16.html
- NEW: `ezdxf.render.make_path()` factory function to create `Path()` objects 
  from many DXF entities.
- NEW: `ezdxf.render.has_path_support()` to check if an entity is supported by 
  `make_path()`
- NEW: add-on `text2path`, see [docs](https://ezdxf.mozman.at/docs/addons/text2path.html)
- NEW: support module `bbox`, see [docs](https://ezdxf.mozman.at/docs/bbox.html)
- NEW: support module `disassemble`, see [docs](https://ezdxf.mozman.at/docs/disassemble.html)
- NEW: get clipping path from VIEWPORT entities by `make_path()`
- NEW: `ezdxf.math.Bezier3P`, optimized quadratic Bézier curve construction tool 
- NEW: quadratic Bézier curve support for the `Path()` class 
- NEW: `path.transform_paths()` to transform multiple `Path()` objects at once 
- NEW: `path.bbox()`, calculate bounding box for multiple `Path()` objects  
- NEW: `path.fit_paths_into_box()`, scale paths to fit into a given box size  
- NEW: `path.from_matplotlib_path()` yields multiple `Path()` objects from a 
  matplotlib Path (TextPath) object.  
- DEPRECATED: `Path.from_lwpolyline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_polyline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_spline()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_ellipse()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_arc()`, replaced by factory `make_path()`
- DEPRECATED: `Path.from_circle()`, replaced by factory `make_path()`
