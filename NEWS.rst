
News
====

Latest versions of ezdxf (>= 0.9.0) are not Python 2 compatible

Version 0.8.10a0 - dev
----------------------

- BUGFIX release for Python 2 compatible main version 0.8

Version 0.8.9 - 2018-11-28
--------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-8-9.html
- IMPORTANT: Python 2 support will be dropped in ezdxf v0.9.0, because Python 2 support get more and more annoying.
- CHANGE: refactoring of internal tag representation for a smaller memory footprint, but with some speed penalty
- NEW: packed data for LWPOLYLINE points, faster __getitem__;  added __setitem__, __delitem__, insert() and append()
  methods; renamed discard_points() in clear(); removed get_rstrip_points() and ctx manager rstrip_points();
  user defined point format;
- NEW: packed data for SPLINE, knots, weights, fit- and control points are stored as array.array();
  Spline.get_knot_values(), Spline.get_weights(), Spline.get_control_points() and Spline.get_fit_points() are deprecated,
  direct access to this attributes by Spline.knot_values, Spline.weights, Spline.control_points and Spline.fit_points,
  all attributes with a list-like interface. Knot, control point and fit point counter updated automatically,
  therefore counters are read only now.
- NEW: packed data for MESH, vertices, faces, edges and edge crease values stored as array.array(), high level interface unchanged
- NEW: Drawing.layouts_and_blocks(), iterate over all layouts (mode space and paper space) and all block definitions.
- NEW: Drawing.chain_layouts_and_blocks(), chain entity spaces of all layouts and blocks. Yields an iterator for all
  entities in all layouts and blocks
- NEW: Drawing.query(), entity query over all layouts and blocks
- NEW: Drawing.groupby(), groups DXF entities of all layouts and blocks by an DXF attribute or a key function
- NEW: Layout.set_redraw_order() and Layout.get_redraw_order(), to change redraw order of entities in model space and
  paper space layouts
- NEW: BlockLayout.is_layout_block, True if block is a model space or paper space block definition
- NEW: ezdxf.algebra.Arc helper class to create arcs from 2 points and an angle or radius, or from 3 points
- NEW: ezdxf.algebra.Arc.add_to_layout() with UCS support to create 3D arcs
- NEW: rename paper space layouts by Drawing.layouts.rename(old_name, new_name)
- NEW: Basic support for embedded objects (new in AutoCAD 2018), ezdxf reads and writes the embedded data as it is,
  no interpretation no modification, just enough to not break DXF files with embedded objects at saving.
- CHANGE: Drawing.blocks.delete_block(name, safe=True), new parameter save, check if block is still referenced
  (raises DXFValueError)
- CHANGE: Drawing.blocks.delete_all_blocks(safe=True), if parameter safe is True, do not delete blocks that are still referenced
- BUGFIX: invalid CLASS definition for DXF version R2000 (AC1015) fixed, bug was only triggered at upgrading from R13/R14 to R2000
- BUGFIX: fixed broken Viewport.AcDbViewport property
- `Basic` read support for many missing DXF entities/objects

    - ACAD_PROXY_GRAPHIC
    - HELIX
    - LEADER
    - LIGHT
    - MLEADER (incomplete)
    - MLINE (incomplete)
    - OLEFRAME
    - OLE2FRAME
    - SECTION
    - TABLE (incomplete)
    - TOLERANCE
    - WIPEOUT
    - ACAD_PROXY_OBJECT
    - DATATABLE
    - DICTIONARYVAR
    - DIMASSOC
    - FIELD (incomplete)
    - FIELDLIST (not documented by Autodesk)
    - IDBUFFER
    - LAYER_FILTER
    - MATERIAL
    - MLEADERSTYLE
    - MLINESTYLE
    - SORTENTSTABLE
    - SUN
    - SUNSTUDY (incomplete) (no real world DXF files with SUNSTUDY for testing available)
    - TABLESTYLE (incomplete)
    - VBA_PROJECT (no real world DXF files with embedded VBA for testing available)
    - VISUALSTYLE
    - WIPEOUTVARIABLES
    - for all unsupported entities/objects exist only raw DXF tag support

Version 0.8.8 - 2018-04-02
--------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-8-8.html
- NEW: read/write support for GEODATA entity
- NEW: read/(limited)write support for SURFACE, EXTRUDEDSURFACE, REVOLVEDSURFACE, LOFTEDSURFACE and SWEPTSURFACE entity
- NEW: support for extension dictionaries
- NEW: add_spline_control_frame(), create and add B-spline control frame from fit points
- NEW: add_spline_approx(), approximate B-spline by a reduced count of control points
- NEW: ezdxf.setup_linetypes(dwg), setup standard line types
- NEW: ezdxf.setup_styles(dwg), setup standard text styles
- NEW: LWPolyline.vertices() yields all points as (x, y) tuples in OCS, LWPolyline.dxf.elevation is the z-axis value
- NEW: LWPolyline.vertices_in_wcs() yields all points as (x, y, z) tuples in WCS
- NEW: basic __str__()  and __repr__() support for DXF entities, returns just DXF type and handle
- NEW: bulge related function in module ezdxf.algebra.bulge
- NEW: Object Coordinate System support by DXFEntity.ocs() and OCS() class in module ezdxf.algebra
- NEW: User Coordinate System support by UCS() class in module ezdxf.algebra
- CHANGE: DXFEntity.set_app_data() and Entity.set_xdata accept also list of tuples as tags, DXFTag() is not required
- BUGFIX: entity structure validator excepts group code >= 1000 before XDATA section (used in AutoCAD Civil 3D and AutoCAD Map 3D)

Version 0.8.7 - 2018-03-04
--------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-8-7.html
- NEW: entity.get_layout() returns layout in which entity resides or None if unassigned
- NEW: copy any DXF entity by entity.copy() without associated layout, add copy to any layout you want, by
  layout.add_entity().
- NEW: copy entity to another layout by entity.copy_to_layout(layout)
- NEW: move entity from actual layout to another layout by entity.move_to_layout(layout)
- NEW: support for splines by control points: add_open_spline(), add_closed_spline(), add_rational_spline(),
  add_closed_rational_spline()
- NEW: bspline_control_frame() calculates B-spline control points from fit points, but not the same as AutoCAD
- NEW: R12Spline add-on, 2d B-spline with control frame support by AutoCAD, but curve is just an approximated POLYLINE
- NEW: added entity.get_flag_state() and entity.set_flag_state() for easy access to binary coded flags
- NEW: set new $FINGERPRINTGUID for new drawings
- NEW: set new $VERSIONGUID on saving a drawing
- NEW: improved IMAGE support, by adding RASTERVARIABLES entity, use Drawing.set_raster_variables(frame, quality, units)
- BUGFIX: closing user defined image boundary path automatically, else AutoCAD crashes

Version 0.8.6 - 2018-02-17
--------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-8-6.html
- NEW: ezdxf project website: https://ezdxf.mozman.at/
- CHANGE: create all missing tables of the TABLES sections for DXF R12
- BUGFIX: entities on new layouts will be saved
- NEW: Layout.page_setup() and correct 'main' viewport for DXF R2000+; For DXF R12 page_setup() exists, but does not
  provide useful results. Page setup for DXF R12 is still a mystery to me.
- NEW: Table(), MText(), Ellipse(), Spline(), Bezier(), Clothoid(), LinearDimension(), RadialDimension(),
  ArcDimension() and AngularDimension() composite objects from dxfwrite as add-ons, these add-ons support DXF R12
- NEW: geometry builder as add-ons: MeshBuilder(), MeshVertexMerger(), MengerSponge(), SierpinskyPyramid(), these
  add-ons require DXF R2000+ (MESH entity)
- BUGFIX: fixed invalid implementation of context manager for r12writer

Version 0.8.5 - 2018-01-28
--------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-8-5.html
- CHANGE: block names are case insensitive 'TEST' == 'Test' (like AutoCAD)
- CHANGE: table entry (layer, linetype, style, dimstyle, ...) names are case insensitive 'TEST' == 'Test' (like AutoCAD)
- CHANGE: raises DXFInvalidLayerName() for invalid characters in layer names: <>/\":;?*|=`
- CHANGE: audit process rewritten
- CHANGE: skip all comments, group code 999
- CHANGE: removed compression for unused sections (THUMBNAILSECTION, ACDSDATA)
- NEW: write DXF R12 files without handles: set dwg.header['$HANDLING']=0, default value is 1
- added subclass marker filter for R12 and prior files in legacy_mode=True (required for malformed DXF files)
- removed special check for Leica Disto Unit files, use readfile(filename, legacy_mode=True) (malformed DXF R12 file,
  see previous point)

Version 0.8.4 - 2018-01-14
--------------------------

- Release notes: https://ezdxf.mozman.at/release-v0-8-4.html
- NEW: Support for complex line types with text or shapes
- NEW: DXF file structure validator at SECTION level, tags outside of sections will be removed
- NEW: Basic read support for DIMENSION
- CHANGE: improved exception management, in the future ezdxf should only raise exceptions inherited from DXFError for
  DXF related errors, previous exception classes still work

    - DXFValueError(DXFError, ValueError)
    - DXFKeyError(DXFError, KeyError)
    - DXFAttributeError(DXFError, AttributeError)
    - DXFIndexError(DXFError, IndexError)
    - DXFTableEntryError(DXFValueError)

- speedup low level tag reader around 5%, and speedup tag compiler around 5%

Version 0.8.3 - 2018-01-02
--------------------------

- CHANGE: Lwpolyline - suppress yielding z coordinates if they exists (DXFStructureError: z coordinates are not defined in the DXF standard)
- NEW: setup creates a script called 'dxfpp' (DXF Pretty Printer) in the Python script folder
- NEW: basic support for DXF format AC1032 introduced by AutoCAD 2018
- NEW: ezdxf use logging and writes all logs to a logger called 'ezdxf'. Logging setup is the domain of the application!
- NEW: warns about multiple block definitions with the same name in a DXF file. (DXFStructureError)
- NEW: legacy_mode parameter in ezdxf.read() and ezdxf.readfile(): tries do fix coordinate order in LINE
  entities (10, 11, 20, 21) by the cost of around 5% overall speed penalty at DXF file loading

Version 0.8.2 - 2017-05-01
--------------------------

- NEW: Insert.delete_attrib(tag) - delete ATTRIB entities from the INSERT entity
- NEW: Insert.delete_all_attribs() - delete all ATTRIB entities from the INSERT entity
- BUGFIX: setting attribs_follow=1 at INSERT entity before adding an attribute entity works

Version 0.8.1 - 2017-04-06
--------------------------

- NEW: added support for constant ATTRIB/ATTDEF to the INSERT (block reference) entity
- NEW: added ATTDEF management methods to BlockLayout (has_attdef, get_attdef, get_attdef_text)
- NEW: added (read/write) properties to ATTDEF/ATTRIB for setting flags (is_const, is_invisible, is_verify, is_preset)

Version 0.8.0 - 2017-03-28
--------------------------

- added groupby(dxfattrib='', key=None) entity query function, it is supported by all layouts and the query result
  container: Returns a dict, where entities are grouped by a dxfattrib or the result of a key function.
- added ezdxf.audit() for DXF error checking for drawings created by ezdxf - but not very capable yet
- dxfattribs in factory functions like add_line(dxfattribs=...), now are copied internally and stay unchanged, so they
  can be reused multiple times without getting modified by ezdxf.
- removed deprecated Drawing.create_layout() -> Drawing.new_layout()
- removed deprecated Layouts.create() -> Layout.new()
- removed deprecated Table.create() -> Table.new()
- removed deprecated DXFGroupTable.add() -> DXFGroupTable.new()
- BUFIX in EntityQuery.extend()