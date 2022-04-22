.. module:: ezdxf.render
    :noindex:

MeshBuilder
===========

The :class:`MeshBuilder` is a helper class  to create :class:`~ezdxf.entities.Mesh`
entities. Stores a list of vertices and a faces list where each face is a list
of indices into the vertices list.

The :meth:`MeshBuilder.render` method, renders the mesh into a
:class:`~ezdxf.entities.Mesh` entity. The :class:`~ezdxf.entities.Mesh` entity
supports ngons in AutoCAD, ngons are polygons with more than 4 vertices.

The basic :class:`MeshBuilder` class does not support transformations.

.. class:: MeshBuilder

    .. attribute:: vertices

        List of vertices as :class:`~ezdxf.math.Vec3` or ``(x, y, z)`` tuple

    .. attribute:: faces

        List of faces as list of vertex indices,  where a vertex index is the
        index of the vertex in the :attr:`vertices` list. A face requires at
        least three vertices, :class:`~ezdxf.entities.Mesh` supports ngons,
        so the count of vertices is not limited.

    .. automethod:: copy

    .. automethod:: diagnose

    .. automethod:: faces_as_vertices() -> Iterator[List[Vec3]]

    .. automethod:: open_faces

    .. automethod:: add_vertices

    .. automethod:: add_face

    .. automethod:: add_mesh(vertices=None, faces=None, edges=None, mesh=None) -> None

    .. automethod:: has_none_planar_faces

    .. automethod:: render_mesh(layout: BaseLayout, dxfattribs: dict = None, matrix: Matrix44 = None, ucs: UCS = None)

    .. automethod:: render_polyface(layout: BaseLayout, dxfattribs: dict = None, matrix: Matrix44 = None, ucs: UCS = None)

    .. automethod:: render_3dfaces(layout: BaseLayout, dxfattribs: dict = None, matrix: Matrix44 = None, ucs: UCS = None)

    .. automethod:: render_normals(layout: BaseLayout, length: float = 1, relative=True, dxfattribs: dict = None)

    .. automethod:: from_mesh

    .. automethod:: from_polyface

    .. automethod:: from_builder(other: MeshBuilder)

    .. automethod:: flip_normals

    .. automethod:: subdivide(level: int = 1, quads=True) -> MeshTransformer

    .. automethod:: merge_coplanar_faces(passes: int = 1) -> MeshTransformer

    .. automethod:: optimize_vertices(precision: int = 6) -> MeshTransformer

    .. automethod:: subdivide_ngons(max_vertex_count: int = 4) -> Iterator[Sequence[Vec3]]

    .. automethod:: tessellation(max_vertex_count: int = 4) -> Iterator[Sequence[Vec3]]


.. autoclass:: ezdxf.render.mesh.EdgeStat

    .. attribute:: count

        how often the edge `(a, b)` is used in faces as `(a, b)` or `(b, a)`

    .. attribute:: balance

        count of edges `(a, b)` - count of edges `(b, a)` and should be 0 in
        "healthy" closed surfaces, if the balance is not 0, maybe doubled
        coincident faces exist or faces may have mixed clockwise and
        counter-clockwise vertex orders

.. class:: MeshDiagnose

    Diagnose tools for :class:`MeshBuilder` which can be used to detect
    topology errors for closed surfaces.

    .. note::

        There exist no tools in `ezdxf` to repair broken surfaces, but you can
        use the :mod:`ezdxf.addons.meshex` addon to exchange meshes with the
        open source tool `MeshLab <https://www.meshlab.net/>`_.

    Create an instance of this tool by the :meth:`MeshBuilder.diagnose` method.

    .. versionadded:: 0.18

    .. attribute:: vertices

        Sequence of mesh vertices as :class:`~ezdxf.math.Vec3` instances

    .. attribute:: faces

        Sequence of faces as ``Sequence[int]``

    .. autoproperty:: n_vertices

    .. autoproperty:: n_faces

    .. autoproperty:: n_edges

    .. autoproperty:: edge_stats

    .. autoproperty:: is_watertight

    .. autoproperty:: is_edge_balance_broken

    .. automethod:: total_edge_count

    .. automethod:: unique_edges

    .. automethod:: estimate_normals_direction


MeshTransformer
===============

Same functionality as :class:`MeshBuilder` but supports inplace transformation.

.. class:: MeshTransformer

    Subclass of :class:`MeshBuilder`

    .. automethod:: transform(matrix: Matrix44)

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
bookkeeping and also does not support transformations. Location of merged
vertices is the location of the first vertex with the same key.

This class is intended as intermediate object to create a compact meshes and
convert them to :class:`MeshTransformer` objects to apply transformations to the
mesh:

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
Location of merged vertices is the average location of all vertices with the
same key, this needs extra memory and runtime in comparison to
:class:`MeshVertexMerger` and this class also does not support
transformations.

.. autoclass:: MeshAverageVertexMerger

