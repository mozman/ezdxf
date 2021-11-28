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
