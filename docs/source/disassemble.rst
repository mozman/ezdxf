Disassemble
===========

.. versionadded:: 0.16

.. module:: ezdxf.disassemble

This module provide tools for the recursive decomposition of DXF entities into
a flat stream of DXF entities and converting DXF entities into geometric
primitives of :class:`~ezdxf.path.Path` and :class:`~ezdxf.render.mesh.MeshBuilder`
objects encapsulated into intermediate :class:`AbstractPrimitive` classes.

The :class:`~ezdxf.entities.Hatch` entity is special because this entity can
not be reduced into as single geometric primitive. The :func:`make_primitive`
function returns an empty primitive, instead use the :func:`to_primitives`
function to convert a :class:`~ezdxf.entities.Hatch` entity into multiple
(boundary path) primitives::

    primitives = list(to_primitives([hatch_entity]))


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
height calculation and much less accuracy for text width calculation.

It is possible to improve this results by using font support from the
`Matplotlib` package, but this is an **optional** feature and has to be
activated explicit::

    from  ezdxf import options

    options.use_matplotlib_font_support = True

This is a global option for the current running Interpreter and it is active
until deactivated::

    options.use_matplotlib_font_support = False

.. warning::

    This feature requires a working Matplotlib installation else an ``ImportError``
    exception will be raised sooner or later. This feature also depends on the
    :mod:`~ezdxf.addons.drawing` add-on, which is installed by default. Using
    the Matplotlib font support adds **runtime overhead** at the first
    usage of any of the text related primitives.

.. seealso::

    Global option to set the font caching directory:
    :attr:`ezdxf.options.font_cache_directory`

Install Matplotlib from command line::

    pip3 install matplotlib

The `Matplotlib` font support will improve the results for TEXT, ATTRIB and
ATTDEF. The MTEXT entity has many advanced features which would require a full
"Rich Text Format" rendering and that is far beyond the goals and capabilities
of this library, therefore the boundary box for MTEXT will **never** be as
accurate as in a dedicated CAD application.

Flatten Complex DXF Entities
----------------------------

.. autofunction:: recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]

Entity Deconstruction
---------------------

These functions disassemble DXF entities into simple geometric objects
like meshes, paths or vertices. The :class:`AbstractPrimitive` is a simplified
intermediate class to use a common interface on various DXF entities.

.. autofunction:: make_primitive(entity: DXFEntity, max_flattening_distance=None) -> AbstractPrimitive

.. autofunction:: to_primitives(entities: Iterable[DXFEntity], max_flattening_distance: float = None) -> Iterable[AbstractPrimitive]

.. autofunction:: to_meshes(primitives: Iterable[AbstractPrimitive]) -> Iterable[MeshBuilder]

.. autofunction:: to_paths(primitives: Iterable[AbstractPrimitive]) -> Iterable[Path]

.. autofunction:: to_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]

.. autofunction:: to_control_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]

.. class:: AbstractPrimitive

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


