
News
====

Version 0.8.1 - 2017-04-06

  * NEW: added support for constant ATTRIB/ATTDEF to the INSERT (block reference) entity
  * NEW: added ATTDEF management methods to BlockLayout (has_attdef, get_attdef, get_attdef_text)
  * NEW: added (read/write) properties to ATTDEF/ATTRIB for setting flags (is_const, is_invisible, is_verify, is_preset)

Version 0.8.0 - 2017-03-28

  * added groupby(dxfattrib='', key=None) entity query function, it is supported by all layouts and the query result
    container: Returns a dict, where entities are grouped by a dxfattrib or the result of a key function.
  * added ezdxf.audit() for DXF error checking for drawing created by ezdxf - but not very capable yet
  * dxfattribs in factory functions like add_line(dxfattribs=...), now are copied internally and stay unchanged, so they
    can be reused multiple times without getting modified by ezdxf.
  * removed deprecated Drawing.create_layout() -> Drawing.new_layout()
  * removed deprecated Layouts.create() -> Layout.new()
  * removed deprecated Table.create() -> Table.new()
  * removed deprecated DXFGroupTable.add() -> DXFGroupTable.new()
  * BUFIX in EntityQuery.extend()

Version 0.7.9 - 2017-01-31

  * BUGFIX: lost data if model space and active layout are called \*MODEL_SPACE and \*PAPER_SPACE

Version 0.7.8 - 2017-01-22

  * BUGFIX: HATCH accepts SplineEdges without defined fit points
  * BUGFIX: fixed universal line ending problem in ZipReader()
  * Moved repository to GitHub: https://github.com/mozman/ezdxf.git

Version 0.7.7 - 2016-10-22

  * NEW: repairs malformed Leica Disto DXF R12 files, ezdxf saves a valid DXF R12 file.
  * NEW: added Layout.unlink(entity) method: unlinks an entity from layout but does not delete entity from the drawing database.
  * NEW: added Drawing.add_xref_def(filename, name) for adding external reference definitions
  * CHANGE: renamed parameters for EdgePath.add_ellipse() - major_axis_vector -> major_axis; minor_axis_length -> ratio
    to be consistent to the ELLIPSE entity
  * UPDATE: Entity.tags.new_xdata() and Entity.tags.set_xdata() accept tuples as tags, no import of DXFTag required
  * UPDATE: EntityQuery to support both 'single' and "double" quoted strings - Harrison Katz <harrison@neadwerx.com>
  * improved DXF R13/R14 compatibility

Version 0.7.6 - 2016-04-16

  * NEW: r12writer.py - a fast and simple DXF R12 file/stream writer. Supports only LINE, CIRCLE, ARC, TEXT, POINT,
    SOLID, 3DFACE and POLYLINE. The module can be used without ezdxf.
  * NEW: Get/Set extended data on DXF entity level, add and retrieve your own data to DXF entities
  * NEW: Get/Set app data on DXF entity level (not important for high level users)
  * NEW: Get/Set/Append/Remove reactors on DXF entity level (not important for high level users)
  * CHANGE: using reactors in PdfDefinition for well defined UNDERLAY entities
  * CHANGE: using reactors and IMAGEDEF_REACTOR for well defined IMAGE entities
  * BUGFIX: default name=None in add_image_def()

Version 0.7.5 - 2016-04-03

  * NEW: Drawing.acad_release property - AutoCAD release number for the drawing DXF version like 'R12' or 'R2000'
  * NEW: support for PDFUNDERLAY, DWFUNDERLAY and DGNUNDERLAY entities
  * BUGFIX: fixed broken layout setup in repair routine
  * BUGFIX: support for utf-8 encoding on saving, DXF R2007 and later is saved with UTF-8 encoding
  * CHANGE: Drawing.add_image_def(filename, size_in_pixel, name=None), renamed key to name and set name=None for auto-generated internal image name
  * CHANGE: argument order of Layout.add_image(image_def, insert, size_in_units, rotation=0., dxfattribs=None)

Version 0.7.4 - 2016-03-13

  * NEW: support for DXF entity IMAGE (work in progress)
  * NEW: preserve leading file comments (tag code 999)
  * NEW: writes saving and upgrading comments when saving DXF files; avoid this behavior by setting options.store_comments = False
  * NEW: ezdxf.new() accepts the AutoCAD release name as DXF version string e.g. ezdxf.new('R12') or R2000, R2004, R2007, ...
  * NEW: integrated acadctb.py module from my dxfwrite package to read/write AutoCAD .ctb config files; no docs so far
  * CHANGE: renamed Drawing.groups.add() to new() for consistent name schema for adding new items to tables (public interface)
  * CHANGE: renamed Drawing.<tablename>.create() to new() for consistent name schema for adding new items to tables,
    this applies to all tables: layers, styles, dimstyles, appids, views, viewports, ucs, block_records. (public interface)
  * CHANGE: renamed Layouts.create() to new() for consistent name schema for adding new items to tables (internal interface)
  * CHANGE: renamed Drawing.create_layout() to new_layout() for consistent name schema for adding new items (public interface)
  * CHANGE: renamed factory method <layout>.add_3Dface() to add_3dface()
  * REMOVED: logging and debugging options
  * BUGFIX: fixed attribute definition for align_point in DXF entity ATTRIB (AC1015 and newer)
  * Cleanup DXF template files AC1015 - AC1027, file size goes down from >60kb to ~20kb

Version 0.7.3 - 2016-03-06

  * Quick bugfix release, because ezdxf 0.7.2 can damage DXF R12 files when saving!!!
  * NEW: improved DXF R13/R14 compatibility
  * BUGFIX: create CLASSES section only for DXF versions newer than R12 (AC1009)
  * TEST: converted a bunch of R8 (AC1003) files to R12 (AC1009), AutoCAD didn't complain
  * TEST: converted a bunch of R13 (AC1012) files to R2000 (AC1015), AutoCAD didn't complain
  * TEST: converted a bunch of R14 (AC1014) files to R2000 (AC1015), AutoCAD didn't complain

Version 0.7.2 - 2016-03-05

  * NEW: reads DXF R13/R14 and saves content as R2000 (AC1015) - experimental feature, because of the lack of test data
  * NEW: added support for common DXF attribute line weight
  * NEW: POLYLINE, POLYMESH - added properties is_closed, is_m_closed, is_n_closed
  * BUGFIX: MeshData.optimize() - corrected wrong vertex optimization
  * BUGFIX: can open DXF files without existing layout management table
  * BUGFIX: restore module structure ezdxf.const

Version 0.7.1 - 2016-02-21

  * Supported/Tested Python versions: CPython 2.7, 3.4, 3.5, pypy 4.0.1 and pypy3 2.4.0
  * NEW: read legacy DXF versions older than AC1009 (DXF R12) and saves it as DXF version AC1009.
  * NEW: added methods is_frozen(), freeze(), thaw() to class Layer()
  * NEW: full support for DXF entity ELLIPSE (added add_ellipse() method)
  * NEW: MESH data editor - implemented add_face(vertices), add_edge(vertices), optimize(precision=6) methods
  * BUGFIX: creating entities on layouts works
  * BUGFIX: entity ATTRIB - fixed halign attribute definition
  * CHANGE: POLYLINE (POLYFACE, POLYMESH) - on layer change also change layer of associated VERTEX entities

Version 0.7.0 - 2015-11-26

  * Supported Python versions: CPython 2.7, 3.4, pypy 2.6.1 and pypy3 2.4.0
  * NEW: support for DXF entity HATCH (solid fill, gradient fill and pattern fill), pattern fill with background color supported
  * NEW: support for DXF entity GROUP
  * NEW: VIEWPORT entity, but creating new viewports does not work as expected - just for reading purpose.
  * NEW: support for new common DXF attributes in AC1018 (AutoCAD 2004): true_color, color_name, transparency
  * NEW: support for new common DXF attributes in AC1021 (AutoCAD 2007): shadow_mode
  * NEW: extended custom vars interface
  * NEW: dxf2html - added support for custom properties in the header section
  * NEW: query() supports case insensitive attribute queries by appending an 'i' to the query string, e.g. '\*[layer=="construction"]i'
  * NEW: Drawing.cleanup() - call before saving the drawing but only if necessary, the process could take a while.
  * BUGFIX: query parser couldn't handle attribute names containing '_'
  * CHANGE: renamed dxf2html to pp (pretty printer), usage: py -m ezdxf.pp yourfile.dxf (generates yourfile.html in the same folder)
  * CHANGE: cleanup file structure

Version 0.6.5 - 2015-02-27

  * BUGFIX: custom properties in header section written after $LASTSAVEDBY tag - the only way AutoCAD accepts custom tags

Version 0.6.4 - 2015-02-27

  * NEW: Support for custom properties in the header section - Drawing.header.custom_vars - but so far AutoCAD ignores
    new created custom properties by ezdxf- I don't know why.
  * BUGFIX: wrong DXF subclass for Arc.extrusion (error in DXF Standard)
  * BUGFIX: added missing support files for dxf2html

Version 0.6.3 - 2014-09-10

  * Beta status
  * BUGFIX: Text.get_pos() - dxf attribute error "alignpoint"

Version 0.6.2 - 2014-05-09

  * Beta status
  * NEW: set ``ezdxf.options.compress_default_chunks = True`` to compress unnecessary Sections (like THUMBNAILIMAGE) in
    memory with zlib
  * NEW: Drawing.compress_binary_data() - compresses binary data (mostly code 310) in memory with zlib or set
    ``ezdxf.options.compress_binary_data = True`` to compress binary data of every drawing you open.
  * NEW: support for MESH entity
  * NEW: support for BODY, 3DSOLID and REGION entity, you get the ACIS data
  * CHANGE: Spline() - removed context managers fit_points(), control_points(), knot_values() and weights() and added a
    general context_manager edit_data(), similar to Mesh.edit_data() - unified API
  * CHANGE: MText.buffer() -> MText.edit_data() - unified API (MText.buffer() still exists as alias)
  * CHANGE: refactored internal structure - only two DXF factories remaining:

    - LegacyDXFFactory() for AC1009 (DXF12) drawings
    - ModernDXFFactory() for newer DXF versions except DXF13/14.

  * BUGFIX: LWPolyline.get_rstrip_point() removed also x- and y-coords if zero
  * BUGFIX: opens DXF12 files without handles again
  * BUGFIX: opens DXF12 files with HEADER section but without $ACADVER set

Version 0.6.1 - 2014-05-02

  * Beta status
  * NEW: create new layouts - Drawing.create_layout(name, dxfattribs=None)
  * NEW: delete layouts - Drawing.delete_layout(name)
  * NEW: delete blocks - Drawing.blocks.delete_block(name)
  * NEW: read DXF files from zip archives (its slow).
  * CHANGE: LWPolyline returns always 5-tuples (x, y, start_width, end_width, bulge). start_width, end_width and bulge
    is 0 if not present.
  * NEW: LWPolyline.get_rstrip_points() -> generates points without appending zeros.
  * NEW: LWPolyline.rstrip_points() -> context manager for points without appending zeros.
  * BUGFIX: fixed handle creation bug for DXF12 files without handles, a code 5/105 issue
  * BUGFIX: accept floats as int (thanks to ProE)
  * BUGFIX: accept entities without owner tag (thanks to ProE)
  * improved dxf2html; creates a more readable HTML file; usage: python -m ezdxf.dxf2html filename.dxf

Version 0.6.0 - 2014-04-25

  * Beta status
  * Supported Python versions: CPython 2.7, 3.4 and pypy 2.2.1
  * Refactoring of internal structures
  * CHANGE: appended entities like VERTEX for POLYLINE and ATTRIB for INSERT are linked to the main entity and do
    not appear in layouts, model space or blocks (modelspace.query('VERTEX') is always an emtpy list).
  * CHANGE: refactoring of the internal 2D/3D point representation for reduced memory footprint
  * faster unittests
  * BUGFIX: opens minimalistic DXF12 files
  * BUGFIX: support for POLYLINE new (but undocumented) subclass names: AcDbPolyFaceMesh, AcDbPolygonMesh
  * BUGFIX: support for VERTEX new (but undocumented) subclass names: AcDbFaceRecord, AcDbPolyFaceMeshVertex,
    AcDbPolygonMeshVertex, AcDb3dPolylineVertex
  * CHANGE: Polyline.get_mode() returns new names: AcDb2dPolyline, AcDb3dPolyline, AcDbPolyFaceMesh, AcDbPolygonMesh
  * CHANGE: separated layout spaces - each layout has its own entity space

Version 0.5.2 - 2014-04-15

  * Beta status
  * Supported Python versions: CPython 2.7, 3.3, 3.4 and pypy 2.2.1
  * BUGFIX: ATTRIB definition error for AC1015 and later (error in DXF specs)
  * BUGFIX: entity.dxf_attrib_exists() returned True for unset attribs with defined DXF default values
  * BUGFIX: layout.delete_entity() didn't delete following data entities for INSERT (ATTRIB) & POLYLINE (VERTEX)
  * NEW: delete all entities from layout/block/entities section
  * cleanup DXF template files

Version 0.5.1 - 2014-04-14

  * Beta status
  * Supported Python versions: CPython 2.7, 3.3, 3.4 and pypy 2.2.1
  * BUGFIX: restore Python 2 compatibility (has no list.clear() method); test launcher did not run tests in subfolders,
    because of missing __init__.py files

Version 0.5.0 - 2014-04-13

  * Beta status
  * BUGFIX: Drawing.get_layout_setter() - did not work with entities without DXF attribute *paperspace*
  * NEW: default values for DXF attributes as defined in the DXF standard, this allows usage of optional DXF attributes
    (with defined default values) without check of presence, like *entity.dxf.paperspace*.
  * NEW: DXF entities SHAPE, RAY, XLINE, SPLINE
  * NEW: delete entities from layout/block
  * CHANGE: entity 3DFACE requires 3D coordinates (created by add_3Dface())
  * CHANGE: LWPolyline all methods return points as (x, y, [start_width, [end_width, [bulge]]]) tuples
  * updated docs

Version 0.4.2 - 2014-04-02

  * Beta status
  * Supported Python versions: CPython 2.7, 3.3, 3.4 and pypy 2.1
  * NEW: DXF entities LWPOLYLINE, MTEXT
  * NEW: convenience methods place(), grid(), get_attrib_text() and has_attrib() for the Insert entity
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
