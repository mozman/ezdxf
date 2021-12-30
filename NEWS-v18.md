Version 0.18 - 2021-12-xx
-------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-18.html
- NEW: angular dimension rendering support, new factory methods:
  `add_angular_dim_2l()`, `add_angular_dim_3p()`, `add_angular_dim_cra()`, 
  `add_angular_dim_arc()` 
- NEW: arc length dimension rendering support, new factory methods: 
  `add_arc_dim_3p()`, `add_arc_dim_cra()`, `add_arc_dim_arc()`
- NEW: ordinate dimension rendering support, new factory methods: 
  `add_ordinate_dim()`, `add_ordinate_x_dim()`, `add_ordinate_y_dim()`
- NEW: function `ezdxf.tools.text.is_upside_down_text_angle()` in WCS
- NEW: function `ezdxf.tools.text.upright_text_angle()` in WCS
- NEW: helper class `ezdxf.math.ConstructionPolyline` to measure, interpolate and 
  divide polylines and anything that can be approximated or flattened into 
  vertices
- NEW: `ezdxf.gfxattribs.GfxAttribs()` class, [docs](https://ezdxf.mozman.at/docs/tools/gfxattribs.html)
- NEW: `TextEntityAlignment` enum replaces the string based alignment definition
- NEW: method `Text.get_placement()`, replaces `get_pos()` 
- NEW: method `Text.set_placement()`, replaces `set_pos()` 
- NEW: method `Text.get_align_enum()`, replaces `get_align()`
- NEW: method `Text.set_align_enum()`, replaces `set_align()`
- DEPRECATED: method `Text.get_pos()` will be removed in v1.0.0
- DEPRECATED: method `Text.set_pos()` will be removed in v1.0.0
- DEPRECATED: method `Text.get_align()` will be removed in v1.0.0
- DEPRECATED: method `Text.set_align()` will be removed in v1.0.0
 