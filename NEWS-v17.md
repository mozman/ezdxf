Version 0.17 - dev
------------------

- Release notes: https://ezdxf.mozman.at/release-v0-17.html
- NEW: Column support for MTEXT read and create, but no editing
- NEW: factory method `BaseLayout.add_mtext_static_columns()`
- NEW: factory method `BaseLayout.add_mtext_dynamic_manual_height_columns()`
- NEW: `move_to()` command and multi-path support for the `ezdxf.path.Path` class 
- NEW: regular `make_path()` support for the HATCH entity, returns a multi-path object  
- NEW: regular `make_primitive()` support for the HATCH entity  