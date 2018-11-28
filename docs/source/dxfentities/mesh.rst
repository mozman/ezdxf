Mesh
====

.. class:: Mesh(GraphicEntity)

    Introduced in DXF version R13 (AC1012), dxftype is MESH.

    3D mesh entity similar to the :class:`Polyface` entity. Create :class:`Mesh` in layouts and
    blocks by factory function :meth:`~Layout.add_mesh`.

    All points in :ref:`WCS` as (x, y, z) tuples

    Since *ezdxf* v0.8.9 :class:`Mesh` stores vertices, edges, faces and creases as packed data (:code:`array.array()`).

DXF Attributes for Mesh
-----------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Mesh.dxf.version

.. attribute:: Mesh.dxf.blend_crease

0 = off, 1 = on

.. attribute:: Mesh.dxf.subdivision_levels

int >= 0, 0 = no smoothing

Mesh Methods
------------

.. method:: Mesh.edit_data()

Context manager various mesh data, returns :class:`MeshData`.

.. seealso::

    :ref:`tut_image`

MeshData
--------

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
