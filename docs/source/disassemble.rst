Disassemble
===========

.. versionadded:: 0.16

.. module:: ezdxf.disassemble

This module provide tools for the recursive decomposition of DXF entities into
a flat stream of DXF entities and converting DXF entities into generic
:class:`~ezdxf.render.path.Path` and :class:`~ezdxf.render.mesh.MeshBuilder`
objects.

.. autofunction:: recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]

.. autofunction:: to_primitives(entities: Iterable[DXFEntity]) -> Iterable[AbstractPrimitive]

.. autofunction:: to_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]

.. autofunction:: make_primitive(entity: DXFEntity) -> AbstractPrimitive

.. class:: AbstractPrimitive

    Interface class for path/mesh primitives.

    .. autoattribute:: path

    .. autoattribute:: mesh

    .. automethod:: vertices() -> Iterable[Vec3]


