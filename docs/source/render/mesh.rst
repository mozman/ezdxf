.. module:: ezdxf.render

MeshBuilder
===========

A simple MESH builder. Stores a list of vertices, a list of edges where an edge is a list of indices into the
vertices list, and a faces list where each face is a list of indices into the vertices list.

The :meth:`MeshBuilder.render` method, renders the mesh into a DXF :class:`~ezdxf.entities.Mesh` entity.
The :class:`~ezdxf.entities.Mesh` entity supports ngons in AutoCAD, ngons are polygons with more than 4 vertices.

Creates only new meshes.

.. class:: MeshBuilder

    .. method:: add_face(vertices)

        Add a face as vertices list to the mesh. A face requires at least 3 vertices, each vertex is a (x, y, z) tuple.
        A face is stored as index list, which means, a face does not contain the vertex itself, but the indices of the
        vertices in the vertex list.

        list [index v1, index v2, index v3, ...].

        :param vertices: list of at least 3 vertices [(x1, y1, z1), (x2, y2, z2), (x3, y3, y3), ...]

    .. method:: add_edge(vertices)

        An edge consist of two vertices [v1, v2]. Each vertex is a (x, y, z) tuple and will be added to the mesh
        and the resulting vertex indices will be added to the mesh edges list. The stored edge is [index v1, index v2]

        :param vertices: list of 2 vertices : [(x1, y1, z1), (x2, y2, z2)]

    .. method:: add_vertices(vertices)

        Add new vertices to the mesh.

        e.g. adding 4 vertices to an empty mesh, returns the indices (0, 1, 2, 3), adding additional 4 vertices
        return s the indices (4, 5, 6, 7)

        :param vertices: list of vertices, vertex as (x, y, z) tuple
        :returns: a tuple of vertex indices.

    .. method:: add_mesh(vertices=None, faces=None, edges=None, mesh=None)

        Add another mesh to this mesh.

        :param vertices: list of vertices, a vertex is a (x, y, z)
        :param faces: list of faces, a face is a list of vertex indices
        :param edges: list of edges, an edge is a list of vertex indices
        :param mesh: another mesh entity, mesh overrides vertices, faces and edges

    .. method:: transform(matrix)

        Transform actual mesh into a new mesh by applying the transformation matrix to vertices.

        :param matrix: transformation matrix as :class:`~ezdxf.math.Matrix44`
        :returns: new :class:`ezdxf.render.MeshBuilder` object (same type as builder)

    .. method:: translate(x=0, y=0, z=0)

        Translate mesh inplace.

    .. method:: scale(sx=1, sy=1, sz=1)

        Scale mesh inplace.

    .. method:: render(layout, dxfattribs=None, matrix=None)

        Render mesh as :class:`~ezdxf.entities.Mesh` entity into `layout`.


        :param layout: ezdxf :class:`Layout` object
        :param dxfattribs: dict of DXF attributes e.g. {'layer': 'mesh', 'color': 7}
        :param matrix: transformation matrix as :class:`~ezdxf.math.Matrix44`

    .. method:: from_mesh(cls, other)

        Create new mesh from other mesh as class method.

MeshVertexMerger
================

Same functionality as :class:`MeshBuilder`, but creates meshes with unique vertices. Resulting meshes have no doublets,
but :class:`MeshVertexMerger` needs extra memory for bookkeeping.

Creates only new meshes.

.. class:: MeshVertexMerger

    Subclass of :class:`MeshBuilder`

    .. method:: add_vertices(vertices)

        Add new vertices only, if no vertex with identical x, y, z coordinates already exists, else the index of the
        existing vertex is returned as index of the new (not added) vertex.

        :param vertices: list of vertices, vertex as (x, y, z) tuple
        :returns: a tuple of vertex indices.
