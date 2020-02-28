.. module:: ezdxf.render
    :noindex:

MeshBuilder
===========

The :class:`MeshBuilder` is a helper class  to create :class:`~ezdxf.entities.Mesh` entities.
Stores a list of vertices, a list of edges where an edge is a list of indices into the
vertices list, and a faces list where each face is a list of indices into the vertices list.

The :meth:`MeshBuilder.render` method, renders the mesh into a :class:`~ezdxf.entities.Mesh` entity.
The :class:`~ezdxf.entities.Mesh` entity supports ngons in AutoCAD, ngons are polygons with more than 4 vertices.

The basic :class:`MeshBuilder` class does not support transformations.

.. class:: MeshBuilder

    .. attribute:: vertices

        List of vertices as :class:`~ezdxf.math.Vector` or ``(x, y, z)`` tuple

    .. attribute:: edges

        List of edges as 2-tuple of vertex indices, where a vertex index is the index of the vertex in the
        :attr:`vertices` list.

    .. attribute:: faces

        List of faces as list of vertex indices,  where a vertex index is the index of the vertex in the
        :attr:`vertices` list. A face requires at least three vertices, :class:`~ezdxf.entities.Mesh` supports ngons,
        so the count of vertices is not limited.

    .. automethod:: copy()

    .. automethod:: faces_as_vertices() -> Iterable[List[Vector]]

    .. automethod:: edges_as_vertices() -> Iterable[Tuple[Vector, Vector]]

    .. automethod:: add_vertices

    .. automethod:: add_edge

    .. automethod:: add_face

    .. automethod:: add_mesh(vertices=None, faces=None, edges=None, mesh=None) -> None

    .. automethod:: has_none_planar_faces

    .. automethod:: render(layout: BaseLayout, dxfattribs: dict = None, matrix: Matrix44 = None)

    .. automethod:: render_polyface(layout: BaseLayout, dxfattribs: dict = None, matrix: Matrix44 = None)

    .. automethod:: render_normals(layout: BaseLayout, length: float = 1, relative=True, dxfattribs: dict = None)

    .. automethod:: from_mesh

    .. automethod:: from_polyface

    .. automethod:: from_builder(other: MeshBuilder)


MeshTransformer
===============

Same functionality as :class:`MeshBuilder` but supports inplace transformation.

.. class:: MeshTransformer

    Subclass of :class:`MeshBuilder`

    .. automethod:: subdivide(level: int = 1, quads=True, edges=False) -> MeshTransformer

    .. automethod:: transform(matrix: Matrix44)

    .. automethod:: translate

    .. automethod:: scale

    .. automethod:: scale_uniform

    .. automethod:: rotate_x

    .. automethod:: rotate_y

    .. automethod:: rotate_z

    .. automethod:: rotate_axis

    .. automethod:: transform_to_wcs

MeshVertexMerger
================

Same functionality as :class:`MeshBuilder`, but created meshes with unique vertices and no doublets,
but :class:`MeshVertexMerger` needs extra memory for bookkeeping and also does not support transformations.
Location of merged vertices is the location of the first vertex with the same key.

This class is intended as intermediate object to create a compact meshes and convert them to :class:`MeshTransformer`
objects to apply transformations to the mesh:

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
Location of merged vertices is the average location of all vertices with the same key, this needs extra
memory and runtime in comparision to :class:`MeshVertexMerger` and also does not support transformations.

.. autoclass:: MeshAverageVertexMerger

