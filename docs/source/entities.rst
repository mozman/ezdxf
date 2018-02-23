Common Base Class
=================

.. class:: GraphicEntity

   Common base class for all graphic entities.

.. attribute:: GraphicEntity.dxf

   (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
   :code:`entity.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
   writeable.

.. attribute:: GraphicEntity.dxftype

   (read only) Get the DXF type string, like ``LINE`` for the line entity.

.. attribute:: GraphicEntity.handle

   (read only) Get the entity handle. (feature for experts)

.. attribute:: GraphicEntity.drawing

   (read only) Get the associated drawing.

.. attribute:: GraphicEntity.dxffactory

   (read only) Get the associated DXF factory. (feature for experts)

.. attribute:: GraphicEntity.rgb

   (read/write) Get/Set true color as RGB-Tuple. This attribute does not exist in DXF AC1009 (R12) entities, the
   attribute exists in DXF AC1015 entities but does not work (raises :class:`ValueError`), requires at least DXF Version
   AC1018 (AutoCAD R2004). usage: :code:`entity.rgb = (30, 40, 50)`;

.. attribute:: GraphicEntity.transparency

   (read/write) Get/Set transparency value as float. This attribute does not exist in DXF AC1009 (R12) entities, the
   attribute exists in DXF AC1015 entities but does not work (raises :class:`ValueError`), requires at least DXF Version
   AC1018 (AutoCAD R2004). Value range 0.0 to 1.0 where 0.0 means entity is opaque and 1.0 means entity is 100%
   transparent (invisible). This is the recommend method to get/set transparency values, when ever possible do not use
   the DXF low level attribute :attr:`entity.dxf.transparency`

.. method:: GraphicEntity.copy()

   Deep copy of DXFEntity with new handle and duplicated linked entities (VERTEX, ATTRIB, SEQEND).
   The new entity is not included in any layout space, so the owner tag is set to '0' for undefined owner/layout.

   Use :meth:`Layout.add_entity()` to add the duplicated entity to a layout, layout can be the model space, a paper
   space layout or a block layout.

   This is not a deep copy in the meaning of Python, because handle, link and owner is changed.

.. method:: GraphicEntity.copy_to_layout(layout)

   Duplicate entity and add new entity to *layout*.

.. method:: GraphicEntity.move_to_layout(layout, source=None)

   Move entity from actual layout to *layout*. *Source* has to be specified if the entity resides in a block layout,
   *source* is not required if the entity resides in the model space or in a paper space layout.

.. method:: GraphicEntity.get_dxf_attrib(key, default=ValueError)

   Get DXF attribute *key*, returns *default* if key doesn't exist, or raise
   :class:`ValueError` if *default* is :class:`ValueError` and no DXF default
   value is defined::

        layer = entity.get_dxf_attrib("layer")
        # same as
        layer = entity.dxf.layer

.. method:: GraphicEntity.set_dxf_attrib(key, value)

   Set DXF attribute *key* to *value*::

       entity.set_dxf_attrib("layer", "MyLayer")
       # same as
       entity.dxf.layer = "MyLayer"

.. method:: GraphicEntity.del_dxf_attrib(key)

   Delete/remove DXF attribute *key*. Raises :class:`AttributeError` if *key* isn't supported.

.. method:: GraphicEntity.dxf_attrib_exists(key)

   Returns *True* if DXF attrib *key* really exists else *False*. Raises :class:`AttributeError` if *key* isn't supported

.. method:: GraphicEntity.supported_dxf_attrib(key)

   Returns *True* if DXF attrib *key* is supported by this entity else *False*. Does not grant that attrib
   *key* really exists.

.. method:: GraphicEntity.valid_dxf_attrib_names(key)

   Returns a list of supported DXF attribute names.

.. _Common DXF attributes for DXF R12:

Common DXF attributes for DXF R12
=================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

=========== ===========
DXFAttr     Description
=========== ===========
handle      DXF handle (feature for experts)
layer       layer name as string; default=0
linetype    linetype as string, special names BYLAYER, BYBLOCK; default=BYLAYER
color       dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER; default=256
paperspace  0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an
            entity to a layout (feature for experts); default=0
extrusion   extrusion direction as 3D point; default=(0, 0, 1)
=========== ===========

.. _Common DXF attributes for DXF R13 or later:

Common DXF attributes for DXF R13 or later
==========================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

============= ===========
DXFAttr       Description
============= ===========
handle        DXF handle (feature for experts)
owner         handle to owner, it's a BLOCK_RECORD entry (feature for experts)
layer         layer name as string; default = 0
linetype      linetype as string, special names BYLAYER, BYBLOCK; default=BYLAYER
color         dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER; default= 256
lineweight    lineweight enum value. Stored and moved around as a 16-bit integer.
ltscale       line type scale as float; default=1.0
invisible     1 for invisible, 0 for visible; default=0
paperspace    0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an
              entity to a layout (feature for experts); default=0
extrusion     extrusion direction as 3D point; default=(0, 0, 1)
thickness     entity thickness as float; default=0
true_color    true color value as int 0x00RRGGBB, requires DXF Version AC1018 (AutoCAD R2004)
color_name    color name as string, requires DXF Version AC1018 (AutoCAD R2004)
transparency  transparency value as int, 0x020000TT 0x00 = 100% transparent / 0xFF = opaque, requires DXF Version AC1018
              (AutoCAD R2004)
shadow_mode   as int; 0 = Casts and receives shadows, 1 = Casts shadows, 2 = Receives shadows, 3 = Ignores shadows;
              requires DXF Version AC1021 (AutoCAD R2007)
============= ===========


Line
====

.. class:: Line(GraphicEntity)

   A line form *start* to *end*, *dxftype* is ``LINE``.
   Create lines in layouts and blocks by factory function :meth:`~Layout.add_line`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
start       R12     start point of line (2D/3D Point)
end         R12     end point of line (2D/3D Point)
=========== ======= ===========

Point
=====

.. class:: Point(GraphicEntity)

   A point at location *point*, *dxftype* is ``POINT``.
   Create points in layouts and blocks by factory function :meth:`~Layout.add_point`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
location    R12     location of the point (2D/3D Point)
=========== ======= ===========

Circle
======

.. class:: Circle(GraphicEntity)

   A circle at location *center* and *radius*, *dxftype* is ``CIRCLE``.
   Create circles in layouts and blocks by factory function :meth:`~Layout.add_circle`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
center      R12     center point of circle (2D/3D Point)
radius      R12     radius of circle (float)
=========== ======= ===========

Arc
===

.. class:: Arc(GraphicEntity)

   An arc at location *center* and *radius* from *start_angle* to *end_angle*, *dxftype* is ``ARC``. The arc goes from
   *start_angle* to *end_angle* in *counter clockwise* direction. Create arcs in layouts and blocks by factory function
   :meth:`~Layout.add_arc`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
center      R12     center point of arc (2D/3D Point)
radius      R12     radius of arc (float)
start_angle R12     start angle in degrees (float)
end_angle   R12     end angle in degrees (float)
=========== ======= ===========

Ellipse
=======

.. class:: Ellipse(GraphicEntity)

   Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``ELLIPSE``.

   An ellipse with center point at location *center* and a major axis *major_axis* as vector. *ratio* is the ratio of
   minor axis to major axis. *start_param* and *end_param* defines start and end point of the ellipse, a full ellipse
   goes from 0 to 2*pi. The ellipse goes from start to end param in *counter clockwise* direction. Create ellipses in
   layouts and blocks by factory function :meth:`~Layout.add_ellipse`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
center      R13     center point of circle (2D/3D Point)
major_axis  R13     Endpoint of major axis, relative to the center (tuple of float)
ratio       R13     Ratio of minor axis to major axis (float)
start_param R13     Start parameter (this value is 0.0 for a full ellipse) (float)
end_param   R13     End parameter (this value is 2*pi for a full ellipse) (float)
=========== ======= ===========

Text
====

.. class:: Text(GraphicEntity)

    A simple one line text, dxftype is ``TEXT``. Text height is in drawing units and defaults to 1, but it depends on
    the rendering software what you really get. Width is a scaling factor, but it is not defined what is scaled (I
    assume the text height), but it also depends on the rendering software what you get. This is one reason why DXF and
    also DWG are not reliable for exchanging exact styling, they are just reliable for exchanging exact geometry.
    Create text in layouts and blocks by factory function :meth:`~Layout.add_text`.

===================== ======= ===========
DXFAttr               Version Description
===================== ======= ===========
text                  R12     the content text itself (str)
insert                R12     first alignment point of text (2D/3D Point), relevant for the adjustments ``LEFT``,
                              ``ALIGN`` and ``FIT``.
align_point           R12     second alignment point of text (2D/3D Point), if the justification is anything other than
                              ``LEFT``, the second alignment point specify also the first alignment
                              point: (or just the second alignment point for ``ALIGN`` and ``FIT``)
height                R12     text height in drawing units (float); default=1
rotation              R12     text rotation in degrees (float); default=0
oblique               R12     text oblique angle (float); default=0
style                 R12     text style name (str); default=``STANDARD``
width                 R12     width scale factor (float); default=1
halign                R12     horizontal alignment flag (int), use :meth:`Text.set_pos` and :meth:`Text.get_align`; default=0
valign                R12     vertical alignment flag (int), use :meth:`Text.set_pos` and :meth:`Text.get_align`; default=0
text_generation_flag  R12     text generation flags (int)
                               - 2 = text is backward (mirrored in X)
                               - 4 = text is upside down (mirrored in Y)
===================== ======= ===========

.. method:: Text.set_pos(p1, p2=None, align=None)

   :param p1: first alignment point as (x, y[, z])-tuple
   :param p2: second alignment point as (x, y[, z])-tuple, required for ``ALIGNED`` and ``FIT`` else ignored
   :param str align: new alignment, ``None`` for preserve existing alignment.

   Set text alignment, valid positions are:

   ============   =============== ================= =====
   Vert/Horiz     Left            Center            Right
   ============   =============== ================= =====
   Top            ``TOP_LEFT``    ``TOP_CENTER``    ``TOP_RIGHT``
   Middle         ``MIDDLE_LEFT`` ``MIDDLE_CENTER`` ``MIDDLE_RIGHT``
   Bottom         ``BOTTOM_LEFT`` ``BOTTOM_CENTER`` ``BOTTOM_RIGHT``
   Baseline       ``LEFT``        ``CENTER``         ``RIGHT``
   ============   =============== ================= =====

   Special alignments are, ``ALIGNED`` and ``FIT``, they require a second alignment point, the text
   is justified with the vertical alignment *Baseline* on the virtual line between these two points.

   =========== ===========
   Alignment   Description
   =========== ===========
   ``ALIGNED`` Text is stretched or compressed to fit exactly between *p1* and *p2* and the text height is also adjusted to preserve height/width ratio.
   ``FIT``     Text is stretched or compressed to fit exactly between *p1* and *p2* but only the text width is
               adjusted, the text height is fixed by the *height* attribute.
   ``MIDDLE``  also a *special* adjustment, but the result is the same as for ``MIDDLE_CENTER``.
   =========== ===========

.. method:: Text.get_pos()

   Returns a tuple (*align*, *p1*, *p2*), *align* is the alignment method, *p1* is the alignment point, *p2* is only
   relevant if *align* is ``ALIGNED`` or ``FIT``, else it's *None*.

.. method:: Text.get_align()

   Returns the actual text alignment as string, see tables above.

.. method:: Text.set_align(align='LEFT')

   Just for experts: Sets the text alignment without setting the alignment points, set adjustment points *insert*
   and *alignpoint* manually.


Polyline
========

.. class:: Polyline(GraphicEntity)

    The *POLYLINE* entity is very complex, it's use to build 2D/3D polylines, 3D meshes and 3D polyfaces. For every type
    exists a different wrapper class but they all have the same dxftype of ``POLYLINE``. Detect the polyline type by
    :meth:`Polyline.get_mode`.

    Create 2D polylines in layouts and blocks by factory function :meth:`~Layout.add_polyline2D`.

    Create 3D polylines in layouts and blocks by factory function :meth:`~Layout.add_polyline3D`.

===================== ======= ===========
DXFAttr               Version Description
===================== ======= ===========
elevation             R12     elevation point, the X and Y values are always 0, and the Z value is the polyline's elevation (3D Point)
flags                 R12     polyline flags (int), see table below
default_start_width   R12     default line start width (float); default=0
default_end_width     R12     default line end width (float); default=0
m_count               R12     polymesh M vertex count (int); default=1
n_count               R12     polymesh N vertex count (int); default=1
m_smooth_density      R12     smooth surface M density (int); default=0
n_smooth_density      R12     smooth surface N density (int); default=0
smooth_type           R12     Curves and smooth surface type (int); default=0, see table below
===================== ======= ===========

Polyline constants for *flags* defined in :mod:`ezdxf.const`:

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

Polymesh constants for *smooth_type* defined in :mod:`ezdxf.const`:

======================== =====  =============================
Polyline.dxf.smooth_type Value  Description
======================== =====  =============================
POLYMESH_NO_SMOOTH       0      no smooth surface fitted
POLYMESH_QUADRIC_BSPLINE 5      quadratic B-spline surface
POLYMESH_CUBIC_BSPLINE   6      cubic B-spline surface
POLYMESH_BEZIER_SURFACE  8      Bezier surface
======================== =====  =============================

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

   Get :class:`Vertex` object at position *pos*. Very slow!!!. Vertices are organized as linked list, so it is
   faster to work with a temporary list of vertices: :code:`list(polyline.vertices())`.

.. method:: Polyline.vertices()

   Iterate over all polyline vertices as :class:`Vertex` objects. (replaces :meth:`Polyline.__iter__`)

.. method:: Polyline.points()

   Iterate over all polyline points as (x, y[, z])-tuples, not as :class:`Vertex` objects.

.. method:: Polyline.append_vertices(points, dxfattribs=None)

   Append points as :class:`Vertex` objects.

   :param points: iterable polyline points, every point is a (x, y[, z])-tuple.
   :param dxfattribs: dict of DXF attributes for the :class:`Vertex`

.. method:: Polyline.insert_vertices(pos, points, dxfattribs=None)

   Insert points as :class:`Vertex` objects at position *pos*.

   :param int pos: 0-baesd insert position
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

=================== ======= ===========
DXFAttr             Version Description
=================== ======= ===========
location            R12     vertex location (2D/3D Point)
start_width         R12     line segment start width (float); default=0
end_width           R12     line segment end width (float); default=0
bulge               R12     Bulge (float); default=0. The bulge is the tangent of one fourth the included angle for an arc segment, made negative if the arc goes clockwise from the start point to the endpoint. A bulge of 0 indicates a straight segment, and a bulge of 1 is a semicircle.
flags               R12     vertex flags (int), see table below.
tangent             R12     curve fit tangent direction (float)
vtx1                R12     index of 1st vertex, if used as face (feature for experts)
vtx2                R12     index of 2nd vertex, if used as face (feature for experts)
vtx3                R12     index of 3rd vertex, if used as face (feature for experts)
vtx4                R12     index of 4th vertex, if used as face (feature for experts)
=================== ======= ===========

Vertex constants for *flags* defined in :mod:`ezdxf.const`:

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

Polymesh
========

.. class:: Polymesh(Polyline)

   A polymesh is a grid of mcount x ncount vertices and every vertex has its own xyz-coordinates.
   The :class:`Polymesh` is an extended :class:`Polyline` class, dxftype is also ``POLYLINE`` but
   :meth:`~Polyline.get_mode` returns ``AcDbPolygonMesh``.
   Create polymeshes in layouts and blocks by factory function :meth:`~Layout.add_polymesh`.

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
   Create polyfaces in layouts and blocks by factory function :meth:`~Layout.add_polyface`.

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

Solid
=====

.. class:: Solid(GraphicEntity)

   A solid filled triangle or quadrilateral, *dxftype* is ``SOLID``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
   Create solids in layouts and blocks by factory function :meth:`~Layout.add_solid`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
vtx0        R12     location of the 1. point (2D/3D Point)
vtx1        R12     location of the 2. point (2D/3D Point)
vtx2        R12     location of the 3. point (2D/3D Point)
vtx3        R12     location of the 4. point (2D/3D Point)
=========== ======= ===========

Trace
=====

.. class:: Trace(GraphicEntity)

   A Trace is solid filled triangle or quadrilateral, *dxftype* is ``TRACE``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`). I don't know the difference
   between SOLID and TRACE.
   Create traces in layouts and blocks by factory function :meth:`~Layout.add_trace`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
vtx0        R12     location of the 1. point (2D/3D Point)
vtx1        R12     location of the 2. point (2D/3D Point)
vtx2        R12     location of the 3. point (2D/3D Point)
vtx3        R12     location of the 4. point (2D/3D Point)
=========== ======= ===========

3DFace
======

.. class:: 3DFace(GraphicEntity)

   (This is not a valid Python name, but it works, because all classes
   described here, do not exist in this simple form.)

   A 3DFace is real 3D solid filled triangle or quadrilateral, *dxftype* is ``3DFACE``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
   Create 3DFaces in layouts and blocks by factory function :meth:`~Layout.add_3dface`.

============== ======= ===========
DXFAttr        Version Description
============== ======= ===========
vtx0           R12     location of the 1. point (3D Point)
vtx1           R12     location of the 2. point (3D Point)
vtx2           R12     location of the 3. point (3D Point)
vtx3           R12     location of the 4. point (3D Point)
invisible_edge R12     invisible edge flag (int, default=0)

                       - 1 = first edge is invisible
                       - 2 = second edge is invisible
                       - 4 = third edge is invisible
                       - 8 = fourth edge is invisible

                       Combine values by adding them, e.g. 1+4 = first and third edge is invisible.
============== ======= ===========

LWPolyline
==========

.. class:: LWPolyline(GraphicEntity)

   Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``LWPOLYLINE``.

   A lightweight polyline is defined as a single graphic entity. The :class:`LWPolyline` differs from the old-style
   :class:`Polyline`, which is defined as a group of subentities. :class:`LWPolyline` display faster (in AutoCAD) and
   consume less disk space and RAM. Create :class:`LWPolyline` in layouts and blocks by factory function
   :meth:`~Layout.add_lwpolyline`. LWPolylines are planar elements, therefore all coordinates have no value for the
   z axis.

.. seealso::

    :ref:`tut_lwpolyline`

===================== ======= ===========
DXFAttr               Version Description
===================== ======= ===========
elevation             R13     z-axis value in WCS is the polyline elevation (float), default=0
flags                 R13     polyline flags (int), see table below
const_width           R13     constant line width (float), default=0
count                 R13     number of vertices
===================== ======= ===========

LWPolyline constants for *flags* defined in :mod:`ezdxf.const`:

============================== ======= ===========
LWPolyline.dxf.flags           Value   Description
============================== ======= ===========
LWPOLYLINE_CLOSED              1       polyline is closed
LWPOLYLINE_PLINEGEN            128     ???
============================== ======= ===========

.. attribute:: LWPolyline.closed

   *True* if polyline is closed else *False*.  A closed polyline has a connection from the last vertex
   to the first vertex. (read/write)

.. method:: LWPolyline.get_points()

   Returns all polyline points as list of tuples (x, y, start_width, end_width, bulge).

   start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present).

.. method:: LWPolyline.get_rstrip_points()

   Generates points without appending zeros: yields (x1, y1), (x2, y2) instead of (x1, y1, 0, 0, 0), (x2, y2, 0, 0, 0).

.. method:: LWPolyline.set_points(points)

   Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
   Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

.. method:: LWPolyline.points()

   Context manager for polyline points. Returns a list of tuples (x, y, start_width, end_width, bulge)

   start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present). Setting/Appending
   points accepts (x, y, [start_width, [end_width, [bulge]]]) tuples. Set start_width, end_width to 0 to be ignored
   (x, y, 0, 0, bulge).

.. method:: LWPolyline.rstrip_points()

   Context manager for polyline points without appending zeros.

.. method:: LWPolyline.append_points(points)

   Append additional *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.
   Set start_width, end_width to 0 to be ignored (x, y, 0, 0, bulge).

.. method:: LWPolyline.discard_points()

   Remove all points.

.. method:: LWPolyline.__len__()

   Number of polyline vertices.

.. method:: LWPolyline.__getitem__(index)

   Get point at position *index* as (x, y, start_width, end_width, bulge) tuple. Actual implementation is very slow!
   start_width, end_width and bulge is 0 if not present (0 is the DXF default value if not present).

MText
=====

.. class:: MText(GraphicEntity)

   Introduced in AutoCAD R13 (DXF version AC1012), extended in AutoCAD 2007 (DXF version AC1021), *dxftype* is ``MTEXT``.

   Multiline text fits a specified width but can extend vertically to an indefinite length. You can format individual
   words or characters within the MText. Create :class:`MText` in layouts and blocks by factory function
   :meth:`~Layout.add_mtext`.

.. seealso::

    :ref:`tut_mtext`

===================== ======= ===========
DXFAttr               Version Description
===================== ======= ===========
insert                R13     Insertion point (3D Point)
char_height           R13     initial text height (float); default=1.0
width                 R13     reference rectangle width (float)
attachment_point      R13     attachment point (int), see table below
flow_direction        R13     text flow direction (int), see table below
style                 R13     text style (string); default='STANDARD'
text_direction        R13     x-axis direction vector in WCS (3D Point); default=(1, 0, 0); if *rotation* and *text_direction* are present, *text_direction* wins
rotation              R13     text rotation in degrees (float); default=0
line_spacing_style    R13     line spacing style (int), see table below
line_spacing_factor   R13     percentage of default (3-on-5) line spacing to be applied. Valid values range from 0.25 to 4.00 (float)
===================== ======= ===========

MText constants for *attachment_point* defined in :mod:`ezdxf.const`:

============================== =======
MText.dxf.attachment_point     Value
============================== =======
MTEXT_TOP_LEFT                 1
MTEXT_TOP_CENTER               2
MTEXT_TOP_RIGHT                3
MTEXT_MIDDLE_LEFT              4
MTEXT_MIDDLE_CENTER            5
MTEXT_MIDDLE_RIGHT             6
MTEXT_BOTTOM_LEFT              7
MTEXT_BOTTOM_CENTER            8
MTEXT_BOTTOM_RIGHT             9
============================== =======

MText constants for *flow_direction* defined in :mod:`ezdxf.const`:

============================== ======= ===========
MText.dxf.flow_direction       Value   Description
============================== ======= ===========
MTEXT_LEFT_TO_RIGHT            1       left to right
MTEXT_TOP_TO_BOTTOM            3       top to bottom
MTEXT_BY_STYLE                 5       by style (the flow direction is inherited from the associated text style)
============================== ======= ===========

MText constants for *line_spacing_style* defined in :mod:`ezdxf.const`:

============================== ======= ===========
MText.dxf.line_spacing_style   Value   Description
============================== ======= ===========
MTEXT_AT_LEAST                 1       taller characters will override
MTEXT_EXACT                    2       taller characters will not override
============================== ======= ===========

.. method:: MText.get_text()

   Returns content of :class:`MText` as string.

.. method:: MText.set_text(text)

   Set *text* as :class:`MText` content.

.. method:: MText.set_location(insert, rotation=None, attachment_point=None)

   Set DXF attributes *insert*, *rotation* and *attachment_point*, *None* for *rotation* or *attachment_point*
   preserves the existing value.

.. method:: MText.get_rotation()

   Get text rotation in degrees, independent if it is defined by *rotation* or *text_direction*

.. method:: MText.set_rotation(angle)

   Set DXF attribute *rotation* to *angle* (in degrees) and deletes *text_direction* if present.

.. method:: MText.edit_data()

   Context manager for :class:`MText` content::

        with mtext.edit_data() as data:
            data += "append some text" + data.NEW_LINE

            # or replace whole text
            data.text = "Replacement for the existing text."

.. class:: MTextData

   Temporary object to manage the :class:`MText` content. Create context object by :meth:`MText.edit_data`.

.. seealso::

    :ref:`tut_mtext`

.. attribute:: MTextData.text

   Represents the :class:`MText` content, treat it like a normal string. (read/write)

.. method:: MTextData.__iadd__(text)

   Append *text* to the :attr:`MTextData.text` attribute.

.. method:: MTextData.append(text)

   Synonym for :meth:`MTextData.__iadd__`.

.. method:: MTextData.set_font(name, bold=False, italic=False, codepage=1252, pitch=0)

   Change actual font inline.

.. method:: MTextData.set_color(color_name)

   Set text color to ``red``, ``yellow``, ``green``, ``cyan``, ``blue``, ``magenta`` or ``white``.

**Convenient constants defined in MTextData:**

=================== ===========
Constant            Description
=================== ===========
UNDERLINE_START     start underline text (:code:`b += b.UNDERLINE_START`)
UNDERLINE_STOP      stop underline text (:code:`b += b.UNDERLINE_STOP`)
UNDERLINE           underline text (:code:`b += b.UNDERLINE % "Text"`)
OVERSTRIKE_START    start overstrike
OVERSTRIKE_STOP     stop overstrike
OVERSTRIKE          overstrike text
STRIKE_START        start strike trough
STRIKE_STOP         stop strike trough
STRIKE              strike trough text
GROUP_START         start of group
GROUP_END           end of group
GROUP               group text
NEW_LINE            start in new line (:code:`b += "Text" + b.NEW_LINE`)
NBSP                none breaking space (:code:`b += "Python" + b.NBSP + "3.4"`)
=================== ===========

Shape
=====

.. class:: Shape(GraphicEntity)

   Shapes (*dxftype* is ``SHAPE``) are objects that you use like blocks. Shapes are stored in external shape files
   (\*.SHX). You can specify the scale and rotation for each shape reference as you add it. You can not create shapes
   with *ezdxf*, you can just insert shape references.

   Create a :class:`Shape` reference in layouts and blocks by factory function :meth:`~Layout.add_shape`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
insert      R12     insertion point as (2D/3D Point)
name        R12     shape name
size        R12     shape size
rotation    R12     rotation angle in degrees; default=0
xscale      R12     relative X scale factor; default=1
oblique     R12     oblique angle; default=0
=========== ======= ===========

Ray
===

.. class:: Ray(GraphicEntity)

   Introduced in AutoCAD R13 (DXF version AC1012), *dxfversion* is ``RAY``.

   A :class:`Ray` starts at a point and continues to infinity. Create :class:`Ray` in layouts and blocks by factory
   function :meth:`~Layout.add_ray`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
start       R13     start point as (3D Point)
unit_vector R13     unit direction vector as (3D Point)
=========== ======= ===========

XLine
=====

.. class:: XLine(GraphicEntity)

   Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``XLINE``.

   A line that extents to infinity in both directions, used as construction line. Create :class:`XLine` in layouts and
   blocks by factory function :meth:`~Layout.add_xline`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
start       R13     location point of line as (3D Point)
unit_vector R13     unit direction vector as (3D Point)
=========== ======= ===========

Spline
======

.. class:: Spline(GraphicEntity)

   Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``SPLINE``.

   A spline curve, all coordinates have to be 3D coordinates even the spline is only a 2D planar curve.

   The spline curve is defined by a set of *fit points*, the spline curve passes all these fit points.
   The *control points* defines a polygon which influences the form of the curve, the first control point should be
   identical with the first fit point and the last control point should be identical the last fit point.

   Don't ask me about the meaning of *knot values* or *weights* and how they influence the spline curve, I don't know
   it, ask your math teacher or the internet. I think the *knot values* can be ignored, they will be calculated by the
   CAD program that processes the DXF file and the weights determines the influence 'strength' of the *control points*,
   in normal case the weights are all 1 and can be left off.

   To create a :class:`Spline` curve you just need a bunch of *fit points*, *control point*, *knot_values* and *weights*
   are optional (tested with AutoCAD 2010). If you add additional data, be sure that you know what you do.

   Create :class:`Spline` in layouts and blocks by factory function :meth:`~Layout.add_spline`.

   For more information about spline mathematics go to `Wikipedia`_.

.. _Wikipedia: https://en.wikipedia.org/wiki/Spline_%28mathematics%29

======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
degree                  R13     degree of the spline curve (int)
flags                   R13     bit coded option flags (see table below)
n_knots                 R13     count of knot values (int), automatically set by *ezdxf*, treat it as read only
n_fit_points            R13     count of fit points (int), automatically set by *ezdxf*, treat it as read only
n_control_points        R13     count of control points (int), automatically set by *ezdxf*, treat it as read only
knot_tolerance          R13     knot tolerance (float); default=1e-10
fit_tolerance           R13     fit tolerance (float); default=1e-10
control_point_tolerance R13     control point tolerance (float); default=1e-10
start_tangent           R13     start tangent vector as (3D Point)
end_tangent             R13     ene tangent vector as (3D Point)
======================= ======= ===========

Spline constants for *flags* defined in :mod:`ezdxf.const`:

=================== ======= ===========
Spline.dxf.flags    Value   Description
=================== ======= ===========
CLOSED_SPLINE       1       Spline is closed
PERIODIC_SPLINE     2
RATIONAL_SPLINE     4
PLANAR_SPLINE       8
LINEAR_SPLINE       16      planar bit is also set
=================== ======= ===========

.. seealso::

    :ref:`tut_spline`

.. attribute:: Spline.closed

   *True* if spline is closed else *False*.  A closed spline has a connection from the last control point
   to the first control point. (read/write)

.. method:: Spline.get_control_points()

   Returns the control points as list of (x, y, z) tuples.

.. method:: Spline.set_control_points(points)

   Set control points, *points* is a list (container or generator) of (x, y, z) tuples.

.. method:: Spline.get_fit_points()

   Returns the fit points as list of (x, y, z) tuples.

.. method:: Spline.set_fit_points(points)

   Set fit points, *points* is a list (container or generator) of (x, y, z) tuples.

.. method:: Spline.get_knot_values()

   Returns the knot values as list of *floats*.

.. method:: Spline.set_knot_values(values)

   Set knot values, *values* is a list (container or generator) of *floats*.

.. method:: Spline.get_weights()

   Returns the weight values as list of *floats*.

.. method:: Spline.set_weights(values)

   Set weights, *values* is a list (container or generator) of *floats*.

.. method:: Spline.edit_data()

   Context manager for all spline data, returns :class:`SplineData`.

Fit points, control points, knot values and weights can be manipulated as lists by using the general context manager
:meth:`Spline.edit_data`::

    with spline.edit_data() as spline_data:
        # spline_data contains standard python lists: add, change or delete items as you want
        # fit_points and control_points have to be (x, y, z)-tuples
        # knot_values and weights have to be numbers
        spline_data.fit_points.append((200, 300, 0))  # append a fit point
        # on exit the context manager calls all spline set methods automatically

.. class:: SplineData

.. attribute:: SplineData.fit_points

    Standard Python list of :class:`Spline` fit points as (x, y, z)-tuples. (read/write)

.. attribute:: SplineData.control_points

    Standard Python list of :class:`Spline` control points as (x, y, z)-tuples. (read/write)

.. attribute:: SplineData.knot_values

    Standard Python list of :class:`Spline` knot values as floats. (read/write)

.. attribute:: SplineData.weights

    Standard Python list of :class:`Spline` weights as floats. (read/write)

Body
====

.. class:: Body(GraphicEntity)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``BODY``.

    A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
    Create :class:`Body` objects in layouts and blocks by factory function :meth:`~Layout.add_body`.
    *ezdxf* will never interpret ACIS source code, don't ask me for this feature.

.. method:: Body.get_acis_data()

    Get the ACIS source code as a list of strings.

.. method:: Body.set_acis_data(test_lines)

    Set the ACIS source code as a list of strings **without** line endings.

.. method:: Body.edit_data()

    Context manager for  ACIS text lines, returns :class:`ModelerGeometryData`::

        with body_entity.edit_data as data:
            # data.text_lines is a standard Python list
            # remove, append and modify ACIS source code
            data.text_lines = ['line 1', 'line 2', 'line 3']  # replaces the whole ACIS content (with invalid data)


.. class:: ModelerGeometryData:

.. attribute:: ModelerGeometryData.text_lines

    ACIS date as list of strings. (read/write)

.. method:: ModelerGeometryData.__str__()

    Return concatenated :attr:`~ModelerGeometryData.text_lines` as one string, lines are separated by ``\n``.

Region
======

.. class:: Region(Body)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``REGION``.

    An object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
    Create :class:`Region` objects in layouts and blocks by factory function
    :meth:`~Layout.add_region`.

.. method:: Region.get_acis_data()

    Get the ACIS source code as a list of strings.

.. method:: Region.set_acis_data(test_lines)

    Set the ACIS source code as a list of strings **without** line endings.

.. method:: Region.edit_data()

    Context manager for  ACIS text lines, returns :class:`ModelerGeometryData`.

3DSolid
=======

.. class:: 3DSolid(Body)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``3DSOLID``.

    A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
    Create :class:`3DSolid` objects in layouts and blocks by factory function
    :meth:`~Layout.add_3dsolid`.

.. method:: 3DSolid.get_acis_data()

    Get the ACIS source code as a list of strings.

.. method:: 3DSolid.set_acis_data(test_lines)

    Set the ACIS source code as a list of strings **without** line endings.

.. method:: 3DSolid.edit_data()

    Context manager for  ACIS text lines, returns :class:`ModelerGeometryData`.

======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
history                  R13    handle to history object, see: :ref:`low_level_access_to_dxf_entities`
======================= ======= ===========

Image
=====

.. class:: Image(GraphicEntity)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``IMAGE``.

    Add a raster image to the DXF file, the file itself is not embedded into the DXF file, it is always a separated file.
    The IMAGE entity is like a block reference, you can use it multiple times to add the image on different locations
    with different scales and rotations. But therefore you need a also a IMAGEDEF entity, see :class:`ImageDef`.
    Create :class:`Image` in layouts and blocks by factory function :meth:`~Layout.add_image`. ezdxf creates only
    images in the XY-plan. You can place images in the 3D space too, but then you have to set the *u_pixel* and
    the *v_pixel* vectors by yourself.


======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
insert                  R13     Insertion point, lower left corner of the image
u_pixel                 R13     U-vector of a single pixel (points along the visual bottom of the image, starting at the insertion point) (x, y, z) tuple
v_pixel                 R13     V-vector of a single pixel (points along the visual left side of the image, starting at the insertion point) (x, y, z) tuple
image_size              R13     Image size in pixels
image_def               R13     Handle to the image definition entity, see :class:`ImageDef`
flags                   R13     see table below
clipping                R13     Clipping state: 0 = Off; 1 = On
brightness              R13     Brightness value (0-100; default = 50)
contrast                R13     Contrast value (0-100; default = 50)
fade                    R13     Fade value (0-100; default = 0)
clipping_boundary_type  R13     Clipping boundary type. 1 = Rectangular; 2 = Polygonal
count_boundary_points   R13     Number of clip boundary vertices
======================= ======= ===========


=========================== ======= ===========
Image.dxf.flags             Value   Description
=========================== ======= ===========
IMAGE_SHOW                  1       Show image
IMAGE_SHOW_WHEN_NOT_ALIGNED 2       Show image when not aligned with screen
IMAGE_USE_CLIPPING_BOUNDARY 4       Use clipping boundary
IMAGE_TRANSPARENCY_IS_ON    8       Transparency is on
=========================== ======= ===========


.. method:: Image.get_boundary()

    Returns a list of vertices as pixel coordinates, lower left corner is (0, 0) and upper right corner is (ImageSizeX,
    ImageSizeY), independent from the absolute location of the image in WCS.

.. method:: Image.reset_boundary()

    Reset boundary path to the default rectangle [(0, 0), (ImageSizeX, ImageSizeY)].

.. method:: Image.set_boundary(vertices)

    Set boundary path to vertices. 2 points describe a rectangle (lower left and upper right corner), more than 2 points
    is a polygon as clipping path. Sets clipping state to 1 and also sets the IMAGE_USE_CLIPPING_BOUNDARY flag.

.. method:: Image.get_image_def()

    returns the associated IMAGEDEF entity. see :class:`ImageDef`.


ImageDef
========

.. class:: ImageDef(GraphicEntity)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``IMAGEDEF``.

    :class:`ImageDef` defines an image, which can be placed by the :class:`Image` entity. Create :class:`ImageDef` by
    the :class:`Drawing` factory function :meth:`~Drawing.add_image_def`.


======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
filename                R13     Relative (to the DXF file) or absolute path to the image file as string
image_size              R13     Image size in pixel as (x, y) tuple
pixel_size              R13     Default size of one pixel in AutoCAD units (x, y) tuple
loaded                  R13     Default = 1
resolution_units        R13     Resolution units. 0 = No units; 2 = Centimeters; 5 = Inch, default is 0
======================= ======= ===========


Underlay
========

.. class:: Underlay(GraphicEntity)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``PDFUNDERLAY``, ``DWFUNDERLAY`` or ``DGNUNDERLAY``.

    Add an underlay file to the DXF file, the file itself is not embedded into the DXF file, it is always a separated file.
    The (PDF)UNDERLAY entity is like a block reference, you can use it multiple times to add the underlay on different
    locations with different scales and rotations. But therefore you need a also a (PDF)DEFINITION entity, see
    :class:`UnderlayDefinition`.
    Create :class:`Underlay` in layouts and blocks by factory function :meth:`~Layout.add_underlay`. The DXF standard
    supports three different fileformats: PDF, DWF (DWFx) and DGN. An Underlay can be clipped by a rectangle or a
    polygon path. The clipping coordinates are 2D OCS/ECS coordinates and in drawing units but without scaling.


======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
insert                  R13     Insertion point, lower left corner of the image
scale_x                 R13     scaling factor in x dircetion (float)
scale_y                 R13     scaling factor in y dircetion (float)
scale_z                 R13     scaling factor in z dircetion (float)
rotation                R13     ccw rotation in degrees around the extrusion vector (float)
extrusion               R13     extrusion vector (default=0, 0, 1)
underlay_def            R13     Handle to the underlay definition entity, see :class:`UnderlayDefinition`
flags                   R13     see table below
contrast                R13     Contrast value (20-100; default = 100)
fade                    R13     Fade value (0-80; default = 0)
======================= ======= ===========


============================== ======= ===========
Underlay.dxf.flags             Value   Description
============================== ======= ===========
UNDERLAY_CLIPPING              1       clipping is on/off
UNDERLAY_ON                    2       underlay is on/off
UNDERLAY_MONOCHROME            4       Monochrome
UNDERLAY_ADJUST_FOR_BACKGROUND 8       Adjust for background
============================== ======= ===========

.. attribute:: Underlay.clipping

   True or False (read/write)

.. attribute:: Underlay.on

   True or False (read/write)

.. attribute:: Underlay.monochrome

   True or False (read/write)

.. attribute:: Underlay.adjust_for_background

   True or False (read/write)

.. attribute:: Underlay.scale

   Scaling (x, y, z) tuple (read/write)


.. method:: Underlay.get_boundary()

    Returns a list of vertices as pixel coordinates, just two values represent the lower left and the upper right
    corners of the clipping rectangle, more vertices describe a clipping polygon.

.. method:: Underlay.reset_boundary()

    Removes the clipping path.

.. method:: Underlay.set_boundary(vertices)

    Set boundary path to vertices. 2 points describe a rectangle (lower left and upper right corner), more than 2 points
    is a polygon as clipping path. Sets clipping state to 1.

.. method:: Underlay.get_underlay_def()

    returns the associated (PDF)DEFINITION entity. see :class:`UnderlayDefinition`.


UnderlayDefinition
==================

.. class:: UnderlayDefinition(GraphicEntity)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``PDFDEFINITION``, ``DWFDEFINITION`` and
    ``DGNDEFINITION``.

    :class:`UnderlayDefinition` defines an underlay, which can be placed by the :class:`Underlay` entity. Create
    :class:`UnderlayDefinition` by the :class:`Drawing` factory function :meth:`~Drawing.add_underlay_def`.


======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
filename                R13     Relative (to the DXF file) or absolute path to the image file as string
name                    R13     defines what to display - pdf: page number; dgn: 'default'; dwf: ???
======================= ======= ===========


Mesh
====

.. class:: Mesh(GraphicEntity)

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``MESH``.

    3D mesh entity similar to the :class:`Polyface` entity. Create :class:`Mesh` in layouts and
    blocks by factory function :meth:`~Layout.add_mesh`.

.. method:: Mesh.edit_data()

    Context manager various mesh data, returns :class:`MeshData`.

.. seealso::

    :ref:`tut_image`

======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
version                 R13     int
blend_crease            R13     0 = off, 1 = on
subdivision_levels      R13     int >= 0, 0 = no smoothing
======================= ======= ===========

.. class:: MeshData

.. attribute:: MeshData.vertices

    A standard Python list with (x, y, z) tuples (read/write)

.. attribute:: MeshData.faces

    A standard Python list with (v1, v2, v3,...) tuples (read/write)

    Each face consist of a list of vertex indices (= index in :attr:`MeshData.vertices`).

.. attribute:: MeshData.edges

    A standard Python list with (v1, v2) tuples (read/write)

    Each edge consist of exact two vertex indices (= index in :attr:`MeshData.vertices`).

.. attribute:: MeshData.edge_crease_values

    A standard Python list of float values, one value for each edge. (read/write)

.. method:: MeshData.add_face(vertices)

    Add a face by coordinates, vertices is a list of (x, y, z) tuples.

.. method:: MeshData.add_edge(vertices)

    Add an edge by coordinates, vertices is a list of two (x, y, z) tuples.

.. method:: MeshData.optimize(precision=6)

    Tries to reduce vertex count by merging near vertices. *precision* defines the decimal places for coordinate
    be equal to merge two vertices.

.. seealso::

    :ref:`tut_mesh`

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

Hatch
=====

.. class:: Hatch

    Introduced in AutoCAD R13 (DXF version AC1012), *dxftype* is ``HATCH``.

    Fills an enclosed area defined by one or more boundary paths with a hatch pattern, solid fill, or gradient fill.
    Create :class:`Hatch` in layouts and blocks by factory function :meth:`~Layout.add_hatch`.

.. attribute:: Hatch.has_solid_fill

    *True* if hatch has a solid fill else *False*. (read only)

.. attribute:: Hatch.has_pattern_fill

    *True* if hatch has a pattern fill else *False*. (read only)

.. attribute:: Hatch.has_gradient_fill

    *True* if hatch has a gradient fill else *False*. A hatch with gradient fill has also a solid fill. (read only)

.. attribute:: Hatch.bgcolor

    Property background color as (r, g, b) tuple, rgb values in range 0..255 (read/write/del)

    usage::

        color = hatch.bgcolor  # get background color as (r, g, b) tuple
        hatch.bgcolor = (10, 20, 30)  # set background color
        del hatch.bgcolor  # delete background color

.. method:: Hatch.edit_boundary()

    Context manager to edit hatch boundary data, yields a :class:`BoundaryPathData` object.

.. method:: Hatch.edit_pattern()

    Context manager to edit hatch pattern data, yields a :class:`PatternData` object.

.. method:: Hatch.set_pattern_definition(lines)

    Setup hatch patten definition by a list of definition lines and a definition line is a 4-tuple [angle, base_point,
    offset, dash_length_items]

    - *angle*: line angle in degrees
    - *base-point*: (x, y) tuple
    - *offset*: (dx, dy) tuple, added to base point for next line and so on
    - *dash_length_items*: list of dash items (item > 0 is a line, item < 0 is a gap and item == 0.0 is a point)

    :param list lines: list of definition lines

.. method:: Hatch.set_solid_fill(color=7, style=1, rgb=None)

    Set :class:`Hatch` to solid fill mode and removes all gradient and pattern fill related data.

    :param int color: ACI (AutoCAD Color Index) in range 0 to 256, (0 = BYBLOCK; 256 = BYLAYER)
    :param int style: hatch style (0 = normal; 1 = outer; 2 = ignore)
    :param tuple rgb: true color value as (r, g, b) tuple - has higher priority than *color*. True color support requires at least DXF version AC1015.

.. method:: Hatch.set_gradient(color1=(0, 0, 0), color2=(255, 255, 255), rotation=0., centered=0., one_color=0, tint=0., name='LINEAR')

    Set :class:`Hatch` to gradient fill mode and removes all pattern fill related data. Gradient support requires at
    least DXF version AC1018. A gradient filled hatch is also a solid filled hatch.

    :param tuple color1: (r, g, b) tuple for first color, rgb values as int in range 0..255
    :param tuple color2: (r, g, b) tuple for second color, rgb values as int in range 0..255
    :param float rotation: rotation in degrees (360 deg = circle)
    :param int centered: determines whether the gradient is centered or not
    :param int one_color: 1 for gradient from *color1* to tinted *color1*
    :param float tint: determines the tinted target *color1* for a one color gradient. (valid range 0.0 to 1.0)
    :param str name: name of gradient type, default 'LINEAR'

    Valid gradient type names are:

    - ``LINEAR``
    - ``CYLINDER``
    - ``INVCYLINDER``
    - ``SPHERICAL``
    - ``INVSPHERICAL``
    - ``HEMISPHERICAL``
    - ``INVHEMISPHERICAL``
    - ``CURVED``
    - ``INVCURVED``

.. method:: Hatch.get_gradient()

    Get gradient data, returns a :class:`GradientData` object.

.. method:: Hatch.edit_gradient()

    Context manager to edit hatch gradient data, yields a :class:`GradientData` object.

.. method:: Hatch.set_pattern_fill(name, color=7, angle=0., scale=1., double=0, style=1, pattern_type=1, definition=None)

    Set :class:`Hatch` to pattern fill mode. Removes all gradient related data.

    :param int color: AutoCAD Color Index in range 0 to 256, (0 = BYBLOCK; 256 = BYLAYER)
    :param float angle: angle of pattern fill in degrees (360 deg = circle)
    :param float scale: pattern scaling
    :param int double: double flag
    :param int style: hatch style (0 = normal; 1 = outer; 2 = ignore)
    :param int pattern_type: pattern type (0 = user-defined; 1 = predefined; 2 = custom) ???
    :param list definition: list of definition lines and a definition line is a 4-tuple [angle, base_point,
        offset, dash_length_items], see :meth:`Hatch.set_pattern_definition`

.. method:: Hatch.get_seed_points()

    Get seed points as list of (x, y) points, I don't know why there can be more than one seed point.

.. method:: Hatch.set_seed_points(points)

    Set seed points, *points* is a list of (x, y) tuples, I don't know why there can be more than one seed point.

======================= ======= ===========
DXFAttr                 Version Description
======================= ======= ===========
pattern_name            R13     pattern name as string
solid_fill              R13     solid fill = 1, pattern fill = 0 (better use: :meth:`Hatch.set_solid_fill`, :meth:`Hatch.set_pattern_fill`)
associative             R13     1 for associative hatch else 0, associations not handled by ezdxf, you have to
                                set the handles to the associated DXF entities by yourself.
hatch_style             R13     0 = normal; 1 = outer; 2 = ignore (search for AutoCAD help for more information)
pattern_type            R13     0 = user; 1 = predefined; 2 = custom; (???)
pattern_angle           R13     pattern angle in degrees (360 deg = circle)
pattern_scale           R13     as float
pattern_double          R13     1 = double else 0
n_seed_points           R13     count of seed points (better user: :meth:`Hatch.get_seed_points`)
======================= ======= ===========

.. seealso::

    :ref:`tut_hatch`



Hatch Boundary Helper Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: BoundaryPathData

    Defines the borders of the hatch, a hatch can consist of more than one path.

.. attribute:: BoundaryPathData.paths

    List of all boundary paths. Contains :class:`PolylinePath` and :class:`EdgePath` objects. (read/write)

.. method:: BoundaryPathData.add_polyline_path(path_vertices, is_closed=1, flags=1)

    Create and add a new :class:`PolylinePath` object.

    :param list path_vertices: list of polyline vertices as (x, y) or (x, y, bulge) tuples.
    :param int is_closed: 1 for a closed polyline else 0
    :param int flags: external(1) or outermost(16) or default (0)

.. method:: BoundaryPathData.add_edge_path(flags=1)

    Create and add a new :class:`EdgePath` object.

    :param int flags: external(1) or outermost(16) or default (0)

.. method:: BoundaryPathData.clear()

    Remove all boundary paths.



.. class:: PolylinePath

    A polyline as hatch boundary path.

.. attribute:: PolylinePath.path_type_flags

    external(1) or outermost(16) or default (0) - polyline(2) will be set by *ezdxf*

    My interpretation of the :attr:`path_type_flags`, see also :ref:`tut_hatch`:

    * external - path is part of the hatch outer border
    * outermost - path is completely inside of one or more external paths
    * default - path is completely inside of one or more outermost paths

    If there are troubles with AutoCAD, maybe the hatch entity contains the pixel size tag (47) - delete it
    :code:`hatch.AcDbHatch.remove_tags([47])` and maybe the problem is solved. *ezdxf* does not use the pixel size tag,
    but it can occur in DXF files created by other applications.

.. attribute:: PolylinePath.is_closed

    *True* if polyline path is closed else *False*.

.. attribute:: PolylinePath.vertices

    List of path vertices as (x, y, bulge) tuples. (read/write)

.. attribute:: PolylinePath.source_boundary_objects

    List of handles of the associated DXF entities for associative hatches. There is no support for associative hatches
    by ezdxf you have to do it all by yourself. (read/write)

.. method:: PolylinePath.set_vertices(vertices, is_closed=1)

    Set new vertices for the polyline path, a vertex has to be a (x, y) or a (x, y, bulge) tuple.

.. method:: PolylinePath.clear()

    Removes all vertices and all links to associated DXF objects (:attr:`PolylinePath.source_boundary_objects`).



.. class:: EdgePath

    Boundary path build by edges. There are four different edge types: :class:`LineEdge`, :class:`ArcEdge`,
    :class:`EllipseEdge` of :class:`SplineEdge`. Make sure there are no gaps between edges. AutoCAD in this regard is
    very picky. *ezdxf* performs no checks on gaps between the edges.

.. attribute:: EdgePath.path_type_flags

    external(1) or outermost(16) or default (0), see :attr:`PolylinePath.path_type_flags`

.. attribute:: EdgePath.edges

    List of boundary edges of type :class:`LineEdge`, :class:`ArcEdge`, :class:`EllipseEdge` of :class:`SplineEdge`

.. attribute:: EdgePath.source_boundary_objects

    Required for associative hatches, list of handles to the associated DXF entities.

.. method:: EdgePath.clear()

    Delete all edges.

.. method:: EdgePath.add_line(start, end)

    Add a :class:`LineEdge` from *start* to *end*.

    :param tuple start: start point of line, (x, y) tuple
    :param tuple end: end point of line, (x, y) tuple

.. method:: EdgePath.add_arc(center, radius=1., start_angle=0., end_angle=360., is_counter_clockwise=0)

    Add an :class:`ArcEdge`.

    :param tuple center: center point of arc, (x, y) tuple
    :param float radius: radius of circle
    :param float start_angle: start angle of arc in degrees
    :param float end_angle: end angle of arc in degrees
    :param int is_counter_clockwise: 1 for yes 0 for no

.. method:: EdgePath.add_ellipse(center, major_axis_vector=(1., 0.), minor_axis_length=1., start_angle=0., end_angle=360., is_counter_clockwise=0)

    Add an :class:`EllipseEdge`.

    :param tuple center: center point of ellipse, (x, y) tuple
    :param tuple major_axis: vector of major axis as (x, y) tuple
    :param float ratio: ratio of minor axis to major axis as float
    :param float start_angle: start angle of ellipse in degrees
    :param float end_angle: end angle of ellipse in degrees
    :param int is_counter_clockwise: 1 for yes 0 for no

.. method:: EdgePath.add_spline(fit_points=None, control_points=None, knot_values=None, weights=None, degree=3, rational=0, periodic=0)

    Add a :class:`SplineEdge`.

    :param list fit_points: points through which the spline must go, at least 3 fit points are required. list of (x, y) tuples
    :param list control_points: affects the shape of the spline, mandatory amd AutoCAD crashes on invalid data. list of (x, y) tuples
    :param list knot_values: (knot vector) mandatory and AutoCAD crashes on invalid data. list of floats; *ezdxf* provides two
        tool functions to calculate valid knot values: :code:`ezdxf.tools.knot_values(n_control_points, degree)` and
        :code:`ezdxf.tools.knot_values_uniform(n_control_points, degree)`
    :param list weights: weight of control point, not mandatory, list of floats.
    :param int degree: degree of spline
    :param int rational: 1 for rational spline, 0 for none rational spline
    :param int periodic: 1 for periodic spline, 0 for none periodic spline

.. warning::

    Unlike for the spline entity AutoCAD does not calculate the necessary *knot_values* for the spline edge itself.
    On the contrary, if the *knot_values* in the spline edge are missing or invalid  AutoCAD **crashes**.

.. class:: LineEdge

    Straight boundary edge.

.. attribute:: LineEdge.start

    Start point as (x, y) tuple. (read/write)

.. attribute:: LineEdge.end

    End point as (x, y) tuple. (read/write)

.. class:: ArcEdge

    Arc as boundary edge.

.. attribute:: ArcEdge.center

     Center point of arc as (x, y) tuple. (read/write)

.. attribute:: ArcEdge.radius

     Arc radius as float. (read/write)

.. attribute:: ArcEdge.start_angle

     Arc start angle in degrees (360 deg = circle). (read/write)

.. attribute:: ArcEdge.end_angle

     Arc end angle in degrees (360 deg = circle). (read/write)

.. attribute:: ArcEdge.is_counter_clockwise

     1 for counter clockwise arc else 0. (read/write)

.. class:: EllipseEdge

    Elliptic arc as boundary edge.

.. attribute:: EllipseEdge.major_axis_vector

    Ellipse major axis vector as (x, y) tuple. (read/write)

.. attribute:: EllipseEdge.minor_axis_length

    Ellipse minor axis length as float. (read/write)

.. attribute:: EllipseEdge.radius

     Ellipse radius as float. (read/write)

.. attribute:: EllipseEdge.start_angle

     Ellipse start angle in degrees (360 deg = circle). (read/write)

.. attribute:: EllipseEdge.end_angle

     Ellipse end angle in degrees (360 deg = circle). (read/write)

.. attribute:: EllipseEdge.is_counter_clockwise

     1 for counter clockwise ellipse else 0. (read/write)

.. class:: SplineEdge

    Spline as boundary edge.

.. attribute:: SplineEdge.degree

     Spline degree as int. (read/write)

.. attribute:: SplineEdge.rational

     1 for rational spline else 0. (read/write)

.. attribute:: SplineEdge.periodic

     1 for periodic spline else 0. (read/write)

.. attribute:: SplineEdge.knot_values

     List of knot values as floats. (read/write)

.. attribute:: SplineEdge.control_points

     List of control points as (x, y) tuples. (read/write)

.. attribute:: SplineEdge.fit_points

     List of fit points as (x, y) tuples. (read/write)

.. attribute:: SplineEdge.weights

     List of weights (of control points) as floats. (read/write)

.. attribute:: SplineEdge.start_tangent

     Spline start tangent (vector)  as (x, y) tuple. (read/write)

.. attribute:: SplineEdge.end_tangent

     Spline end tangent (vector)  as (x, y) tuple. (read/write)

Hatch Pattern Definition Helper Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: PatternData

.. attribute:: PatternData.lines

    List of pattern definition lines (read/write). see :class:`PatternDefinitionLine`

.. method:: PatternData.new_line(angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None)

    Create a new pattern definition line, but does not add the line to the :attr:`PatternData.lines` attribute.

.. method:: PatternData.add_line(angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None)

    Create a new pattern definition line and add the line to the :attr:`PatternData.lines` attribute.

.. method:: PatternData.clear()

    Delete all pattern definition lines.

.. class:: PatternDefinitionLine

    Represents a pattern definition line, use factory function :meth:`PatternData.new_line` to create new pattern
    definition lines.

.. attribute:: PatternDefinitionLine.angle

    Line angle in degrees (circle = 360 deg). (read/write)

.. attribute:: PatternDefinitionLine.base_point

    Base point as (x, y) tuple. (read/write)

.. attribute:: PatternDefinitionLine..offset

    Offset as (x, y) tuple. (read/write)

.. attribute:: PatternDefinitionLine.dash_length_items

    List of dash length items (item > 0 is line, < 0 is gap, 0.0 = dot). (read/write)

Hatch Gradient Fill Helper Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: GradientData

.. attribute:: GradientData.color1

    First rgb color as (r, g, b) tuple, rgb values in range 0 to 255. (read/write)

.. attribute:: GradientData.color2

    Second rgb color as (r, g, b) tuple, rgb values in range 0 to 255. (read/write)

.. attribute:: GradientData.one_color

    If :attr:`~GradientData.one_color` is 1 - the hatch is filled with a smooth transition between
    :attr:`~GradientData.color1` and a specified :attr:`~GradientData.tint` of :attr:`~GradientData.color1`. (read/write)

.. attribute:: GradientData.rotation

    Gradient rotation in degrees (circle = 360 deg). (read/write)

.. attribute:: GradientData.centered

    Specifies a symmetrical gradient configuration. If this option is not selected, the gradient fill is shifted up and
    to the left, creating the illusion of a light source to the left of the object. (read/write)

.. attribute:: GradientData.tint

    Specifies the tint (color1 mixed with white) of a color to be used for a gradient fill of one color. (read/write)

.. seealso::

    :ref:`tut_hatch_pattern`
