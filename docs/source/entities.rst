Common Base Class
=================

.. class:: GraphicEntity

   Common base class for all graphic entities.

.. attribute:: GraphicEntity.dxf

   (read only) The DXF attributes namespace, access DXF attributes by this attribute, like
   :code:`object.dxf.layer = 'MyLayer'`. Just the *dxf* attribute is read only, the DXF attributes are read- and
   writeable.

.. attribute:: GraphicEntity.dxftype

   (read only) Get the DXF type string, like ``LINE`` for the line entity.

.. attribute:: GraphicEntity.handle

   (read only) Get the entity handle. (feature for experts)

.. attribute:: GraphicEntity.layout

   (read only) Get the associated layout.

.. attribute:: GraphicEntity.drawing

   (read only) Get the associated drawing.

.. attribute:: GraphicEntity.dxffactory

   (read only) Get the associated DXF factory. (feature for experts)

.. method:: GraphicEntity.get_dxf_attrib(key, default=ValueError)

   Get DXF attribute `key`, returns `default` if key doesn't exist, or raise :class:`ValueError` if `default` is
   :class:`ValueError`::

        layer = entity.get_dxf_attrib("layer")
        # same as
        layer = entity.dxf.layer

.. method:: GraphicEntity.set_dxf_attrib(key, value)

   Set DXF attribute `key` to `value`::

       entity.set_dxf_attrib("layer", "MyLayer")
       # same as
       entity.dxf.layer = "MyLayer"

.. method:: GraphicEntity.del_dxf_attrib(key)

   Delete/remove DXF attribute `key`. Raises `AttributeError` if `key` isn't supported.

.. method:: GraphicEntity.dxf_attrib_exists(key)

   Returns `True` if DXF attrib `key` really exists else `False`. Raises `AttributeError` if `key` isn't supported

.. method:: GraphicEntity.supported_dxf_attrib(key)

   Returns `True` if DXF attrib `key` is supported by this entity else `False`. Does not grant that attrib
   `key` really exists.

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
layer       layer name as string; default=``0``
linetype    linetype as string, special names ``BYLAYER``, ``BYBLOCK``; default=``BYLAYER``
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
layer         layer name as string; default=``0``
linetype      linetype as string, special names ``BYLAYER``, ``BYBLOCK``; default=``BYLAYER``
color         dxf color index, 0 ... BYBLOCK, 256 ... BYLAYER; default= 256
ltscale       line type scale as float; defaults=1.0
invisible     1 for invisible, 0 for visible; default=0
paperspace    0 for entity resides in model-space, 1 for paper-space, this attribute is set automatically by adding an
              entity to a layout (feature for experts); default=0
extrusion     extrusion direction as 3D point; default=(0, 0, 1)
thickness     entity thickness as float; default=0
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

   :param tuple p1: first alignment point
   :param tuple p2: second alignment point, required for ``ALIGNED`` and ``FIT`` else ignored
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

.. class:: Polyline

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

.. method:: Polyline.get_mode()

   Returns a string: ``polyline2d``, ``polyline3d``, ``polymesh`` or ``polyface``

.. method:: Polyline.m_close()

   Close mesh in M direction (also closes polylines).

.. method:: Polyline.n_close()

   Close mesh in N direction.

.. method:: Polyline.close(m_close, n_close=False)

   Close mesh in M (if *mclose* is *True*) and/or N (if *nclose* is *True*) direction.

.. method:: Polyline.__len__()

   Returns the count of vertices. Used by builtin :func:`len`.

.. method:: Polyline.__iter__()

   Iterate over all vertices as :class:`Vertex`.

.. method:: Polyline.__getitem__(pos)

   Get vertex at position *pos*. Used as polyline[pos] operator. Very slow!!!. It is better to operate on a temporary
   list of vertices (:meth:`~Polyline.vertices`).

.. method:: Polyline.points()

   Generator of polyline points as tuple, not as :class:`Vertex`.

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

.. class:: LWPolyline

   Introduced in AutoCAD R13 (DXF version AC1012)

   A lightweight polyline is defined as a single graphic entity. The :class:`LWPolyline` differs from the old-style
   polyline, which is defined as a group of subentities. :class:`LWPolyline` display faster (in AutoCAD) and consume
   less disk space and RAM. Create :class:`LWPolyline` in layouts and blocks by factory function
   :meth:`~Layout.add_lwpolyline`.

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

   ``True`` if polyline is closed else ``False``.  A closed polyline has a connection from the last vertex
   to the first vertex. (read/write)

.. method:: LWPolyline.get_points()

   Returns all polyline points as list of tuples (x, y, [start_width, [end_width, [bulge]]]).

.. method:: LWPolyline.set_points(points)

   Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.

.. method:: LWPolyline.points()

   Context manager for polyline points. Returns a list of tuples (x, y, [start_width, [end_width, [bulge]]])

.. method:: LWPolyline.append_points(points)

   Append additional *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]]) tuples.

.. method:: LWPolyline.discard_points()

   Remove all points.

.. method:: LWPolyline.__getitem__(index)

   Get point at position *index* as (x, y, [start_width, [end_width, [bulge]]]) tuple. Actual implementation is very slow!

MText
=====

.. class:: MText

   Introduced in AutoCAD R13 (DXF version AC1012), extended in AutoCAD 2007 (DXF version AC1021)

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
style                 R13     text style (string); default=``STANDARD``
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

   Set DXF attributes *insert*, *rotation* and *attachment_point*, ``None`` for *rotation* or *attachment_point*
   preserves the existing value.

.. method:: MText.get_rotation()

   Get text rotation in degrees, independent if it is defined by *rotation* or *text_direction*

.. method:: MText.set_rotation(angle)

   Set DXF attribute *rotation* to *angle* (in degrees) and deletes *text_direction* if present.

.. method:: MText.buffer()

   Context manager for :class:`MText` content::

        with mtext.buffer() as b:
            b += "append some text" + b.NEW_LINE

            # or replace whole text
            b.text = "Replacement for the existing text."


.. class:: MTextBuffer

   Temporary object to manage the :class:`MText` content. Create context object by :meth:`MText.buffer`.

.. seealso::

    :ref:`tut_mtext`

.. attribute:: MTextBuffer.text

   Represents the :class:`MText` content, treat it like a normal string. (read/write)

.. method:: MTextBuffer.__iadd__(text)

   Append *text* to the :attr:`MTextBuffer.text` attribute.

.. method:: MTextBuffer.append(text)

   Synonym for :meth:`MTextBuffer.__iadd__`.

.. method:: MTextBuffer.set_font(name, bold=False, italic=False, codepage=1252, pitch=0)

   Change actual font inline.

.. method:: MTextBuffer.set_color(color_name)

   Set text color to ``red``, ``yellow``, ``green``, ``cyan``, ``blue``, ``magenta`` or ``white``.

**Convenient constants defined in MTextBuffer:**

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

.. class:: Shape

   Shapes are objects that you use like blocks. Shapes are stored in external shape files (\*.SHX). You can specify the
   scale and rotation for each shape reference as you add it. You can not create shapes with *ezdxf*, you can just insert
   shape references.

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

.. class:: Ray

   Introduced in AutoCAD R13 (DXF version AC1012)

   A :class:`Ray` starts at a point and continues to infinity.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
start       R13     start point as (3D Point)
unit_vector R13     unit direction vector as (3D Point)
=========== ======= ===========

XLine
=====

.. class:: XLine

   Introduced in AutoCAD R13 (DXF version AC1012)

   A line that extents to infinity in both directions, used as construction line.

=========== ======= ===========
DXFAttr     Version Description
=========== ======= ===========
start       R13     location point of line as (3D Point)
unit_vector R13     unit direction vector as (3D Point)
=========== ======= ===========

Spline
======

.. class:: Spline

   Introduced in AutoCAD R13 (DXF version AC1012)

   A spline curve, all coordinates have to be 3D coordinates even the spline is only a 2D planar curve.

   The spline curve is defined by a set of `fit points`, the spline curve passes all these fit points.
   The `control points` defines a polygon which influences the form of the curve, the first control point should be
   identical with the first fit point and the last control point should be identical the last fit point.

   Don't ask me about the meaning of `knot values` or `weights` and how they influence the spline curve, I don't know
   it, ask your math teacher or the internet. I think the `knot values` can be ignored, they will be calculated by the
   CAD program that processes the DXF file and the weights determines the influence 'strength' of the `control points`,
   in normal case the weights are all `1` and can be left off.

   To create a :class:`Spline` curve you just need a bunch of `fit points`, `control point`, `knot_values` and `weights`
   are optional (tested with AutoCAD 2010). If you add additional data, be sure that you know what you do.

   For more information about spline mathematic go to `Wikipedia`_.

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

   ``True`` if spline is closed else ``False``.  A closed spline has a connection from the last control point
   to the first control point. (read/write)

.. method:: Spline.get_control_points()

   Returns the control points as `list` of `3D points`.

.. method:: Spline.set_control_points(points)

   Set control points, `points` is a list (container or generator) of (x, y, z) tuples.

.. method:: Spline.control_points()

   Context manager for `control points`.

.. method:: Spline.get_fit_points()

   Returns the fit points as `list` of `3D points`.

.. method:: Spline.set_fit_points(points)

   Set fit points, `points` is a list (container or generator) of (x, y, z) tuples.

.. method:: Spline.fit_points()

   Context manager for `fit points`.

.. method:: Spline.get_knot_values()

   Returns the knot values as `list` of `floats`.

.. method:: Spline.set_knot_values(values)

   Set knot values, `values` is a list (container or generator) of `floats`.

.. method:: Spline.knot_values()

   Context manager for `knot values`.

.. method:: Spline.get_weights()

   Returns the weight values as `list` of `floats`.

.. method:: Spline.set_weights(values)

   Set weights, `values` is a list (container or generator) of `floats`.

.. method:: Spline.weights()

   Context manager for `weights`.

Fit points, control points, knot values and weights can be manipulated as lists by using context managers::

    with spline.fit_points() as fp:
        # fp is a standard python list: add, change or delete items as you want
        # items have to be (x, y, z)-tuples
        fp.append((200, 300, 0))  # append a fit point
        # on exit the context manager calls spline.set_fit_points(cp) automatically

