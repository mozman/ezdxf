
News
====

Version 0.5.0 - 2014-04-13

  * Beta status
  * BUGFIX: Drawing.get_layout_setter() - did not work with entities without DXF attribute *paperspace*
  * NEW: default values for DXF attributes as defined in the DXF standard, this allows usage of optional DXF attributes
    (with defined default values) without check of presence, like *entity.dxf.paperspace*.
  * NEW: DXF entities Shape, Ray, XLine, Spline
  * NEW: delete entities from layout/drawing
  * CHANGE: entity 3DFACE requires 3D coordinates (created by add_3Dface())
  * CHANGE: LWPolyline all methods return points as (x, y, [start_width, [end_width, [bulge]]]) tuples
  * updated docs

Version 0.4.2 - 2014-04-02

  * Beta status
  * Supported Python versions: CPython 2.7, 3.3, 3.4 and pypy 2.1
  * NEW: DXF entities LWPolyline, MText
  * NEW: convenience methods place(), grid(), get_attrib_text() and has_attrib() to the Insert entity
  * CHANGE: pyparsing as external dependency
  * BUGFIX: iteration over drawing.entities yields full functional entities (correct layout attribute)
  * BUGFIX: install error with pip and missing DXF template files of versions 0.4.0 & 0.4.1

Version 0.3.0 - 2013-07-20

  * Alpha status
  * Supported Python versions: CPython 2.7, 3.3 and pypy 2.0
  * NEW: Entity Query Language
  * NEW: Import data from other DXF files
  * CHANGE: License changed to MIT License

Version 0.1.0 - 2010-03-14

  * Alpha status
  * Initial release
