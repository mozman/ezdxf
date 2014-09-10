
News
====

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
