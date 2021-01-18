Disassemble
===========

.. versionadded:: 0.16

.. module:: ezdxf.disassemble

This module provide tools for the recursive decomposition of DXF entities into
a flat stream of DXF entities and converting DXF entities into generic
:class:`~ezdxf.render.path.Path` and :class:`~ezdxf.render.mesh.MeshBuilder`
objects.

.. warning::

    Do not expect advanced vectorization capabilities: Text entities like TEXT,
    ATTRIB, ATTDEF and MTEXT get only a rough bounding box representation.
    VIEWPORT and IMAGE are represented by their clipping path. Unsupported
    entities: all ACIS based entities, WIPEOUT, XREF, UNDERLAY, ACAD_TABLE.
    Unsupported entities will be ignored.

.. autofunction:: recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]

.. autofunction:: to_primitives(entities: Iterable[DXFEntity]) -> Iterable[AbstractPrimitive]

.. autofunction:: to_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]

.. autofunction:: make_primitive(entity: DXFEntity) -> AbstractPrimitive

.. class:: AbstractPrimitive

    Interface class for path/mesh primitives.

    .. autoattribute:: path

    .. autoattribute:: mesh

    .. automethod:: vertices() -> Iterable[Vec3]


