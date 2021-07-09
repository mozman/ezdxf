Version 0.17 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-17.html
- NEW: column support for MTEXT read and create, but no editing
- NEW: factory method `BaseLayout.add_mtext_static_columns()`
- NEW: factory method `BaseLayout.add_mtext_dynamic_manual_height_columns()`
- NEW: add-on tool `MTextExplode()` to explode MTEXT entities
  into single line TEXT entities and additional LINE entities to emulate 
  strokes, requires the `Matplotlib` package
- NEW: `move_to()` command and multi-path support for the `ezdxf.path.Path` class 
- NEW: regular `make_path()` support for the HATCH entity, returns a multi-path object  
- NEW: regular `make_primitive()` support for the HATCH entity  
- NEW: `text2path.make_path_from_str()` returns a multi-path object  
- NEW: `text2path.make_path_from_enity()` returns a multi-path object  
- NEW: `MPOLYGON` load/write/create support
- NEW: `ezdxf.path.to_mpolygons()` function: Path() to MPOLYGON converter
- NEW: `ezdxf.path.render_mpolygons()` function: render MPOLYGON entities form paths
- NEW: store *ezdxf* and custom metadata in DXF files
- NEW: command `ezdxf browse FILE ...`, PyQt DXF structure browser
- NEW: `dxf2code` add-on: function `black()` and method `Code.black_code_str()` 
  returns the code string formatted by [Black](https://pypi.org/project/black/)
  