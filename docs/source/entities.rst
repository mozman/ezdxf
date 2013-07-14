Common Base Class
=================

.. class:: GraphicEntity

   Common base class for all graphic entities.

.. attribute:: dxf

   (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
   :code:`object.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
   writeable.

.. attribute:: dxftype

   (read only) Get the DXF type string, like ``LINE`` for the line entity.

.. attribute:: handle

   (read only) Get the entity handle. (feature for experts)

.. method:: get_dxf_attrib(key, default=ValueError)

   Get DXF attribute *key*, returns *default* if key doesn't exist, or raise :class:`ValueError` if *default* is
   :class:`ValueError`::

        layer = entity.get_dxf_attrib("layer")
        # same as
        layer = entity.dxf.layer

.. method:: set_dxf_attrib(key, value)

   Set DXF attribute *key* to *value*::

       entity.set_dxf_attrib("layer", "MyLayer")
       # same as
       entity.dxf.layer = "MyLayer"


.. _Common DXF attributes for DXF R12:

Common DXF attributes for DXF R12
=================================

Access DXF attributes by the *dxf* attribute of an entity, like :code:`object.dxf.layer = 'MyLayer'`.

=========== ===========
DXFAttr     Description
=========== ===========
handle      DXF handle (feature for experts)
layer       layer name as string, default is ``0``
linetype    linetype as string, special names ``BYLAYER``, ``BYBLOCK``,
            default is ``BYLAYER``
color       dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER, default is 256
paperspace  0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an
            entity to a layout (feature for experts)
extrusion   extrusion direction as 3D point
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
layer         layer name as string, default is ``0``
linetype      linetype as string, special names ``BYLAYER``, ``BYBLOCK``,
              default is ``BYLAYER``
color         dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER, default is 256
ltscale       line type scale as float, defaults to 1.0
invisible     1 for invisible, 0 for visible
paperspace    0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an
              entity to a layout (feature for experts)
extrusion     extrusion direction as 3D point
thickness     entity thickness as float
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
   No factory function for creating points until someone need it.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
point       R12     location of the point (2D/3D Point)
=========== ======= ===========

Circle
======

.. class:: Circle

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

.. class:: Arc

   An arc at location *center* and *radius* from *startangle* to *endangle*, *dxftype* is ``ARC``.
   Create arcs in layouts and blocks by factory function :meth:`~Layout.add_arc`.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
center      R12     center point of arc (2D/3D Point)
radius      R12     radius of arc (float)
startangle  R12     start angle in degrees (float)
endangle    R12     end angle in degrees (float)
=========== ======= ===========

Text
====

.. class:: Text

    A simple one line text, dxftype is ``TEXT``. Text height is in drawing units and defaults to 1, but it depends on
    the rendering software what you really get. Width is a scaling factor, but it is not defined what is scaled (I
    assume the text height), but it also depends on the rendering software what you get. This is one reason why DXF and
    also DWG are not reliable for exchanging exact styling, they are just reliable for exchanging exact geometry.
    Create text in layouts and blocks by factory function :meth:`~Layout.add_text`.

=================== ======= ===========
DXFAttr             Version Description
=================== ======= ===========
text                R12     the content text itself (str)
insert              R12     first alignment point of text (2D/3D Point), relevant for the adjustments ``LEFT``,
                            ``ALIGN`` and ``FIT``.
alignpoint          R12     second alignment point of text (2D/3D Point), if the justification is anything other than
                            ``LEFT``, the second alignment point specify also the first alignment
                            point: (or just the second alignment point for ``ALIGN`` and ``FIT``)
height              R12     text height in drawing units (float), default is 1
rotation            R12     text rotation in degrees (float), default is 0
oblique             R12     text oblique angle (float), default is 0
style               R12     text style name (str), default is ``STANDARD``
width               R12     width scale factor (float), default is 1
halign              R12     horizontal alignment flag (int), use :meth:`Text.set_pos` and :meth:`Text.get_align`
valign              R12     vertical alignment flag (int), use :meth:`Text.set_pos` and :meth:`Text.get_align`
textgenerationflag  R12     text generation flags (int)
                             - 2 = text is backward (mirrored in X)
                             - 4 = text is upside down (mirrored in Y)
=================== ======= ===========

.. method:: Text.set_pos(p1, p2=None, align=None)

   :param tuple p1: first alignment point
   :param tuple p2: second alignment point, required for ``ALIGNED`` and ``FIT`` else ignored
   :param str align: new alignment, *None* for preserve existing alignment.

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

.. class:: Polyline

    The *POLYLINE* entity is very complex, it's use to build 2D/3D polylines, 3D meshes and 3D polyfaces. For every type
    exists a different wrapper class but they all have the same dxftype of ``POLYLINE``. Detect the polyline type by
    :meth:`Polyline.get_mode`.

    Create 2D polylines in layouts and blocks by factory function :meth:`~Layout.add_polyline2D`.

    Create 3D polylines in layouts and blocks by factory function :meth:`~Layout.add_polyline3D`.

=================== ======= ===========
DXFAttr             Version Description
=================== ======= ===========
elevation           R12     elevation point, the X and Y values are always 0, and the Z value is the polyline's elevation (2D/3D Point)
flags               R12     polyline flags (int), see table below
defaultstartwidth   R12     default line start width (float), default is 0
defaultendwidth     R12     default line end width (float), default is 0
mcount              R12     polymesh M vertex count (int)
ncount              R12     polymesh N vertex count (int)
msmoothdensity      R12     smooth surface M density (int), default is 0
nsmoothdensity      R12     smooth surface N density (int), default is 0
smoothtype          R12     Curves and smooth surface type (int), default is 0, see table below
=================== ======= ===========


================================== ===== ====================================
polyline.dxf.flags                 Value Description
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

======================== =====  =============================
poyline.dxf.smoothtype   Value  Description
======================== =====  =============================
POLYMESH_NO_SMOOTH       0      no smooth surface fitted
POLYMESH_QUADRIC_BSPLINE 5      quadratic B-spline surface
POLYMESH_CUBIC_BSPLINE   6      cubic B-spline surface
POLYMESH_BEZIER_SURFACE  8      Bezier surface
======================== =====  =============================

.. method:: Polyline.get_mode()

   Returns a string: ``polyline2d``, ``polyline3d``, ``polymesh`` or ``polyface``

.. method:: Polyline.mclose()

   Close mesh in M direction (also closes polylines).

.. method:: Polyline.nclose()

   Close mesh in N direction.

.. method:: Polyline.close(mclose, nclose=False)

   Close mesh in M (if *mclose* is *True*) and/or N (if *nclose* is *True*) direction.

.. method:: Polyline.__len__()

   Returns the count of vertices. Used by builtin :func:`len`.

.. method:: Polyline.__iter__()

   Iterate over all vertices as :class:`Vertex`.

.. method:: Polyline.__getitem__(pos)

   Get vertex at position *pos*. Used as polyline[pos] operator. Very slow!!!. It is better to operate on a temporary
   list of vertices (:meth:`~Polyline.vertices`).

.. method:: Polyline.points()

   Returns the polyline points as list of tuple, not as :class:`Vertex`.

.. method:: Polyline.vertices()

   Returns the polyline vertices as list of :class:`Vertex`.

.. method:: Polyline.append_vertices(points, dxfattribs=None)

   Append points as :class:`Vertex` objects.

   :param iterable points: iterable polyline points, every point is a tuple.
   :param dict dxfattribs: dxf attributes for the :class:`Vertex`

.. method:: Polyline.insert_vertices(pos, points, dxfattribs=None)

   Insert points as :class:`Vertex` objects at position *pos*.

   :param int pos: insert position 0-indexed
   :param iterable points: iterable polyline points, every point is a tuple.
   :param dict dxfattribs: dxf attributes for the :class:`Vertex`

.. method:: Polyline.delete_vertices(pos, count=1)

   Delete *count* vertices at position *pos*.

   :param int pos: insert position 0-indexed
   :param int count: count of vertices to delete

Vertex
======

.. class:: Vertex

   A vertex represents a polyline/mesh point, dxftype is ``VERTEX``, you don't have to create vertices by yourself.

=================== ======= ===========
DXFAttr             Version Description
=================== ======= ===========
location            R12     vertex location (2D/3D Point)
startwidth          R12     line segment start width (float), default is 0
endwidth            R12     line segment end width (float), default is 0
bulge               R12     Bulge (float), default is 0. The bulge is the tangent of one fourth the included angle for an arc segment, made negative if the arc goes clockwise from the start point to the endpoint. A bulge of 0 indicates a straight segment, and a bulge of 1 is a semicircle.
flags               R12     vertex flags (int), see table below.
tangent             R12     curve fit tangent direction (float)
vtx1                R12     index of 1st vertex, if used as face (feature for experts)
vtx2                R12     index of 2nd vertex, if used as face (feature for experts)
vtx3                R12     index of 3rd vertex, if used as face (feature for experts)
vtx4                R12     index of 4th vertex, if used as face (feature for experts)
=================== ======= ===========

============================== ======= ===========
vertex.dxf.flags               Value   Description
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
   :meth:`~Polyline.get_mode` returns ``polymesh``.
   Create polymeshes in layouts and blocks by factory function :meth:`~Layout.add_polymesh`.

.. method:: Polymesh.get_mesh_vertex(pos)

   Get mesh vertex at position *pos* as :class:`Vertex`.

   :param tuple pos: (m, n) tuple

.. method:: Polymesh.set_mesh_vertex(pos, point, dxfattribs=None)

   Set mesh vertex at position *pos* to location *point* and update the dxf attributes of the :class:`Vertex`.

   :param tuple pos: (m, n) tuple
   :param tuple point: vertex coordinates as (x, y, z) tuple
   :param dict dxfattribs: dxf attributes for the :class:`Vertex`

Polyface
========

.. class:: Polyface(Polyline)

   A polyface consist of multiple location independent 3D areas called faces.
   The :class:`Polyface` is an extended :class:`Polyline` class, dxftype is also ``POLYLINE`` but
   :meth:`~Polyline.get_mode` returns ``polyface``.
   Create polyfaces in layouts and blocks by factory function :meth:`~Layout.add_polyface`.

.. method:: Polyface.append_face(face, dxfattribs=None)

   Append one *face*, *dxfattribs* is used for all vertices generated.

   :param tuple face: a tuple of 3 or 4 3D points, a 3D point is a (x, y, z)-tuple
   :param dict dxfattribs: dxf attributes for the :class:`Vertex`

.. method:: Polyface.append_faces(faces, dxfattribs=None)

   Append a list of *faces*, *dxfattribs* is used for all vertices generated.

   :param tuple faces: a list of faces, a face is a tuple of 3 or 4 3D points, a 3D point is a (x, y, z)-tuple
   :param dict dxfattribs: dxf attributes for the :class:`Vertex`

.. method:: Polyface.faces()

   Iterate over all faces, a face is a tuple of vertices; yielding (vtx1, vtx2, vtx3[, vtx4])-tuple

Solid
=====

.. class:: Solid

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

.. class:: Trace

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

.. class:: 3DFace

   (This is not a valid Python name, but it works, because all classes
   described here, do not exist in this simple form.)

   A 3DFace is real 3D solid filled triangle or quadrilateral, *dxftype* is ``3DFACE``. Access corner points by name
   (:code:`entity.dxf.vtx0 = (1.7, 2.3)`) or by index (:code:`entity[0] = (1.7, 2.3)`).
   Create 3DFaces in layouts and blocks by factory function :meth:`~Layout.add_3Dface`.

============== ======= ===========
DXFAttr        Version Description
============== ======= ===========
vtx0           R12     location of the 1. point (2D/3D Point)
vtx1           R12     location of the 2. point (2D/3D Point)
vtx2           R12     location of the 3. point (2D/3D Point)
vtx3           R12     location of the 4. point (2D/3D Point)
invisible_edge R12     invisible edge flag (int, default = 0)

                       - 1 = first edge is invisible
                       - 2 = second edge is invisible
                       - 4 = third edge is invisible
                       - 8 = fourth edge is invisible

                       Combine values by adding them, e.g. 1+4 = first and third edge is invisible.
============== ======= ===========
