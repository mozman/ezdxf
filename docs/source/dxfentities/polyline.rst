Polyline
========

.. class:: Polyline(GraphicEntity)

The POLYLINE entity is very complex, it's used to build 2D/3D polylines, 3D meshes and 3D polyfaces. For every type
exists a different wrapper class but they all have the same dxftype of POLYLINE. Detect the polyline type by
:meth:`Polyline.get_mode`.

Create 2D polylines in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_polyline2D`.

For 2D entities all points in :ref:`OCS`.

Create 3D polylines in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_polyline3D`.

For 3D entities all points in :ref:`WCS`.

DXF Attributes for Polyline
---------------------------

:ref:`Common DXF attributes for DXF R12`

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Polyline.dxf.elevation

    Elevation point, the X and Y values are always 0, and the Z value is the polyline's elevation (3D Point in
    :ref:`OCS` when 2D, :ref:`WCS` when 3D).

.. attribute:: Polyline.dxf.flags

    Constants defined in :mod:`ezdxf.const`:

    ================================== ===== ====================================
    Polyline.dxf.flags                 Value Description
    ================================== ===== ====================================
    POLYLINE_CLOSED                    1     This is a closed Polyline (or a
                                             polygon mesh closed in the M
                                             direction)
    POLYLINE_MESH_CLOSED_M_DIRECTION   1     equals POLYLINE_CLOSED
    POLYLINE_CURVE_FIT_VERTICES_ADDED  2     Curve-fit vertices have been added
    POLYLINE_SPLINE_FIT_VERTICES_ADDED 4     Spline-fit vertices have been added
    POLYLINE_3D_POLYLINE               8     This is a 3D Polyline
    POLYLINE_3D_POLYMESH               16    This is a 3D polygon mesh
    POLYLINE_MESH_CLOSED_N_DIRECTION   32    The polygon mesh is closed in the
                                             N direction
    POLYLINE_POLYFACE_MESH             64    This Polyline is a polyface mesh
    POLYLINE_GENERATE_LINETYPE_PATTERN 128   The linetype pattern is generated
                                             continuously around the vertices of
                                             this Polyline
    ================================== ===== ====================================

.. attribute:: Polyline.dxf.default_start_width

    Default line start width (float); default=0

.. attribute:: Polyline.dxf.default_end_width

    Default line end width (float); default=0

.. attribute:: Polyline.dxf.m_count

    Polymesh M vertex count (int); default=1

.. attribute:: Polyline.dxf.n_count

    Polymesh N vertex count (int); default=1

.. attribute:: Polyline.dxf.m_smooth_density

    Smooth surface M density (int); default=0

.. attribute:: Polyline.dxf.n_smooth_density

    Smooth surface N density (int); default=0

.. attribute:: Polyline.dxf.smooth_type

    Curves and smooth surface type (int); default=0, see table below

    Constants for *smooth_type* defined in :mod:`ezdxf.const`:

    ========================== =====  =============================
    Polyline.dxf.smooth_type   Value  Description
    ========================== =====  =============================
    POLYMESH_NO_SMOOTH         0      no smooth surface fitted
    POLYMESH_QUADRATIC_BSPLINE 5      quadratic B-spline surface
    POLYMESH_CUBIC_BSPLINE     6      cubic B-spline surface
    POLYMESH_BEZIER_SURFACE    8      Bezier surface
    ========================== =====  =============================

Polyline Attributes
-------------------

.. attribute:: Polyline.is_2d_polyline

    *True* if polyline is a 2D polyline.


.. attribute:: Polyline.is_3d_polyline

    *True* if polyline is a 3D polyline.

.. attribute:: Polyline.is_polygon_mesh

    *True* if polyline is a polygon mesh, see :class:`Polymesh`

.. attribute:: Polyline.is_poly_face_mesh

    *True* if polyline is a poly face mesh, see :class:`Polyface`

.. attribute:: Polyline.is_closed

    *True* if polyline is closed.

.. attribute:: Polyline.is_m_closed

    *True* if polyline (as polymesh) is closed in m direction.

.. attribute:: Polyline.is_n_closed

    *True* if polyline (as polymesh) is closed in n direction.

Polyline Methods
----------------

.. method:: Polyline.get_mode()

    Returns a string: ``AcDb2dPolyline``, ``AcDb3dPolyline``, ``AcDbPolygonMesh`` or ``AcDbPolyFaceMesh``

.. method:: Polyline.m_close()

    Close mesh in M direction (also closes polylines).

.. method:: Polyline.n_close()

    Close mesh in N direction.

.. method:: Polyline.close(m_close, n_close=False)

    Close mesh in M (if *mclose* is *True*) and/or N (if *nclose* is *True*) direction.

.. method:: Polyline.__len__()

    Returns count of vertices.

.. method:: Polyline.__getitem__(pos)

    Get :class:`Vertex` object at position *pos*.

.. method:: Polyline.vertices()

    Iterate over all polyline vertices as :class:`Vertex` objects. (replaces :meth:`Polyline.__iter__`)

.. method:: Polyline.points()

    Iterate over all polyline points as (x, y[, z])-tuples, not as :class:`Vertex` objects.

.. method:: Polyline.append_vertex(point, dxfattribs=None)

    Append a single point as :class:`Vertex` object.

    :param point: point is a (x, y[, z])-tuple.
    :param dxfattribs: dict of DXF attributes for the :class:`Vertex`


.. method:: Polyline.append_vertices(points, dxfattribs=None)

    Append multiple points as :class:`Vertex` objects.

    :param points: iterable of polyline points, each point is a (x, y[, z])-tuple.
    :param dxfattribs: dict of DXF attributes for the :class:`Vertex`


.. method:: Polyline.insert_vertices(pos, points, dxfattribs=None)

    Insert points as :class:`Vertex` objects at position *pos*.

    :param int pos: 0-based insert position
    :param iterable points: iterable polyline points, every point is a tuple.
    :param dxfattribs: dict of DXF attributes for the :class:`Vertex`

.. method:: Polyline.delete_vertices(pos, count=1)

    Delete *count* vertices at position *pos*.

    :param int pos: 0-based insert position
    :param int count: count of vertices to delete


Vertex
======

.. class:: Vertex(GraphicEntity)

   A vertex represents a polyline/mesh point, dxftype is ``VERTEX``, you don't have to create vertices by yourself.

DXF Attributes for Vertex
-------------------------

.. attribute:: Vertex.dxf.location

vertex location (2D/3D Point :ref:`OCS` when 2D, :ref:`WCS` when 3D)

.. attribute:: Vertex.dxf.start_width

line segment start width (float); default=0

.. attribute:: Vertex.dxf.end_width

line segment end width (float); default=0

.. attribute:: Vertex.dxf.bulge

Bulge (float); default=0. The bulge is the tangent of one fourth the included angle for an arc segment, made negative
if the arc goes clockwise from the start point to the endpoint. A bulge of 0 indicates a straight segment, and a bulge
of 1 is a semicircle.

.. attribute:: Vertex.dxf.flags

Constants defined in :mod:`ezdxf.const`:

============================== ======= ===========
Vertex.dxf.flags               Value   Description
============================== ======= ===========
VTX_EXTRA_VERTEX_CREATED       1       Extra vertex created by curve-fitting
VTX_CURVE_FIT_TANGENT          2       curve-fit tangent defined for this vertex. A curve-fit tangent direction of 0 may be omitted from the DXF output, but is significant if this bit is set.
VTX_SPLINE_VERTEX_CREATED      8       spline vertex created by spline-fitting
VTX_SPLINE_FRAME_CONTROL_POINT 16      spline frame control point
VTX_3D_POLYLINE_VERTEX         32      3D polyline vertex
VTX_3D_POLYGON_MESH_VERTEX     64      3D polygon mesh
VTX_3D_POLYFACE_MESH_VERTEX    128     polyface mesh vertex
============================== ======= ===========

.. attribute:: Vertex.dxf.tangent

curve fit tangent direction (float)

.. attribute:: Vertex.dxf.vtx1

index of 1st vertex, if used as face (feature for experts)

.. attribute:: Vertex.dxf.vtx2

index of 2nd vertex, if used as face (feature for experts)

.. attribute:: Vertex.dxf.vtx3

index of 3rd vertex, if used as face (feature for experts)

.. attribute:: Vertex.dxf.vtx4

index of 4th vertex, if used as face (feature for experts)


Polymesh
========

.. class:: Polymesh(Polyline)

A polymesh is a grid of mcount x ncount vertices and every vertex has its own xyz-coordinates.
The :class:`Polymesh` is an extended :class:`Polyline` class, dxftype is also ``POLYLINE`` but
:meth:`~Polyline.get_mode` returns ``AcDbPolygonMesh``.
Create polymeshes in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_polymesh`.

.. method:: Polymesh.get_mesh_vertex(pos)

Get mesh vertex at position *pos* as :class:`Vertex`.

:param pos: 0-based (row, col)-tuple

.. method:: Polymesh.set_mesh_vertex(pos, point, dxfattribs=None)

Set mesh vertex at position *pos* to location *point* and update the dxf attributes of the :class:`Vertex`.

:param pos: 0-based (row, col)-tuple
:param point: vertex coordinates as (x, y, z)-tuple
:param dxfattribs: dict of DXF attributes for the :class:`Vertex`

.. method:: Polymesh.get_mesh_vertex_cache()

Get a :class:`MeshVertexCache` object for this Polymesh. The caching object provides fast access to the location
attributes of the mesh vertices.



.. class:: MeshVertexCache

Cache mesh vertices in a dict, keys are 0-based (row, col)-tuples.

- set vertex location: :code:`cache[row, col] = (x, y, z)`
- get vertex location: :code:`x, y, z = cache[row, col]`

.. attribute:: MeshVertexCache.vertices

Dict of mesh vertices, keys are 0-based (row, col)-tuples. Writing to this dict doesn't change the DXF entity.

.. method:: MeshVertexCache.__getitem__(pos)

Returns the location of :class:`Vertex` at position *pos* as (x, y, z)-tuple

:param tuple pos: 0-based (row, col)-tuple

.. method:: MeshVertexCache.__setitem__(pos, location)

Set the location of :class:`Vertex` at position *pos* to *location*.

:param pos: 0-based (row, col)-tuple
:param location: (x, y, z)-tuple

Polyface
========

.. class:: Polyface(Polyline)

A polyface consist of multiple location independent 3D areas called faces.
The :class:`Polyface` is an extended :class:`Polyline` class, dxftype is also ``POLYLINE`` but
:meth:`~Polyline.get_mode` returns ``AcDbPolyFaceMesh``.
Create polyfaces in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_polyface`.

.. method:: Polyface.append_face(face, dxfattribs=None)

Append one *face*, *dxfattribs* is used for all vertices generated. Appending single faces is very inefficient, if
possible use :meth:`~Polyface.append_faces` to add a list of new faces.

:param face: a tuple of 3 or 4 3D points, a 3D point is a (x, y, z)-tuple
:param dxfattribs: dict of DXF attributes for the :class:`Vertex`

.. method:: Polyface.append_faces(faces, dxfattribs=None)

Append a list of *faces*, *dxfattribs* is used for all vertices generated.

:param tuple faces: a list of faces, a face is a tuple of 3 or 4 3D points, a 3D point is a (x, y, z)-tuple
:param dxfattribs: dict of DXF attributes for the :class:`Vertex`

.. method:: Polyface.faces()

Iterate over all faces, a face is a tuple of :class:`Vertex` objects; yields (vtx1, vtx2, vtx3[, vtx4], face_record)-tuples

.. method:: Polyface.indexed_faces()

Returns a list of all vertices and a generator of :class:`Face()` objects as tuple::

    vertices, faces = polyface.indexed_faces()

.. method:: Polyface.optimize(precision=6)

Rebuilds :class:`Polyface` with vertex optimization. Merges vertices with nearly same vertex locations.
Polyfaces created by *ezdxf* are optimized automatically.

:param int precision: decimal precision for determining identical vertex locations

.. seealso::

    :ref:`tut_polyface`

.. class:: Face

Represents a single face of the :class:`Polyface` entity.

.. attribute:: Face.vertices

List of all :class:`Polyface` vertices (without face_records). (read only attribute)

.. attribute:: Face.face_record

The face forming vertex of type ``AcDbFaceRecord``, contains the indices to the face building vertices. Indices of
the DXF structure are 1-based and a negative index indicates the beginning of an invisible edge.
:attr:`Face.face_record.dxf.color` determines the color of the face. (read only attribute)

.. attribute:: Face.indices

Indices to the face forming vertices as tuple. This indices are 0-base and are used to get vertices from the
list :attr:`Face.vertices`. (read only attribute)

.. method:: Face.__iter__()

Iterate over all face vertices as :class:`Vertex` objects.

.. method:: Face.__len__()

Returns count of face vertices (without face_record).

.. method:: Face.__getitem__(pos)

Returns :class:`Vertex` at position *pos*.

:param int pos: vertex position 0-based

.. method:: Face.points()

Iterate over all face vertex locations as (x, y, z)-tuples.

.. method:: Face.is_edge_visible(pos)

Returns *True* if edge starting at vertex *pos* is visible else *False*.

:param int pos: vertex position 0-based
