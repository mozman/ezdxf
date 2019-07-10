.. module:: ezdxf.render

MeshBuilder
===========

The :class:`MeshBuilder` is a helper class  to create :class:`~ezdxf.entities.Mesh` entities.
Stores a list of vertices, a list of edges where an edge is a list of indices into the
vertices list, and a faces list where each face is a list of indices into the vertices list.

The :meth:`MeshBuilder.render` method, renders the mesh into a :class:`~ezdxf.entities.Mesh` entity.
The :class:`~ezdxf.entities.Mesh` entity supports ngons in AutoCAD, ngons are polygons with more than 4 vertices.


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

    .. automethod:: add_vertices

    .. automethod:: add_edge

    .. automethod:: add_face

    .. automethod:: add_mesh(vertices=None, faces=None, edges=None, mesh=None) -> None

    .. automethod:: transform(matrix: Matrix44) -> MeshBuilder

    .. automethod:: translate

    .. automethod:: scale

    .. automethod:: render(layout: BaseLayout, dxfattribs: dict = None, matrix: Matrix44 = None)

    .. automethod:: from_mesh


MeshVertexMerger
================

Same functionality as :class:`MeshBuilder`, but creates meshes with unique vertices. Resulting meshes have no doublets,
but :class:`MeshVertexMerger` needs extra memory for bookkeeping.


.. class:: MeshVertexMerger(precision: int = 6)

    Subclass of :class:`MeshBuilder`

    Args:
        precision: floating point precision for vertex rounding

    .. automethod:: add_vertices
