Disassemble
===========

.. versionadded:: 0.16

.. module:: ezdxf.disassemble

This module provide tools for the recursive decomposition of nested block
reference structures into a flat stream of DXF entities and converting DXF
entities into geometric primitives of :class:`~ezdxf.path.Path` and
:class:`~ezdxf.render.mesh.MeshBuilder` objects encapsulated into
intermediate :class:`Primitive` classes.

.. versionchanged:: 0.17
    The :class:`~ezdxf.entities.Hatch` entity is no special case anymore and
    has regular support by the :func:`make_primitive` function.


.. warning::

    Do not expect advanced vectorization capabilities: Text entities like TEXT,
    ATTRIB, ATTDEF and MTEXT get only a rough border box representation.
    The :mod:`~ezdxf.addons.text2path` add-on can convert text into paths.
    VIEWPORT, IMAGE and WIPEOUT are represented by their clipping path.
    Unsupported entities: all ACIS based entities, XREF, UNDERLAY, ACAD_TABLE,
    RAY, XLINE. Unsupported entities will be ignored.

.. _Text Boundary Calculation:

Text Boundary Calculation
-------------------------

Text boundary calculations are based on monospaced (fixed-pitch, fixed-width,
non-proportional) font metrics, which do not provide a good accuracy for text
height calculation and much less accuracy for text width calculation. It is
possible to improve this results by using the font support from the
**optional**  `Matplotlib` package.

Install Matplotlib from command line::

    C:\> pip3 install matplotlib

The `Matplotlib` font support will improve the results for TEXT, ATTRIB and
ATTDEF. The MTEXT entity has many advanced features which would require a full
"Rich Text Format" rendering and that is far beyond the goals and capabilities
of this library, therefore the boundary box for MTEXT will **never** be as
accurate as in a dedicated CAD application.

Using the `Matplotlib` font support adds **runtime overhead**, therefore it is
possible to deactivate the `Matplotlib` font support by setting the
global option::

    options.use_matplotlib_font_support = False


Flatten Complex DXF Entities
----------------------------

.. autofunction:: recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]

Entity Deconstruction
---------------------

These functions disassemble DXF entities into simple geometric objects
like meshes, paths or vertices. The :class:`Primitive` is a simplified
intermediate class to use a common interface on various DXF entities.

.. autofunction:: make_primitive(entity: DXFEntity, max_flattening_distance=None) -> Primitive

.. autofunction:: to_primitives(entities: Iterable[DXFEntity], max_flattening_distance: float = None) -> Iterable[Primitive]

.. autofunction:: to_meshes(primitives: Iterable[Primitive]) -> Iterable[MeshBuilder]

.. autofunction:: to_paths(primitives: Iterable[Primitive]) -> Iterable[Path]

.. autofunction:: to_vertices(primitives: Iterable[Primitive]) -> Iterable[Vec3]

.. autofunction:: to_control_vertices(primitives: Iterable[Primitive]) -> Iterable[Vec3]

.. class:: Primitive

    Interface class for path/mesh primitives.

    .. attribute:: entity

    Reference to the source DXF entity of this primitive.

    .. attribute:: max_flattening_distance

    The `max_flattening_distance` attribute defines the max distance in drawing
    units between the approximation line and the original curve.
    Set the value by direct attribute access. (float) default = 0.01

    .. autoproperty:: path

    .. autoproperty:: mesh

    .. autoproperty:: is_empty

    .. automethod:: vertices() -> Iterable[Vec3]


