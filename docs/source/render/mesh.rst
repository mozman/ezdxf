.. module:: ezdxf.render
    :noindex:

MeshBuilder
===========

The :class:`MeshBuilder` classes are helper tools to manage meshes buildup by
vertices and faces.
The vertices are stored in a vertices list as :class:`Vec3` instances.
The faces are stored as a sequence of vertex indices which is the location of
the vertex in the vertex list. A single :class:`MeshBuilder` class can contain
multiple separated meshes at the same time.

The method :meth:`MeshBuilder.render_mesh` renders the content as a single DXF
:class:`~ezdxf.entities.Mesh` entity, which supports ngons, ngons are polygons
with more than 4 vertices. This entity requires at least DXF R2000.

The method :meth:`MeshBuilder.render_polyface` renders the content as a single
DXF :class:`~ezdxf.entities.Polyface` entity, which supports only triangles and
quadrilaterals. This entity is supported by DXF R12.

The method :meth:`MeshBuilder.render_3dfaces` renders each face of the mesh as
a single  DXF :class:`~ezdxf.entities.Face3d` entity, which supports only
triangles and quadrilaterals. This entity is supported by DXF R12.

The :class:`MeshTransformer` class is often used as an interface object to
transfer mesh data between functions and moduls, like for the mesh exchange
add-on :mod:`~ezdxf.addons.meshex`.

The basic :class:`MeshBuilder` class does not support transformations.

.. class:: MeshBuilder

    .. attribute:: vertices

        List of vertices as :class:`~ezdxf.math.Vec3` or ``(x, y, z)`` tuple

    .. attribute:: faces

        List of faces as list of vertex indices,  where a vertex index is the
        index of the vertex in the :attr:`vertices` list. A face requires at
        least three vertices, :class:`~ezdxf.entities.Mesh` supports ngons,
        so the count of vertices is not limited.

    .. automethod:: add_face

    .. automethod:: add_mesh

    .. automethod:: add_vertices

    .. automethod:: bbox

    .. automethod:: copy

    .. automethod:: diagnose

    .. automethod:: face_normals

    .. automethod:: face_orientation_detector

    .. automethod:: faces_as_vertices

    .. automethod:: flip_normals

    .. automethod:: from_builder(other: MeshBuilder)

    .. automethod:: from_mesh

    .. automethod:: from_polyface

    .. automethod:: get_face_vertices

    .. automethod:: get_face_normal

    .. automethod:: merge_coplanar_faces

    .. automethod:: mesh_tessellation

    .. automethod:: normalize_faces

    .. automethod:: open_faces

    .. automethod:: optimize_vertices

    .. automethod:: render_3dfaces

    .. automethod:: render_mesh

    .. automethod:: render_normals

    .. automethod:: render_polyface

    .. automethod:: separate_meshes

    .. automethod:: subdivide

    .. automethod:: subdivide_ngons

    .. automethod:: tessellation

    .. automethod:: unify_face_normals

    .. automethod:: unify_face_normals_by_reference


MeshTransformer
===============

Same functionality as :class:`MeshBuilder` but supports inplace transformation.

.. class:: MeshTransformer

    Subclass of :class:`MeshBuilder`

    .. automethod:: transform

    .. automethod:: translate

    .. automethod:: scale

    .. automethod:: scale_uniform

    .. automethod:: rotate_x

    .. automethod:: rotate_y

    .. automethod:: rotate_z

    .. automethod:: rotate_axis

MeshVertexMerger
================

Same functionality as :class:`MeshBuilder`, but created meshes with unique
vertices and no doublets, but :class:`MeshVertexMerger` needs extra memory for
bookkeeping and also does not support transformations.
The location of the merged vertices is the location of the first vertex with the
same key.

This class is intended as intermediate object to create compact meshes and
convert them to :class:`MeshTransformer` objects to apply transformations:

.. code-block:: Python

    mesh = MeshVertexMerger()

    # create your mesh
    mesh.add_face(...)

    # convert mesh to MeshTransformer object
    return MeshTransformer.from_builder(mesh)

.. autoclass:: MeshVertexMerger

MeshAverageVertexMerger
=======================

This is an extended version of :class:`MeshVertexMerger`.
The location of the merged vertices is the average location of all vertices with
the same key, this needs extra memory and runtime in comparison to
:class:`MeshVertexMerger` and this class also does not support
transformations.

.. autoclass:: MeshAverageVertexMerger

.. autoclass:: ezdxf.render.mesh.EdgeStat

    .. attribute:: count

        how often the edge `(a, b)` is used in faces as `(a, b)` or `(b, a)`

    .. attribute:: balance

        count of edges `(a, b)` - count of edges `(b, a)` and should be 0 in
        "healthy" closed surfaces, if the balance is not 0, maybe doubled
        coincident faces exist or faces may have mixed clockwise and
        counter-clockwise vertex orders

MeshBuilder Helper Classes
==========================

.. class:: MeshDiagnose

    Diagnose tool which can be used to analyze and detect errors of
    :class:`MeshBuilder` objects like topology errors for closed surfaces.
    The object contains cached values, which do not get updated if the source
    mesh will be changed!

    .. note::

        There exist no tools in `ezdxf` to repair broken surfaces, but you can
        use the :mod:`ezdxf.addons.meshex` addon to exchange meshes with the
        open source tool `MeshLab <https://www.meshlab.net/>`_.

    Create an instance of this tool by the :meth:`MeshBuilder.diagnose` method.

    .. autoproperty:: bbox

    .. autoproperty:: edge_stats

    .. autoproperty:: euler_characteristic

    .. autoproperty:: face_normals

    .. autoproperty:: faces

    .. autoproperty:: is_closed_surface

    .. autoproperty:: is_edge_balance_broken

    .. autoproperty:: is_manifold

    .. autoproperty:: n_edges

    .. autoproperty:: n_faces

    .. autoproperty:: n_vertices

    .. autoproperty:: vertices

    .. automethod:: centroid

    .. automethod:: estimate_face_normals_direction

    .. automethod:: has_non_planar_faces

    .. automethod:: surface_area

    .. automethod:: total_edge_count

    .. automethod:: unique_edges

    .. automethod:: volume


.. autoclass:: FaceOrientationDetector

    .. attribute:: is_manifold

        ``True`` if all edges have an edge count < 3. A non-manifold mesh has
        edges with 3 or more connected faces.

    .. autoproperty:: all_reachable

    .. autoproperty:: count

    .. autoproperty:: backward_faces

    .. autoproperty:: forward_faces

    .. autoproperty:: has_uniform_face_normals

    .. autoproperty:: is_closed_surface

    .. autoproperty:: is_single_mesh

    .. automethod:: classify_faces

    .. automethod:: is_reference_face_pointing_outwards

