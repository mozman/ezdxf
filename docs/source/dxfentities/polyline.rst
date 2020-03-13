Polyline
========

.. module:: ezdxf.entities
    :noindex:

The POLYLINE entity (`POLYLINE DXF Reference`_) is very complex, it's used to build 2D/3D polylines,
3D meshes and 3D polyfaces. For every type exists a different wrapper class but they all have the
same dxftype of ``'POLYLINE'``. Detect POLYLINE type by :meth:`Polyline.get_mode`.

POLYLINE types returned by :meth:`Polyline.get_mode`:

    - ``'AcDb2dPolyline'`` for 2D :class:`Polyline`
    - ``'AcDb3dPolyline'`` for 3D :class:`Polyline`
    - ``'AcDbPolygonMesh'`` for :class:`Polymesh`
    - ``'AcDbPolyFaceMesh'`` for :class:`Polyface`

For 2D entities all vertices in :ref:`OCS`.

For 3D entities all vertices in :ref:`WCS`.


======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'POLYLINE'``
2D factory function      :meth:`ezdxf.layouts.BaseLayout.add_polyline2d`
3D factory function      :meth:`ezdxf.layouts.BaseLayout.add_polyline3d`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. _POLYLINE DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-ABF6B778-BE20-4B49-9B58-A94E64CEFFF3

.. class:: Polyline

    :class:`Vertex` entities are stored in a standard Python list :attr:`Polyline.vertices`.
    Vertices can be retrieved and deleted by direct access to :attr:`Polyline.vertices` attribute:

    .. code-block:: python

        # delete first and second vertex
        del polyline.vertices[:2]

    .. attribute:: dxf.elevation

        Elevation point, the X and Y values are always ``0``, and the Z value is the polyline's elevation
        (3D Point in :ref:`OCS` when 2D, :ref:`WCS` when 3D).

    .. attribute:: dxf.flags

        Constants defined in :mod:`ezdxf.lldxf.const`:

        ================================== ===== ====================================
        :attr:`Polyline.dxf.flags`         Value Description
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

    .. attribute:: dxf.default_start_width

        Default line start width (float); default = ``0``

    .. attribute:: dxf.default_end_width

        Default line end width (float); default = ``0``

    .. attribute:: dxf.m_count

        Polymesh M vertex count (int); default = ``1``

    .. attribute:: dxf.n_count

        Polymesh N vertex count (int); default = ``1``

    .. attribute:: dxf.m_smooth_density

        Smooth surface M density (int); default = ``0``

    .. attribute:: dxf.n_smooth_density

        Smooth surface N density (int); default = ``0``

    .. attribute:: dxf.smooth_type

        Curves and smooth surface type (int); default=0, see table below

        Constants for :attr:`smooth_type` defined in :mod:`ezdxf.lldxf.const`:

        ================================ =====  =============================
        :attr:`Polyline.dxf.smooth_type` Value  Description
        ================================ =====  =============================
        POLYMESH_NO_SMOOTH               0      no smooth surface fitted
        POLYMESH_QUADRATIC_BSPLINE       5      quadratic B-spline surface
        POLYMESH_CUBIC_BSPLINE           6      cubic B-spline surface
        POLYMESH_BEZIER_SURFACE          8      Bezier surface
        ================================ =====  =============================

    .. attribute:: vertices

        List of :class:`Vertex` entities.

    .. autoattribute:: is_2d_polyline

    .. autoattribute:: is_3d_polyline

    .. autoattribute:: is_polygon_mesh

    .. autoattribute:: is_poly_face_mesh

    .. autoattribute:: is_closed

    .. autoattribute:: is_m_closed

    .. autoattribute:: is_n_closed

    .. automethod:: get_mode

    .. automethod:: m_close

    .. automethod:: n_close

    .. automethod:: close

    .. automethod:: __len__

    .. automethod:: __getitem__

    .. automethod:: points

    .. automethod:: append_vertex

    .. automethod:: append_vertices

    .. automethod:: append_formatted_vertices

    .. automethod:: insert_vertices

    .. automethod:: transform_to_wcs(ucs: UCS) -> Polyline

    .. automethod:: virtual_entities() -> Iterable[Union[Line, Arc]]

    .. automethod:: explode(target_layout: BaseLayout = None) -> EntityQuery

Vertex
======

A VERTEX (`VERTEX DXF Reference`_) represents a polyline/mesh vertex.

======================== ==========================================
Subclass of              :class:`ezdxf.entities.DXFGraphic`
DXF type                 ``'VERTEX'``
Factory function         :meth:`Polyline.append_vertex`
Factory function         :meth:`Polyline.extend`
Factory function         :meth:`Polyline.insert_vertices`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. _VERTEX DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-0741E831-599E-4CBF-91E1-8ADBCFD6556D

.. class:: Vertex

    .. attribute:: dxf.location

        Vertex location (2D/3D Point :ref:`OCS` when 2D, :ref:`WCS` when 3D)

    .. attribute:: dxf.start_width

        Line segment start width (float); default = ``0``

    .. attribute:: dxf.end_width

        Line segment end width (float); default = ``0``

    .. attribute:: dxf.bulge

        :ref:`bulge value` (float); default = ``0``.

        The bulge value is used to create arc shaped line segments.

    .. attribute:: dxf.flags

        Constants defined in :mod:`ezdxf.lldxf.const`:

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

    .. attribute:: dxf.tangent

        Curve fit tangent direction (float), used for 2D spline in DXF R12.

    .. attribute:: dxf.vtx1

        Index of 1st vertex, if used as face (feature for experts)

    .. attribute:: dxf.vtx2

        Index of 2nd vertex, if used as face (feature for experts)

    .. attribute:: dxf.vtx3

        Index of 3rd vertex, if used as face (feature for experts)

    .. attribute:: dxf.vtx4

        Index of 4th vertex, if used as face (feature for experts)

    .. attribute:: is_2d_polyline_vertex

    .. attribute:: is_3d_polyline_vertex

    .. attribute:: is_polygon_mesh_vertex

    .. attribute:: is_poly_face_mesh_vertex

    .. attribute:: is_face_record

    .. method:: transform_to_wcs(ucs: UCS) -> Vertex

        Transform VERTEX entity from local :class:`~ezdxf.math.UCS` coordinates to :ref:`WCS` coordinates.

        .. versionadded:: 0.11

Polymesh
========

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Polyline`
DXF type                 ``'POLYLINE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_polymesh`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. class:: Polymesh

    A polymesh is a grid of :attr:`m_count` x :attr:`n_count` vertices, every vertex has its own
    ``(x, y, z)`` location. The :class:`Polymesh` is an subclass of :class:`Polyline`, DXF type is also
    ``'POLYLINE'`` but :meth:`get_mode` returns ``'AcDbPolygonMesh'``.

    .. automethod:: get_mesh_vertex

    .. automethod:: set_mesh_vertex

    .. automethod:: get_mesh_vertex_cache


MeshVertexCache
---------------

.. class:: MeshVertexCache

    Cache mesh vertices in a dict, keys are 0-based ``(row, col)`` tuples.

    Set vertex location: :code:`cache[row, col] = (x, y, z)`

    Get vertex location: :code:`x, y, z = cache[row, col]`

    .. attribute:: vertices

        Dict of mesh vertices, keys are 0-based ``(row, col)`` tuples.

    .. automethod:: __getitem__

    .. automethod:: __setitem__

Polyface
========

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Polyline`
DXF type                 ``'POLYLINE'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_polyface`
Inherited DXF Attributes :ref:`Common graphical DXF attributes`
======================== ==========================================

.. seealso::

    :ref:`tut_polyface`

.. class:: Polyface

    A polyface consist of multiple location independent 3D areas called faces.
    The :class:`Polyface` is a subclass of :class:`Polyline`, DXF type is also ``'POLYLINE'`` but
    :meth:`~Polyline.get_mode` returns ``'AcDbPolyFaceMesh'``.

    .. automethod:: append_face

    .. automethod:: append_faces

    .. automethod:: faces() -> Iterable[List[Vertex]]

    .. automethod:: optimize


